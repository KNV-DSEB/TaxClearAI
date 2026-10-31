import time
from collections import deque
from threading import Lock

from fastapi import HTTPException, Request, status

from src.core.config import get_settings

_WINDOW_SECONDS = 60
_requests_by_client: dict[tuple[str, str], deque[float]] = {}
_requests_lock = Lock()


async def enforce_api_rate_limit(request: Request) -> None:
    """Apply the shared per-IP limit for non-chatbot write endpoints."""
    await _enforce_limit(
        request,
        scope="api",
        max_requests=get_settings().api_rate_limit_per_minute,
    )


async def enforce_chatbot_rate_limit(request: Request) -> None:
    """Apply the configured chatbot-specific per-IP limit."""
    await _enforce_limit(
        request,
        scope="chatbot",
        max_requests=get_settings().chatbot_rate_limit_per_minute,
    )


async def _enforce_limit(request: Request, *, scope: str, max_requests: int) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = (scope, client_ip)
    now = time.monotonic()
    with _requests_lock:
        timestamps = _requests_by_client.setdefault(key, deque())
        while timestamps and now - timestamps[0] >= _WINDOW_SECONDS:
            timestamps.popleft()
        if len(timestamps) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Bạn đã gửi quá nhiều yêu cầu trong thời gian ngắn. Vui lòng thử lại sau.",
            )
        timestamps.append(now)


def reset_rate_limit_state(scope: str | None = None) -> None:
    """Clear local limiter state for tests or controlled process resets."""
    with _requests_lock:
        if scope is None:
            _requests_by_client.clear()
            return
        for key in [key for key in _requests_by_client if key[0] == scope]:
            del _requests_by_client[key]
