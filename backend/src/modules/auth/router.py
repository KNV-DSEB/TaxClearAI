from fastapi import APIRouter, Cookie, Depends, Response

from src.core.config import get_settings
from src.core.schemas import Envelope
from src.modules.auth.dependencies import get_auth_service, get_current_user
from src.modules.auth.domain import UserRecord
from src.modules.auth.schemas import LoginRequest, RefreshView, SessionView, UserView
from src.modules.auth.service import AuthService, SessionTokens

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def secure_cookies() -> bool:
    return get_settings().environment != "development"


# Frontend chuyển tiếp /api/v1 qua cùng tên miền nên giữ SameSite=Strict cả khi deploy
def set_session_cookies(response: Response, tokens: SessionTokens) -> None:
    for name, value, max_age, path in (
        ("access_token", tokens.access_token, 900, "/api/v1"),
        ("refresh_token", tokens.refresh_token, 604800, "/api/v1/auth"),
    ):
        response.set_cookie(
            name,
            value,
            max_age=max_age,
            path=path,
            httponly=True,
            secure=secure_cookies(),
            samesite="strict",
        )


def session_view(response: Response, tokens: SessionTokens) -> Envelope[SessionView]:
    set_session_cookies(response, tokens)
    response.headers["Location"] = "/api/v1/auth/sessions/current"
    return Envelope(
        data=SessionView(
            user=UserView(id=tokens.user.id, username=tokens.user.username),
            expires_at=tokens.expires_at,
        )
    )


@router.post("/sessions", status_code=201, response_model=Envelope[SessionView])
async def create_session(
    data: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> Envelope[SessionView]:
    return session_view(response, await service.login(data.username, data.password))


@router.post("/guest-sessions", status_code=201, response_model=Envelope[SessionView])
async def create_guest_session(
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> Envelope[SessionView]:
    return session_view(response, await service.guest())


@router.post("/refreshes", response_model=Envelope[RefreshView])
async def refresh_session(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> Envelope[RefreshView]:
    tokens = await service.refresh(refresh_token)
    set_session_cookies(response, tokens)
    return Envelope(data=RefreshView(expires_at=tokens.expires_at))


@router.get("/sessions/current", response_model=Envelope[UserView])
async def read_session(user: UserRecord = Depends(get_current_user)) -> Envelope[UserView]:
    return Envelope(data=UserView(id=user.id, username=user.username))


@router.delete("/sessions/current", status_code=204)
async def delete_session(
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> Response:
    await service.logout(refresh_token)
    response = Response(status_code=204)
    for name, path in (("access_token", "/api/v1"), ("refresh_token", "/api/v1/auth")):
        response.delete_cookie(
            name, path=path, httponly=True, secure=secure_cookies(), samesite="strict"
        )
    return response
