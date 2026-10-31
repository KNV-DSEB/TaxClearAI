import json
from types import SimpleNamespace
from typing import Any

import pytest

from src.core.config import Settings
from src.modules.chatbot.llm import AnthropicLLM
from src.modules.chatbot.schemas import LawEntry, Segment


class FakeAnthropicClient:
    def __init__(self, calls: list[dict[str, Any]]) -> None:
        self.calls = calls

    async def __aenter__(self) -> "FakeAnthropicClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        del args

    @property
    def messages(self) -> "FakeAnthropicClient":
        return self

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text='{"suggested_segment":"A1"}')]
        )


@pytest.mark.asyncio
async def test_anthropic_redacts_situation_guardrail_and_answer_at_provider_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_client(**kwargs: Any) -> FakeAnthropicClient:
        assert kwargs["api_key"] == "test-key"
        return FakeAnthropicClient(calls)

    monkeypatch.setattr("src.modules.chatbot.llm.AsyncAnthropic", fake_client)
    llm = AnthropicLLM(
        Settings(
            _env_file=None,
            chatbot_llm_provider="anthropic",
            anthropic_api_key="test-key",
        )
    )
    pii = "Nguyễn Văn An, MST 0123456789, a@example.vn, 0912345678"

    await llm.classify_situation({"entity_type": "HKD"}, f"Tôi tên là {pii}", "survey")
    await llm.classify_intent(f"Tôi tên là {pii}", Segment.A1, "Bước")
    await llm.generate_answer(
        f"Tôi tên là {pii}",
        Segment.A1,
        "Bước",
        {},
        [
            LawEntry(
                id="L1",
                van_ban="Văn bản",
                dieu_khoan="Điều 1",
                noi_dung=f"Nội dung {pii}",
                hieu_luc="Còn hiệu lực",
                tinh_trang="con_hieu_luc",
                link="https://example.invalid",
                ap_dung_cho=[Segment.A1],
            )
        ],
    )

    assert len(calls) == 3
    serialized_calls = json.dumps(calls, ensure_ascii=False)
    for sensitive in ("Nguyễn Văn An", "0123456789", "a@example.vn", "0912345678"):
        assert sensitive not in serialized_calls
