import hashlib
import json
from collections import OrderedDict
from threading import Lock

from src.core.config import Settings
from src.core.logging import logger
from src.modules.chatbot.guardrail import RISK_LABELS, detect_risk_label, normalize_text
from src.modules.chatbot.llm import AnthropicLLM, GeminiLLM, LLMClient, MockLLM
from src.modules.chatbot.privacy import redact_sensitive_data
from src.modules.chatbot.retriever import Retriever
from src.modules.chatbot.schemas import ChatRequest, ChatResponse, LawEntry
from src.modules.chatbot.source_policy import is_usable_source
from src.modules.chatbot.templates import (
    DECISION_BOUNDARY_TEMPLATE,
    EXPERT_TEMPLATES,
    MONEY_TEMPLATE,
    NO_SOURCE_TEMPLATE,
    PENALTY_PRINCIPLE_EXPERT_NOTE,
    SAFE_FALLBACK_TEMPLATE,
    SERVICE_FEE_TEMPLATE,
    fixed_response,
)
from src.modules.chatbot.validator import parse_answer, validate_answer

_SAFE_CONTEXT_FLAGS = {
    "co_lao_dong",
    "co_no",
    "co_hoa_don",
    "co_tai_khoan_ngan_hang",
    "co_sao_ke",
    "co_thong_bao_thue",
    "co_bhxh",
    "co_bhxh_no",
    "co_hoa_don_ton",
    "co_sai_lech_so_lieu",
    "hoi_co_bi_phat",
}
_CLASSIFICATION_CACHE: OrderedDict[str, str] = OrderedDict()
_CLASSIFICATION_CACHE_LOCK = Lock()


