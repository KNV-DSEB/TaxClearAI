import logging

import pytest
from fastapi.testclient import TestClient

from src.core.config import Settings


def test_app_title_defaults_to_tax_clear_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_TITLE", raising=False)
    settings = Settings(_env_file=None)

    assert settings.app_title == "Tax Clear AI"
    assert settings.api_rate_limit_per_minute == 60
    assert settings.chatbot_rate_limit_per_minute == 20


def test_openapi_title_is_tax_clear_ai(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Tax Clear AI"


def test_non_development_rejects_default_jwt_secret() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET_KEY must be changed"):
        Settings(_env_file=None, environment="production", jwt_secret_key="change-me")


@pytest.mark.parametrize(
    ("provider", "key_name"),
    [("gemini", "gemini_api_key"), ("anthropic", "anthropic_api_key")],
)
def test_missing_provider_key_warns_without_failing(
    caplog: pytest.LogCaptureFixture, provider: str, key_name: str
) -> None:
    with caplog.at_level(logging.WARNING):
        settings = Settings(_env_file=None, chatbot_llm_provider=provider, **{key_name: None})

    assert settings.chatbot_llm_provider == provider
    assert "is not configured" in caplog.text
    assert "fallback" in caplog.text


def test_production_warns_when_ai_provider_data_terms_are_not_acknowledged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):
        settings = Settings(
            _env_file=None,
            environment="production",
            jwt_secret_key="test-secret",
            ai_provider_data_terms_ack=False,
        )

    assert settings.ai_provider_data_terms_ack is False
    assert "AI_PROVIDER_DATA_TERMS_ACK is false" in caplog.text
    assert "paid provider plan" in caplog.text


def test_production_acknowledgement_suppresses_provider_terms_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):
        Settings(
            _env_file=None,
            environment="production",
            jwt_secret_key="test-secret",
            ai_provider_data_terms_ack=True,
        )

    assert "AI_PROVIDER_DATA_TERMS_ACK" not in caplog.text
