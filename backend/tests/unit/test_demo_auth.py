import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.core.config import get_settings
from src.core.errors import ApplicationError
from src.core.security import hash_password
from src.modules.auth.domain import UserRecord
from src.modules.auth.service import AuthService


class FakeAuthRepository:
    def __init__(self) -> None:
        self.users: dict[str, UserRecord] = {}
        self.refreshes: list[tuple] = []

    async def find_user(self, username: str) -> UserRecord | None:
        return self.users.get(username)

    async def find_by_id(self, user_id):
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

    async def bootstrap(self, username: str, password_hash: str) -> None:
        if username not in self.users:
            self.users[username] = UserRecord(uuid4(), username, password_hash, True)

    async def add_refresh(self, user_id, token_hash: str, expires_at: datetime) -> None:
        self.refreshes.append((user_id, token_hash, expires_at))

    async def rotate_refresh(self, old_hash: str, new_hash: str) -> UserRecord | None:
        return None

    async def revoke_refresh(self, token_hash: str) -> None:
        pass


def test_demo_login_accepts_any_password_and_auto_bootstraps():
    settings = get_settings()
    original_secret = settings.jwt_secret_key
    object.__setattr__(settings, "jwt_secret_key", "secret-must-be-at-least-32-chars-long!")
    try:
        repo = FakeAuthRepository()
        service = AuthService(repo)

        # 1. demo auto-bootstraps and accepts any password
        session = asyncio.run(service.login("demo", "arbitrary_password_123"))
        assert session.user.username == "demo"
        assert session.access_token is not None
        assert session.refresh_token is not None

        # 2. demo accepts another completely different password
        session2 = asyncio.run(service.login("demo", "completely_different_pass!"))
        assert session2.user.username == "demo"

        # 3. Non-demo user requires correct password
        asyncio.run(repo.bootstrap("real_user", hash_password("correct_password_16_chars")))
        with pytest.raises(ApplicationError) as exc_info:
            asyncio.run(service.login("real_user", "wrong_password"))
        assert exc_info.value.status == 401

        session_real = asyncio.run(service.login("real_user", "correct_password_16_chars"))
        assert session_real.user.username == "real_user"
    finally:
        object.__setattr__(settings, "jwt_secret_key", original_secret)
