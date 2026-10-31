"""The ONE place that reads environment variables — see AGENTS.md "Security Rules"."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_title: str = "Nền tảng hỗ trợ chấm dứt hoạt động HKD/DN"
    environment: str = "development"
    port: int = 8000
    database_url: str | None = None
    jwt_secret_key: str = "change-me"
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
        "vbpl.vn,xaydungchinhsach.chinhphu.vn"
    )
    law_max_age_days: int = Field(default=30, ge=1, le=3650)
    ai_provider_data_terms_ack: bool = False

    @property
    def allowed_law_domains(self) -> frozenset[str]:
        return frozenset(
            domain.strip().lower().rstrip(".")
            for domain in self.law_source_allowlist.split(",")
            if domain.strip()
        )

    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
