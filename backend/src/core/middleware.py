"""CORS + request-ID middleware setup."""

import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware


async def _request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


def register_middleware(app: FastAPI) -> None:
    app.middleware("http")(_request_id_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten this for production — see AGENTS.md "Security Rules"
        allow_methods=["*"],
        allow_headers=["*"],
    )
