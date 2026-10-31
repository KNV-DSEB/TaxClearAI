import asyncio
import json
from functools import lru_cache
from typing import Protocol

from anthropic import AsyncAnthropic
from google import genai
from google.genai import types
from pydantic import BaseModel

from src.core.config import Settings
from src.modules.chatbot.privacy import redact_sensitive_data
from src.modules.chatbot.prompts import (
    GUARDRAIL_PROMPT,
    SITUATION_CLASSIFIER_PROMPT,
    SYSTEM_PROMPT,
)
from src.modules.chatbot.schemas import LawEntry, LLMAnswer, Segment
from src.modules.legal_survey.schemas import SituationSuggestion


class LLMClient(Protocol):
    async def classify_intent(self, message: str, segment: Segment, step: str) -> str: ...

    async def classify_situation(
        self, answers: dict[str, object], free_text: str | None, model: str
    ) -> str: ...

    async def generate_answer(
        self,
        message: str,
        segment: Segment,
        step: str,
        context: dict[str, bool],
        sources: list[LawEntry],
    ) -> str: ...


class GeminiUnavailableError(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class MockLLM:
    async def classify_intent(self, message: str, segment: Segment, step: str) -> str:
        del message, segment, step
        return "khong"

    async def classify_situation(
        self, answers: dict[str, object], free_text: str | None, model: str
    ) -> str:
        del free_text, model
        entity_type = answers.get("entity_type", "HKD")
        operating_status = answers.get("operating_status", "unknown")
        suggestion = "A1" if entity_type == "HKD" else "B1"
        if entity_type == "DN" and operating_status == "abandoned_after_operation":
            suggestion = "B2"
        evidence_key = "entity_type" if entity_type else "operating_status"
        evidence_value = answers.get(evidence_key, "unknown")
        return json.dumps(
            {
                "suggested_segment": suggestion,
                "confidence": 0.75,
                "reasons": [f"{evidence_key}={evidence_value}"],
                "risk_signals": [],
                "missing_info": [],
            }
        )

    async def generate_answer(
        self,
        message: str,
        segment: Segment,
        step: str,
        context: dict[str, bool],
        sources: list[LawEntry],
    ) -> str:
        del segment, step, context
        citation_ids = [sources[0].id] if sources else []
        answer = (
            "Đoạn tài liệu được cung cấp ghi nhận: " + sources[0].noi_dung + f" [{sources[0].id}]"
            if sources
            else "Chưa có căn cứ được cung cấp."
        )
        if message:
            answer += " Nội dung cần được đối chiếu với phạm vi nguồn nhà nước được cung cấp."
        return json.dumps(
            {"answer": answer, "citations": citation_ids, "needs_expert": not bool(citation_ids)},
            ensure_ascii=False,
        )


class GeminiLLM:
    def __init__(self, settings: Settings, client: genai.Client | None = None) -> None:
        self._settings = settings
        self._client = client or _get_gemini_client(settings.gemini_api_key)

    async def classify_intent(self, message: str, segment: Segment, step: str) -> str:
        prompt = f"Nhóm: {segment.value}. Bước: {step}. Tin nhắn: {message}"
        response = await self._generate(
            self._settings.model_guardrail,
            GUARDRAIL_PROMPT,
            prompt,
            max_output_tokens=32,
            temperature=0,
        )
        label = (response or "").strip()
        labels = {
            "bi_co_quan_lien_he",
            "sai_lech_so_lieu",
            "no_ton_dong",
            "hoi_so_tien",
            "hoi_co_bi_phat",
            "ne_thue",
            "chuyen_nhuong_phuc_tap",
            "hoi_quyet_dinh_thay",
            "ngoai_pham_vi",
            "khong_chac_chan",
            "khong",
        }
        return label if label in labels else "khong_chac_chan"

    async def classify_situation(
        self, answers: dict[str, object], free_text: str | None, model: str
    ) -> str:
        prompt = _situation_user_prompt(answers, free_text)
        response = await self._generate(
            model,
            SITUATION_CLASSIFIER_PROMPT,
            prompt,
            max_output_tokens=350,
            temperature=0,
            json_schema=SituationSuggestion,
        )
        if not response:
            raise GeminiUnavailableError("gemini_response_blocked_or_empty")
        return response

    async def generate_answer(
        self,
        message: str,
        segment: Segment,
        step: str,
        context: dict[str, bool],
        sources: list[LawEntry],
    ) -> str:
        source_text = "\n\n".join(
            f"[{source.id}] {source.van_ban}; {source.dieu_khoan}; "
            f"hiệu lực: {source.hieu_luc}; nội dung: {source.noi_dung}"
            for source in sources
        )
        answer_system_prompt = SYSTEM_PROMPT
        if context.get("hoi_co_bi_phat"):
            answer_system_prompt += (
                " Chỉ giải thích nguyên tắc chung về xử phạt hành chính, dẫn căn cứ từ nguồn; "
                "không nêu mức, số tiền hay phần trăm; kết thúc bằng gợi ý kết nối chuyên gia."
            )
        prompt = (
            f"Nhóm: {segment.value}. Bước hiện tại: {step}. Cờ bối cảnh: {context}. "
            f"Câu hỏi đã che định danh: {message}\n\nĐOẠN NGUỒN:\n{source_text}"
        )
        response = await self._generate(
            self._settings.model_answer,
            answer_system_prompt,
            prompt,
            max_output_tokens=700,
            temperature=0.2,
            json_schema=LLMAnswer,
        )
        if not response:
            raise GeminiUnavailableError("gemini_response_blocked_or_empty")
        return response

    async def _generate(
        self,
        model: str,
        system_prompt: str,
        prompt: str,
        *,
        max_output_tokens: int,
        temperature: float,
        json_schema: type[BaseModel] | None = None,
    ) -> str | None:
        thinking_cfg = None
        if not json_schema and "3." not in model:
            thinking_cfg = types.ThinkingConfig(thinking_budget=0)
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            response_mime_type="application/json" if json_schema else None,
            response_schema=json_schema,
            thinking_config=thinking_cfg,
        )
        # Redact once more at the provider boundary, including any retrieved context.
        system_prompt = redact_sensitive_data(system_prompt)
        prompt = redact_sensitive_data(prompt)
        for attempt in range(2):
            try:
                response = await self._client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
            except Exception as error:
                if _is_quota_error(error) and attempt == 0:
                    await asyncio.sleep(0.25)
                    continue
                reason = "gemini_quota" if _is_quota_error(error) else "gemini_request_failed"
                raise GeminiUnavailableError(reason) from error
            if _is_blocked_response(response):
                raise GeminiUnavailableError("gemini_response_blocked_or_empty")
            return response.text
        raise GeminiUnavailableError("gemini_quota")


