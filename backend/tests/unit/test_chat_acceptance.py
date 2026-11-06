import json
from uuid import uuid4

import httpx
import pytest

from src.core.errors import ApplicationError
from src.modules.chat.provider import MAX_ATTEMPTS, GeminiProvider
from src.modules.chat.schemas import GeneratedAnswer
from src.modules.chat.service import ChatService


class FakeProvider:
    def __init__(self, reply=None):
        self.calls = 0
        self.reply = reply or GeneratedAnswer(
            reply="Bạn chọn Đã có, Còn thiếu hoặc Cần xác minh cho từng mục.",
            source_ids=["product-guide"],
        )

    async def generate(self, message, sources):
        self.calls += 1
        return self.reply


@pytest.mark.parametrize(
    "message",
    [
        "Email của tôi là khach@example.com",
        "CCCD 012345678901",
        "Số điện thoại 0901 234 567",
        "Mã số thuế: 0123456789",
    ],
)
async def test_sensitive_input_never_reaches_gemini(message):
    provider = FakeProvider()
    result = await ChatService(provider).answer(uuid4(), message)
    assert result.disposition == "blocked_input"
    assert provider.calls == 0
    assert not result.provider_used


async def test_request_for_tax_amount_is_referred_without_fabricated_numbers():
    provider = FakeProvider()
    result = await ChatService(provider).answer(uuid4(), "Tôi phải nộp bao nhiêu tiền thuế?")
    assert result.disposition == "expert_review"
    assert not result.citations
    assert provider.calls == 0


async def test_unapproved_legal_sources_are_not_used_as_authority():
    provider = FakeProvider()
    result = await ChatService(provider).answer(
        uuid4(), "Thủ tục giải thể gồm những bước pháp lý nào?"
    )
    assert result.disposition == "insufficient_sources"
    assert provider.calls == 0


async def test_product_guide_answer_uses_provider_and_identifies_source_type():
    provider = FakeProvider()
    result = await ChatService(provider).answer(uuid4(), "Tôi dùng checklist trên web như thế nào?")
    assert result.disposition == "answered"
    assert result.provider_used
    assert provider.calls == 1
    assert result.citations[0].source_id == "product-guide"
    assert result.citations[0].kind == "product"


async def test_fabricated_source_or_money_in_model_output_is_not_displayed():
    for generated in [
        GeneratedAnswer(reply="Theo nguồn không được duyệt.", source_ids=["made-up"]),
        GeneratedAnswer(reply="Bạn phải nộp 10 triệu đồng.", source_ids=["product-guide"]),
    ]:
        result = await ChatService(FakeProvider(generated)).answer(uuid4(), "Giải thích checklist")
        assert result.disposition == "insufficient_sources"
        assert "10 triệu" not in result.reply


async def test_chat_rate_limit_is_scoped_to_owner():
    service = ChatService(FakeProvider())
    owner = uuid4()
    for _ in range(3):
        await service.answer(owner, "Giải thích checklist")
    with pytest.raises(ApplicationError) as caught:
        await service.answer(owner, "Giải thích checklist")
    assert caught.value.status == 429
    assert (await service.answer(uuid4(), "Giải thích checklist")).provider_used


async def test_gemini_adapter_sends_key_in_header_and_validates_json():
    def handle(request: httpx.Request):
        assert request.headers.get("x-goog-api-key")
        assert "key=" not in str(request.url)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"reply":"Chọn trạng thái giấy tờ.",'
                                        '"sourceIds":["product-guide"]}'
                                    ),
                                }
                            ]
                        }
                    }
                ]
            },
        )

    provider = GeminiProvider(
        "unit-test-only", "gemini-3.5-flash-lite", httpx.MockTransport(handle)
    )
    result = await provider.generate("Cách dùng checklist?", [])
    assert result.source_ids == ["product-guide"]


async def test_quota_is_reported_without_provider_body_or_secret():
    provider = GeminiProvider(
        "unit-test-only",
        "gemini-3.5-flash-lite",
        httpx.MockTransport(
            lambda _: httpx.Response(429, json={"error": "private provider payload"}),
        ),
    )
    with pytest.raises(ApplicationError) as caught:
        await provider.generate("Cách dùng checklist?", [])
    assert caught.value.status == 429
    assert "private" not in caught.value.detail


GOOD_BODY = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {"text": '{"reply":"Chọn trạng thái giấy tờ.","sourceIds":["product-guide"]}'}
                ]
            },
            "finishReason": "STOP",
        }
    ]
}


def flaky_provider(monkeypatch, *outcomes):
    """Trả lần lượt các kết quả (Response hoặc Exception); đếm số lần gọi."""
    monkeypatch.setattr("src.modules.chat.provider.RETRY_DELAY", 0)
    calls = []

    def handle(request: httpx.Request):
        outcome = outcomes[min(len(calls), len(outcomes) - 1)]
        calls.append(request)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    provider = GeminiProvider(
        "unit-test-only", "gemini-3.5-flash-lite", httpx.MockTransport(handle)
    )
    return provider, calls


