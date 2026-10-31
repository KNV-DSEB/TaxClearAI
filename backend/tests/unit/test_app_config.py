from src.core.config import Settings


def test_app_title_has_hkd_and_company_support_default() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_title == "Nền tảng hỗ trợ chấm dứt hoạt động HKD/DN"
    assert settings.api_rate_limit_per_minute == 60
    assert settings.chatbot_rate_limit_per_minute == 20
