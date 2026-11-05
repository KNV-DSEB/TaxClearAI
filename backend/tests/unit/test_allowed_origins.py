from src.core import middleware


class FakeSettings:
    frontend_origin = " https://tax-clear-ai.vercel.app/ , http://localhost:3000 ,"


def test_allowed_origins_ignores_spaces_trailing_slash_and_empty_items(monkeypatch):
    monkeypatch.setattr(middleware, "get_settings", lambda: FakeSettings())
    assert middleware.allowed_origins() == [
        "https://tax-clear-ai.vercel.app",
        "http://localhost:3000",
    ]
