from uuid import uuid4

import httpx
import pytest

from src.core.errors import ApplicationError
from src.modules.chat.provider import GeminiProvider
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