class AnthropicLLM:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def classify_intent(self, message: str, segment: Segment, step: str) -> str:
        prompt = f"Nhóm: {segment.value}. Bước: {step}. Tin nhắn: {message}"
        return await self._complete(self._settings.model_guardrail, GUARDRAIL_PROMPT, prompt, 32)

    async def classify_situation(
        self, answers: dict[str, object], free_text: str | None, model: str
    ) -> str:
        return await self._complete(
            model,
            SITUATION_CLASSIFIER_PROMPT,
            _situation_user_prompt(answers, free_text),
            350,
        )

    async def generate_answer(
        self,
        message: str,
        segment: Segment,
        step: str,
        context: dict[str, bool],
        sources: list[LawEntry],
    ) -> str:
        source_text = "\n\n".join(
            f"[{source.id}] {source.van_ban}; {source.dieu_khoan}; "
            f"hiệu lực: {source.hieu_luc}; nội dung: {source.noi_dung}"
            for source in sources
        )
        user_prompt = (
            f"Nhóm: {segment.value}. Bước hiện tại: {step}. Cờ bối cảnh: {context}. "
            f"Câu hỏi đã che định danh: {message}\n\nĐOẠN NGUỒN:\n{source_text}"
        )
        answer_system_prompt = SYSTEM_PROMPT
        if context.get("hoi_co_bi_phat"):
            answer_system_prompt += (
                " Chỉ giải thích nguyên tắc chung về xử phạt hành chính, dẫn căn cứ từ nguồn; "
                "không nêu mức, số tiền hay phần trăm; kết thúc bằng gợi ý kết nối chuyên gia."
            )
        return await self._complete(
            self._settings.model_answer, answer_system_prompt, user_prompt, 700
        )

    async def _complete(self, model: str, system: str, prompt: str, max_tokens: int) -> str:
        system = redact_sensitive_data(system)
        prompt = redact_sensitive_data(prompt)
        async with AsyncAnthropic(
            api_key=self._settings.anthropic_api_key,
            timeout=20.0,
            max_retries=1,
        ) as client:
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
        return "\n".join(block.text for block in response.content if block.type == "text")


def _is_quota_error(error: Exception) -> bool:
    status = getattr(error, "status_code", None) or getattr(error, "code", None)
    message = str(error).lower()
    return status == 429 or any(term in message for term in ("429", "quota", "rate limit"))


def _situation_user_prompt(answers: dict[str, object], free_text: str | None) -> str:
    payload = json.dumps(
        {"answers": answers, "free_text": free_text}, ensure_ascii=False, separators=(",", ":")
    )
    return "Dữ liệu khảo sát (JSON):\n" + redact_sensitive_data(payload)


@lru_cache(maxsize=8)
def _get_gemini_client(api_key: str | None) -> genai.Client:
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )


def _is_blocked_response(response: object) -> bool:
    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        return True
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return False
    reason = str(getattr(candidates[0], "finish_reason", "")).upper()
    return "SAFETY" in reason or "BLOCKED" in reason
