"""Giới hạn đầu vào và bảo vệ phiên thử local."""

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.datastructures import Headers
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.core.config import get_settings
from src.core.exceptions import _problem

MAX_BODY = 8192


class ApiSecurityMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.buckets: dict[str, tuple[int, int]] = {}

    def limited(self, key: str, limit: int) -> bool:
        minute = int(time.monotonic() // 60)
        if len(self.buckets) > 10000:
            self.buckets = {key: value for key, value in self.buckets.items() if value[0] == minute}
        if len(self.buckets) > 10000:
            return True
        previous, count = self.buckets.get(key, (minute, 0))
        count = count + 1 if previous == minute else 1
        self.buckets[key] = (minute, count)
        return count > limit

    async def read_body(self, receive: Receive) -> bytes | None:
        body = bytearray()
        while True:
            message = await asyncio.wait_for(receive(), timeout=5)
            if message["type"] == "http.disconnect":
                return None
            body.extend(message.get("body", b""))
            if len(body) > MAX_BODY:
                return None
            if not message.get("more_body", False):
                return bytes(body)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if scope["type"] != "http" or not path.startswith("/api/v1"):
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        client = scope.get("client")
        key = str(client[0]) if client else "local"
        is_login = path == "/api/v1/auth/sessions" and scope["method"] == "POST"
        if self.limited(f"{'login' if is_login else 'api'}:{key}", 5 if is_login else 120):
            response = _problem(429, "Quá nhiều yêu cầu", "Vui lòng chờ một phút.", path)
            response.headers["Retry-After"] = "60"
            await response(scope, receive, send)
            return
        if scope["method"] in {"POST", "PATCH", "DELETE", "PUT"}:
            if headers.get("origin") != get_settings().frontend_origin:
                await _problem(403, "Không thể gửi yêu cầu", "Nguồn truy cập chưa hợp lệ.", path)(
                    scope, receive, send
                )
                return
            try:
                body = await self.read_body(receive)
            except TimeoutError:
                body = None
            if body is None:
                await _problem(
                    413,
                    "Dữ liệu quá lớn hoặc chưa đầy đủ",
                    "Vui lòng rút gọn nội dung và thử lại.",
                    path,
                )(scope, receive, send)
                return

            async def replay() -> Message:
                return {"type": "http.request", "body": body, "more_body": False}

            await self.app(scope, replay, send)
            return
        await self.app(scope, receive, send)


async def _request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    clear_contextvars()
    bind_contextvars(request_id=request_id)
    try:
        response = await call_next(request)
    finally:
        clear_contextvars()
    response.headers["x-request-id"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if get_settings().environment != "development":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    if request.url.path.startswith("/api/"):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(ApiSecurityMiddleware)
    app.middleware("http")(_request_id_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[get_settings().frontend_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
