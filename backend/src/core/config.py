"""The ONE place that reads environment variables — see AGENTS.md "Security Rules"."""

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_title: str = "Tax Clear AI"
    environment: str = "development"
    port: int = 8000
    database_url: str | None = None
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    api_rate_limit_per_minute: int = Field(default=60, ge=1, le=10000)
    chatbot_rate_limit_per_minute: int = Field(default=20, ge=1, le=10000)
    chatbot_llm_provider: Literal["gemini", "anthropic", "mock"] = "gemini"
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    model_guardrail: str = "gemini-2.5-flash-lite"
    model_answer: str = "gemini-2.5-flash"
    model_classifier: str | None = None
    survey_ai_enabled: bool = True
    chatbot_top_k: int = Field(default=6, ge=1, le=20)
    chatbot_min_retrieval_score: int = Field(default=1, ge=0)
    chatbot_mock_mode: bool = False
    chatbot_failsafe: str = "khong_chac_chan"
    chatbot_guardrail_cache_size: int = Field(default=512, ge=0, le=10000)
    law_source_allowlist: str = (
        "congbao.chinhphu.vn,g7.cdnchinhphu.vn,vanban.chinhphu.vn,datafiles.chinhphu.vn,"
        "vbpl.vn,xaydungchinhsach.chinhphu.vn,hue.gov.vn"
    )
    law_max_age_days: int = Field(default=30, ge=1, le=3650)
    law_ocr_enabled: bool = False
    law_ocr_tesseract_cmd: str = "tesseract"
    law_ocr_language: str = "vie"
    law_ocr_tessdata_dir: str | None = None
    law_ocr_min_confidence: float = Field(default=85, ge=0, le=100)
    ai_provider_data_terms_ack: bool = False

    @property
    def allowed_law_domains(self) -> frozenset[str]:
        return frozenset(
            domain.strip().lower().rstrip(".")
            for domain in self.law_source_allowlist.split(",")
            if domain.strip()
        )

    @model_validator(mode="after")
    def validate_runtime_secrets(self) -> "Settings":
        if self.environment != "development" and self.jwt_secret_key == "change-me":
            raise ValueError("JWT_SECRET_KEY must be changed outside development.")

        if self.chatbot_llm_provider == "gemini" and not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY is not configured; chatbot will use its fallback.")
        elif self.chatbot_llm_provider == "anthropic" and not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY is not configured; chatbot will use its fallback.")
        if self.environment == "production" and not self.ai_provider_data_terms_ack:
            logger.warning(
                "AI_PROVIDER_DATA_TERMS_ACK is false; confirm a paid provider plan and suitable "
                "data terms before sending user data to an AI provider; see the privacy section "
                "in docs/chatbot.md."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
