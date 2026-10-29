from fastapi import Cookie, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.contextvars import bind_contextvars

from src.core.database import get_db
from src.modules.auth.domain import UserRecord
from src.modules.auth.repository import AuthRepository
from src.modules.auth.service import AuthService


def get_auth_service(session: AsyncSession = Depends(get_db, use_cache=False)) -> AuthService:
    return AuthService(AuthRepository(session))


async def get_current_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> UserRecord:
    user = await service.current_user(access_token)
    request.state.user_id = str(user.id)
    bind_contextvars(user_id=str(user.id))
    return user
