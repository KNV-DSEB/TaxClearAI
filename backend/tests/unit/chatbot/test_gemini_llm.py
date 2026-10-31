import hashlib
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast

import pytest

from src.core.config import Settings
from src.modules.chatbot.llm import GeminiLLM, MockLLM
from src.modules.chatbot.pipeline import ChatbotPipeline
from src.modules.chatbot.schemas import ChatRequest, LawEntry, Segment


class FakeGeminiClient:
    def __init__(self, replies: list[Any]) -> None:
        self.replies = replies
        self.calls: list[dict[str, Any]] = []
        self.aio = SimpleNamespace(models=SimpleNamespace(generate_content=self.generate_content))

    async def generate_content(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        result = self.replies.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class ApprovedRetriever:
    def retrieve(self, query: str, segment: Segment, top_k: int) -> list[LawEntry]:
        del query, segment, top_k
        return [
            LawEntry(
                id="L900",
                document_number="TEST/2026",
                article="Điều 1",
                clause="Khoản 1",
                van_ban="Nguồn kiểm thử",
                dieu_khoan="Điều kiểm thử",
                noi_dung="Nội dung nguồn kiểm thử.",
                source_url="https://congbao.chinhphu.vn/law",
                source_domain="congbao.chinhphu.vn",
                fetched_at=datetime.now(UTC),
                content_sha256=hashlib.sha256("Nội dung nguồn kiểm thử.".encode()).hexdigest(),
                effectiveness_status="con_hieu_luc",
                ap_dung_cho=[Segment.A1],
            )
        ]


class CountingLLM(MockLLM):
    def __init__(self) -> None:
        self.classification_calls = 0

    async def classify_intent(self, message: str, segment: Segment, step: str) -> str:
        self.classification_calls += 1
        return await super().classify_intent(message, segment, step)


def request(message: str = "Giải thích thủ tục này") -> ChatRequest:
    return ChatRequest.model_validate({"tin_nhan": message, "nhom": "A1", "buoc": "Chuẩn bị hồ sơ"})


def make_settings(**overrides: Any) -> Settings:
    return Settings(_env_file=None, chatbot_guardrail_cache_size=0, **overrides)


def response(text: str | None, finish_reason: str = "STOP") -> Any:
    return SimpleNamespace(
        text=text,
        candidates=[SimpleNamespace(finish_reason=finish_reason)],
    )


def valid_answer() -> str:
    return json.dumps(
        {"answer": "Theo nguồn kiểm thử [L900].", "citations": ["L900"], "needs_expert": False}
    )


@pytest.mark.asyncio
async def test_gemini_uses_json_schema_and_pipeline_parses_valid_answer() -> None:
    fake = FakeGeminiClient([response("khong"), response(valid_answer())])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))
    pipeline = ChatbotPipeline(make_settings(), ApprovedRetriever(), llm)

    result = await pipeline.answer(request())

    assert result.mode == 1
    assert result.citations == ["L900"]
    assert fake.calls[0]["config"].temperature == 0
    assert fake.calls[0]["config"].max_output_tokens <= 32
    assert fake.calls[0]["config"].thinking_config.thinking_budget == 0
    assert fake.calls[1]["config"].response_mime_type == "application/json"
    assert fake.calls[1]["config"].response_schema.__name__ == "LLMAnswer"


@pytest.mark.asyncio
async def test_prompt_inputs_are_redacted_before_guardrail_and_answer_calls() -> None:
    fake = FakeGeminiClient([response("khong"), response(valid_answer())])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))
    pipeline = ChatbotPipeline(make_settings(), ApprovedRetriever(), llm)

    await pipeline.answer(
        request(
            "Tôi tên là Nguyễn Văn An, MST 0123456789, email a@example.vn, số 0912345678; "
            "toi ten la vuong thi a; Anh Hùng"
        )
    )

    prompt_text = " ".join(str(call["contents"]) for call in fake.calls)
    for sensitive in (
        "Nguyễn Văn An",
        "0123456789",
        "a@example.vn",
        "0912345678",
        "vuong thi a",
        "Hùng",
    ):
        assert sensitive not in prompt_text
    assert len(fake.calls) == 2


