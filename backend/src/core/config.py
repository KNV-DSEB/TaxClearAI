"""The ONE place that reads environment variables — see AGENTS.md "Security Rules"."""

from functools import lru_cache

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
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
