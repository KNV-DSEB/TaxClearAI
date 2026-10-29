import asyncio
import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.core.config import get_settings
from src.core.errors import ApplicationError
from src.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from src.modules.auth.domain import UserRecord
from src.modules.auth.repository import AuthRepository


@dataclass(frozen=True)
class SessionTokens:
    user: UserRecord
    access_token: str
    refresh_token: str
    expires_at: datetime


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def require_secret() -> None:
    settings = get_settings()
    if len(settings.jwt_secret_key) < 32 or settings.jwt_secret_key == "change-me":
        raise ApplicationError(503, "Phiên thử nghiệm chưa được cấu hình. Vui lòng liên hệ nhóm.")
    if settings.jwt_algorithm != "HS256":
        raise ApplicationError(503, "Phiên thử nghiệm chưa được cấu hình.")


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def bootstrap(self) -> None:
        settings = get_settings()
        require_secret()
        if not settings.bootstrap_username or len(settings.bootstrap_password) < 16:
            raise ApplicationError(503, "Chưa cấu hình tài khoản thử nghiệm.")
        hashed = await asyncio.to_thread(hash_password, settings.bootstrap_password)
        await self.repository.bootstrap(settings.bootstrap_username, hashed)

    def tokens(self, user: UserRecord, refresh: str) -> SessionTokens:
        expiry = datetime.now(UTC) + timedelta(minutes=15)
        return SessionTokens(user, create_access_token(str(user.id)), refresh, expiry)

    async def login(self, username: str, password: str) -> SessionTokens:
        require_secret()
        if len(password.encode("utf-8")) > 72:
            raise ApplicationError(422, "Mật khẩu vượt giới hạn độ dài cho phép.")
        user = await self.repository.find_user(username)
        if user is None or not user.is_active:
            await asyncio.to_thread(hash_password, password)
            raise ApplicationError(401, "Tên đăng nhập hoặc mật khẩu chưa đúng.")
        valid = await asyncio.to_thread(verify_password, password, user.password_hash)
        if not valid:
            raise ApplicationError(401, "Tên đăng nhập hoặc mật khẩu chưa đúng.")
        refresh = secrets.token_urlsafe(48)
        await self.repository.add_refresh(
            user.id, digest_token(refresh), datetime.now(UTC) + timedelta(days=7)
        )
        return self.tokens(user, refresh)

    async def current_user(self, token: str | None) -> UserRecord:
        require_secret()
        claims = decode_access_token(token) if token else None
        try:
            user_id = UUID(str(claims["sub"])) if claims else None
        except (KeyError, ValueError):
            user_id = None
        user = await self.repository.find_by_id(user_id) if user_id else None
        if user is None or not user.is_active:
            raise ApplicationError(401, "Phiên đã hết hạn. Vui lòng đăng nhập lại.")
        return user

    async def refresh(self, token: str | None) -> SessionTokens:
        require_secret()
        new_token = secrets.token_urlsafe(48)
        user = await self.repository.rotate_refresh(
            digest_token(token or ""), digest_token(new_token)
        )
        if user is None or not user.is_active:
            raise ApplicationError(401, "Phiên đã hết hạn. Vui lòng đăng nhập lại.")
        return self.tokens(user, new_token)

    async def logout(self, token: str | None) -> None:
        await self.repository.revoke_refresh(digest_token(token or ""))
