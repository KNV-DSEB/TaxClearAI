"""RFC 7807 Problem Details error handling — see AGENTS.md "Code Style Rules"."""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from src.core.errors import ApplicationError


def _problem(status_code: int, title: str, detail: str, instance: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content={
            "type": f"https://httpstatuses.com/{status_code}",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_exception_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        response = _problem(exc.status, "Không thể hoàn tất yêu cầu", exc.detail, request.url.path)
        if exc.status == 429:
            response.headers["Retry-After"] = "60"
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _problem(
            exc.status_code, "Không thể hoàn tất yêu cầu", str(exc.detail), request.url.path
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _problem(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Dữ liệu chưa hợp lệ",
            "Vui lòng kiểm tra các mục đã nhập và thử lại.",
            request.url.path,
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        structlog.get_logger().error(
            "request_failed",
            request_id=getattr(request.state, "request_id", None),
            user_id=getattr(request.state, "user_id", None),
            error_type=type(exc).__name__,
        )
        return _problem(500, "Chưa xử lý được yêu cầu", "Vui lòng thử lại sau.", request.url.path)