@pytest.mark.asyncio
async def test_gemini_redacts_survey_free_text_at_provider_boundary() -> None:
    suggestion = json.dumps(
        {
            "suggested_segment": "A1",
            "confidence": 0.8,
            "reasons": ["entity_type=HKD"],
            "risk_signals": [],
            "missing_info": [],
        }
    )
    fake = FakeGeminiClient([response(suggestion)])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))

    await llm.classify_situation(
        {"entity_type": "HKD"},
        "Tôi tên là Nguyễn Văn An, MST 0123456789, a@example.vn, 0912345678",
        "survey-model",
    )

    prompt_text = str(fake.calls[0]["contents"])
    for sensitive in ("Nguyễn Văn An", "0123456789", "a@example.vn", "0912345678"):
        assert sensitive not in prompt_text


@pytest.mark.asyncio
async def test_malformed_json_falls_back_without_exposing_generated_text() -> None:
    fake = FakeGeminiClient([response("khong"), response("not-json"), response("still-not-json")])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))
    pipeline = ChatbotPipeline(make_settings(), ApprovedRetriever(), llm)

    result = await pipeline.answer(request())

    assert result.mode == 3
    assert result.block_reason == "invalid_llm_json"
    assert "not-json" not in result.answer
    assert len(fake.calls) == 3


@pytest.mark.asyncio
async def test_empty_or_safety_blocked_response_uses_failsafe() -> None:
    fake = FakeGeminiClient([response("khong"), response(None, "SAFETY")])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))
    pipeline = ChatbotPipeline(make_settings(), ApprovedRetriever(), llm)

    result = await pipeline.answer(request())

    assert result.mode == 3
    assert result.block_reason == "gemini_response_blocked_or_empty"
    assert len(fake.calls) == 2


@pytest.mark.asyncio
async def test_quota_retries_once_then_uses_safe_fallback() -> None:
    quota_error = RuntimeError("429 quota exceeded")
    quota_error.status_code = 429  # type: ignore[attr-defined]
    fake = FakeGeminiClient([response("khong"), quota_error, quota_error])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))
    pipeline = ChatbotPipeline(make_settings(), ApprovedRetriever(), llm)

    result = await pipeline.answer(request())

    assert result.mode == 3
    assert result.block_reason == "gemini_quota"
    assert result.answer == "Hệ thống đang bận, bạn thử lại sau hoặc hỏi chuyên gia."
    assert len(fake.calls) == 3


@pytest.mark.asyncio
async def test_unknown_guardrail_label_is_converted_to_expert_failsafe() -> None:
    fake = FakeGeminiClient([response("label-la")])
    llm = GeminiLLM(make_settings(gemini_api_key="test"), cast(Any, fake))

    label = await llm.classify_intent("Tin nhắn", Segment.A1, "Bước")

    assert label == "khong_chac_chan"


def test_missing_gemini_key_selects_mock_client() -> None:
    settings = Settings(
        _env_file=None,
        chatbot_mock_mode=False,
        chatbot_llm_provider="gemini",
        gemini_api_key=None,
    )

    assert isinstance(ChatbotPipeline._create_llm(settings), MockLLM)


@pytest.mark.asyncio
async def test_guardrail_classification_uses_configured_lru_cache() -> None:
    llm = CountingLLM()
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_guardrail_cache_size=8), ApprovedRetriever(), llm
    )

    await pipeline.answer(request("Câu hỏi dùng để kiểm tra bộ nhớ đệm"))
    await pipeline.answer(request("Câu hỏi dùng để kiểm tra bộ nhớ đệm"))

    assert llm.classification_calls == 1