async def test_provider_retries_once_after_model_overload(monkeypatch):
    overloaded = httpx.Response(503, json={"error": {"status": "UNAVAILABLE"}})
    provider, calls = flaky_provider(monkeypatch, overloaded, httpx.Response(200, json=GOOD_BODY))
    result = await provider.generate("Cách dùng checklist?", [])
    assert result.source_ids == ["product-guide"]
    assert len(calls) == 2


async def test_provider_retries_when_answer_is_cut_off(monkeypatch):
    cut_off = {
        "candidates": [
            {"content": {"parts": [{"text": '{"reply":"Bước'}]}, "finishReason": "MAX_TOKENS"}
        ]
    }
    provider, calls = flaky_provider(
        monkeypatch, httpx.Response(200, json=cut_off), httpx.Response(200, json=GOOD_BODY)
    )
    assert (await provider.generate("Cách dùng checklist?", [])).source_ids == ["product-guide"]
    assert len(calls) == 2


async def test_retry_after_recitation_asks_for_paraphrase_with_more_variety(monkeypatch):
    recited = {"candidates": [{"finishReason": "RECITATION"}]}
    provider, calls = flaky_provider(
        monkeypatch, httpx.Response(200, json=recited), httpx.Response(200, json=GOOD_BODY)
    )
    await provider.generate("Thủ tục giải thể?", [])
    first, second = (json.loads(call.content) for call in calls)
    assert "không chép lại nguyên văn" not in first["systemInstruction"]["parts"][0]["text"]
    assert "không chép lại nguyên văn" in second["systemInstruction"]["parts"][0]["text"]
    assert second["generationConfig"]["temperature"] > first["generationConfig"]["temperature"]


async def test_provider_retries_when_candidate_has_no_content(monkeypatch):
    blocked = {"candidates": [{"finishReason": "SAFETY"}]}
    provider, calls = flaky_provider(
        monkeypatch, httpx.Response(200, json=blocked), httpx.Response(200, json=GOOD_BODY)
    )
    assert (await provider.generate("Cách dùng checklist?", [])).source_ids == ["product-guide"]
    assert len(calls) == 2


async def test_provider_retries_after_read_timeout(monkeypatch):
    provider, calls = flaky_provider(
        monkeypatch, httpx.ReadTimeout("slow"), httpx.Response(200, json=GOOD_BODY)
    )
    assert (await provider.generate("Cách dùng checklist?", [])).source_ids == ["product-guide"]
    assert len(calls) == 2


async def test_provider_reports_slow_assistant_after_two_timeouts(monkeypatch):
    provider, calls = flaky_provider(monkeypatch, httpx.ReadTimeout("slow"))
    with pytest.raises(ApplicationError) as caught:
        await provider.generate("Cách dùng checklist?", [])
    assert caught.value.status == 504
    assert len(calls) == MAX_ATTEMPTS


async def test_provider_reports_unclear_answer_after_two_invalid_replies(monkeypatch):
    provider, calls = flaky_provider(monkeypatch, httpx.Response(200, json={"candidates": []}))
    with pytest.raises(ApplicationError) as caught:
        await provider.generate("Cách dùng checklist?", [])
    assert caught.value.status == 503
    assert len(calls) == MAX_ATTEMPTS


async def test_provider_does_not_retry_when_quota_is_exhausted(monkeypatch):
    provider, calls = flaky_provider(monkeypatch, httpx.Response(429, json={}))
    with pytest.raises(ApplicationError) as caught:
        await provider.generate("Cách dùng checklist?", [])
    assert caught.value.status == 429
    assert len(calls) == 1


def test_total_wait_stays_below_browser_timeout():
    from src.modules.chat import provider as module

    # api.client.ts hủy yêu cầu sau 25 giây; backend phải báo lỗi trước đó
    assert module.TOTAL_DEADLINE < 25


@pytest.mark.parametrize(
    "message",
    [
        "Doanh thu phát sinh nghĩa là gì trong checklist?",
        "Phát hành hóa đơn liên quan mục nào trong checklist?",
        "Kỳ 2020-2023 tôi cần đánh dấu trạng thái checklist thế nào?",
        "Hồ sơ thuế cần lưu ở mục nào trong checklist?",
    ],
)
async def test_common_tax_words_are_not_mistaken_for_penalty_or_private_data(message):
    result = await ChatService(FakeProvider()).answer(uuid4(), message)
    assert result.disposition == "answered"


@pytest.mark.parametrize(
    ("message", "disposition"),
    [
        ("Doanh nghiệp tôi có bị phạt không?", "expert_review"),
        ("Mức phạt chậm nộp hồ sơ là bao nhiêu?", "expert_review"),
        ("MST của tôi là 0312-AB, kiểm tra giúp", "blocked_input"),
        ("Mã số thuế là gì?", "insufficient_sources"),
        ("Chấm dứt hiệu lực mã số thuế là gì?", "insufficient_sources"),
    ],
)
async def test_penalty_and_identifier_values_are_still_caught(message, disposition):
    result = await ChatService(FakeProvider()).answer(uuid4(), message)
    assert result.disposition == disposition
