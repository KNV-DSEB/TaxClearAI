"""RFC 7807 Problem Details error handling — see AGENTS.md "Code Style Rules"."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse


def _problem(status_code: int, title: str, detail: str, instance: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "type": f"https://httpstatuses.com/{status_code}",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _problem(exc.status_code, "HTTP Error", str(exc.detail), request.url.path)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _problem(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation Error",
            str(exc.errors()),
            request.url.path,
        )