class ChatbotPipeline:
    def __init__(
        self, settings: Settings, retriever: Retriever, llm: LLMClient | None = None
    ) -> None:
        self._settings = settings
        self._retriever = retriever
        self._llm = llm or self._create_llm(settings)

    async def answer(self, request: ChatRequest) -> ChatResponse:
        original_message = request.message
        message = redact_sensitive_data(request.message)
        step = redact_sensitive_data(request.current_step)
        context = {
            key: value for key, value in request.context_flags.items() if key in _SAFE_CONTEXT_FLAGS
        }

        context_risk = _context_risk_label(context)
        if context_risk:
            response = self._guardrail_response(context_risk)
            self._log_request(message, step, request, response, context_risk)
            return response

        risk_label = detect_risk_label(original_message)
        if risk_label is None:
            risk_label = detect_risk_label(message)
        penalty_principle_question = risk_label == "hoi_co_bi_phat"
        if penalty_principle_question:
            risk_label = None
        retrieved: list[LawEntry] = []
        approved: list[LawEntry] = []
        if risk_label is None and not penalty_principle_question:
            retrieved = self._retriever.retrieve(
                message, request.segment, self._settings.chatbot_top_k
            )
            approved = [entry for entry in retrieved if is_usable_source(entry)]
            if not approved:
                response = fixed_response(
                    NO_SOURCE_TEMPLATE,
                    reason=("no_relevant_source" if not retrieved else "no_usable_source"),
                )
                self._log_request(message, step, request, response, response.block_reason or "")
                return response
            predicted = self._cached_classification(message, request.segment.value, step)
            if predicted is None:
                try:
                    # Các dấu hiệu do regex phát hiện đã được giữ nguyên trước bước AI này.
                    predicted = (
                        await self._llm.classify_intent(message, request.segment, step)
                    ).strip()
                    self._cache_classification(message, request.segment.value, step, predicted)
                except Exception:
                    predicted = self._failsafe_label()
            if predicted == "khong":
                risk_label = None
            elif predicted in RISK_LABELS:
                risk_label = predicted
            else:
                risk_label = self._failsafe_label()

        if risk_label == "hoi_co_bi_phat":
            penalty_principle_question = True
            risk_label = None
        if penalty_principle_question:
            context["hoi_co_bi_phat"] = True

        if risk_label:
            response = self._guardrail_response(risk_label)
            if risk_label == "hoi_so_tien" and _is_service_fee_query(original_message):
                response = fixed_response(SERVICE_FEE_TEMPLATE, mode=2, reason=risk_label)
            self._log_request(message, step, request, response, risk_label)
            return response

        if penalty_principle_question:
            retrieved = self._retriever.retrieve(
                message, request.segment, self._settings.chatbot_top_k
            )
            approved = [entry for entry in retrieved if is_usable_source(entry)]
            if not approved:
                response = fixed_response(
                    NO_SOURCE_TEMPLATE,
                    reason=("no_relevant_source" if not retrieved else "no_usable_source"),
                )
                self._log_request(message, step, request, response, response.block_reason or "")
                return response

        raw_answer = ""
        parsed = None
        failure_reason = "invalid_llm_json"
        for _ in range(2):
            try:
                raw_answer = await self._llm.generate_answer(
                    message,
                    request.segment,
                    step,
                    context,
                    approved,
                )
            except Exception as error:
                failure_reason = getattr(error, "reason", "llm_request_failed")
                break
            parsed = parse_answer(raw_answer)
            if parsed is not None:
                break
        if parsed is None:
            fallback = (
                "Hệ thống đang bận, bạn thử lại sau hoặc hỏi chuyên gia."
                if failure_reason == "gemini_quota"
                else SAFE_FALLBACK_TEMPLATE
            )
            response = fixed_response(fallback, reason=failure_reason)
            self._log_request(message, step, request, response, failure_reason)
            return response

        rejection_reason = validate_answer(
            parsed,
            approved,
        )
        if rejection_reason:
            response = fixed_response(SAFE_FALLBACK_TEMPLATE, reason=rejection_reason)
            self._log_request(message, step, request, response, rejection_reason)
            return response

        cited_sources = [source for source in approved if source.id in parsed.citations]
        source_warnings = _source_warnings(cited_sources)
        oldest_fetch = min(source.fetched_at for source in cited_sources if source.fetched_at)
        data_note = (
            "Nội dung lấy tự động từ nguồn nhà nước công bố, cập nhật ngày "
            f"{oldest_fetch.date().isoformat()}; có thể chậm so với thay đổi mới nhất. "
            "Không thay thế tư vấn chuyên môn."
        )
        needs_expert = parsed.needs_expert or penalty_principle_question or bool(source_warnings)
        mode = 3 if needs_expert else 1
        response = ChatResponse(
            answer=parsed.answer
            + ("\n\n" + PENALTY_PRINCIPLE_EXPERT_NOTE if penalty_principle_question else "")
            + ("\n\n" + "\n".join(source_warnings) if source_warnings else ""),
            citations=parsed.citations,
            sources=cited_sources,
            needs_expert=needs_expert,
            mode=mode,
            block_reason=None,
            data_note=data_note,
        )
        self._log_request(message, step, request, response, "")
        return response

    def _failsafe_label(self) -> str:
        configured = self._settings.chatbot_failsafe
        return configured if configured in RISK_LABELS else "khong_chac_chan"

    @staticmethod
    def _guardrail_response(label: str) -> ChatResponse:
        if label == "hoi_so_tien":
            return fixed_response(MONEY_TEMPLATE, mode=2, reason=label)
        if label == "hoi_quyet_dinh_thay":
            return fixed_response(DECISION_BOUNDARY_TEMPLATE, reason=label)
        return fixed_response(
            EXPERT_TEMPLATES.get(label, EXPERT_TEMPLATES["khong_chac_chan"]), reason=label
        )

    @staticmethod
    def _create_llm(settings: Settings) -> LLMClient:
        if settings.chatbot_mock_mode or settings.chatbot_llm_provider == "mock":
            return MockLLM()
        if settings.chatbot_llm_provider == "anthropic":
            return AnthropicLLM(settings) if settings.anthropic_api_key else MockLLM()
        return GeminiLLM(settings) if settings.gemini_api_key else MockLLM()

    def _cached_classification(self, message: str, segment: str, step: str) -> str | None:
        if self._settings.chatbot_guardrail_cache_size == 0:
            return None
        key = _classification_cache_key(message, segment, step)
        with _CLASSIFICATION_CACHE_LOCK:
            value = _CLASSIFICATION_CACHE.get(key)
            if value is not None:
                _CLASSIFICATION_CACHE.move_to_end(key)
            return value

    def _cache_classification(self, message: str, segment: str, step: str, value: str) -> None:
        limit = self._settings.chatbot_guardrail_cache_size
        if limit == 0:
            return
        key = _classification_cache_key(message, segment, step)
        with _CLASSIFICATION_CACHE_LOCK:
            _CLASSIFICATION_CACHE[key] = value
            _CLASSIFICATION_CACHE.move_to_end(key)
            while len(_CLASSIFICATION_CACHE) > limit:
                _CLASSIFICATION_CACHE.popitem(last=False)

    @staticmethod
    def _log_request(
        message: str,
        step: str,
        request: ChatRequest,
        response: ChatResponse,
        reason: str,
    ) -> None:
        logger.info(
            "chatbot_request_completed",
            message_redacted=message[:200],
            current_step_redacted=step[:120],
            segment=request.segment.value,
            mode=response.mode,
            needs_expert=response.needs_expert,
            block_reason=reason,
        )


def _classification_cache_key(message: str, segment: str, step: str) -> str:
    payload = json.dumps([message, segment, step], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _context_risk_label(context: dict[str, bool]) -> str | None:
    if context.get("co_thong_bao_thue"):
        return "bi_co_quan_lien_he"
    if context.get("co_sai_lech_so_lieu"):
        return "sai_lech_so_lieu"
    if any(
        context.get(flag)
        for flag in ("co_no", "co_hoa_don_ton", "co_bhxh_no", "co_hoa_don", "co_bhxh")
    ):
        return "no_ton_dong"
    return None


def _is_service_fee_query(message: str) -> bool:
    normalized = normalize_text(message)
    return any(term in normalized for term in ("phi dich vu", "phi tu van", "phi chuyen gia"))


def _source_warnings(sources: list[LawEntry]) -> list[str]:
    warnings: list[str] = []
    if any(source.amended_by for source in sources):
        warnings.append(
            "Cảnh báo: nguồn có thông tin văn bản sửa đổi; cần đối chiếu nội dung sửa đổi mới nhất."
        )
    if any(source.effectiveness_status.value == "khong_ro" for source in sources):
        warnings.append("Cảnh báo: tình trạng hiệu lực của nguồn chưa rõ.")
    return warnings
