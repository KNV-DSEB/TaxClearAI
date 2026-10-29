"""The ONE place that reads environment variables — see AGENTS.md "Security Rules"."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    port: int = 8000
    database_url: str | None = None
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    frontend_origin: str = "http://localhost:3000"
    bootstrap_username: str = ""
    bootstrap_password: str = ""
    gemini_api_key: str = ""
    gemini_model: str = ""
    test_database_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
