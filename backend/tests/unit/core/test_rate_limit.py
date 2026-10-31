import pytest
from fastapi import HTTPException
from starlette.requests import Request

from src.core.config import Settings
from src.core.rate_limit import (
    InMemoryRateLimitStore,
    enforce_api_rate_limit,
    enforce_chatbot_rate_limit,
    reset_rate_limit_state,
)


def test_in_memory_rate_limit_store_supports_scoped_reset() -> None:
    store = InMemoryRateLimitStore()

    assert store.allow("api", "192.0.2.1", 10.0, 1)
    assert not store.allow("api", "192.0.2.1", 11.0, 1)
    assert store.allow("chatbot", "192.0.2.1", 11.0, 1)
    store.reset("api")
    assert store.allow("api", "192.0.2.1", 12.0, 1)


def _request(client_ip: str) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/test",
            "raw_path": b"/test",
            "query_string": b"",
            "headers": [],
            "client": (client_ip, 12345),
            "server": ("testserver", 80),
        }
    )


@pytest.mark.asyncio
async def test_rate_limits_are_configurable_and_scoped_by_endpoint_group(monkeypatch) -> None:
    reset_rate_limit_state()
    settings = Settings(
        _env_file=None,
        api_rate_limit_per_minute=2,
        chatbot_rate_limit_per_minute=1,
    )
    monkeypatch.setattr("src.core.rate_limit.get_settings", lambda: settings)
    request = _request("192.0.2.10")

    await enforce_api_rate_limit(request)
    await enforce_api_rate_limit(request)
    with pytest.raises(HTTPException) as api_error:
        await enforce_api_rate_limit(request)

    assert api_error.value.status_code == 429
    await enforce_chatbot_rate_limit(request)
    with pytest.raises(HTTPException) as chatbot_error:
        await enforce_chatbot_rate_limit(request)

    assert chatbot_error.value.status_code == 429
    reset_rate_limit_state()
