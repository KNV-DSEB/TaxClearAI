from fastapi import APIRouter, Cookie, Depends, Response

from src.core.config import get_settings
from src.core.schemas import Envelope
from src.modules.auth.dependencies import get_auth_service
from src.modules.auth.schemas import LoginRequest, RefreshView, SessionView, UserView
from src.modules.auth.service import AuthService, SessionTokens

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def set_session_cookies(response: Response, tokens: SessionTokens) -> None:
    secure = get_settings().environment != "development"
    response.set_cookie(
        "access_token",
        tokens.access_token,
        max_age=900,
        httponly=True,
        secure=secure,
        samesite="strict",
        path="/api/v1",
    )
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        max_age=604800,
        httponly=True,
        secure=secure,
        samesite="strict",
        path="/api/v1/auth",
    )


@router.post("/sessions", status_code=201, response_model=Envelope[SessionView])
async def create_session(
    data: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> Envelope[SessionView]:
    tokens = await service.login(data.username, data.password)
    set_session_cookies(response, tokens)
    response.headers["Location"] = "/api/v1/auth/sessions/current"
    return Envelope(
        data=SessionView(
            user=UserView(id=tokens.user.id, username=tokens.user.username),
            expires_at=tokens.expires_at,
        )
    )


@router.post("/refreshes", response_model=Envelope[RefreshView])
async def refresh_session(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> Envelope[RefreshView]:
    tokens = await service.refresh(refresh_token)
    set_session_cookies(response, tokens)
    return Envelope(data=RefreshView(expires_at=tokens.expires_at))


@router.delete("/sessions/current", status_code=204)
async def delete_session(
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> Response:
    await service.logout(refresh_token)
    response = Response(status_code=204)
    response.delete_cookie("access_token", path="/api/v1")
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return response
