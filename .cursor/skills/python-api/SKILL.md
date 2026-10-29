---
name: python-api
description: Reviews FastAPI backend code for framework idioms, Pydantic usage, async correctness, dependency injection, and Python-specific security. Activates when explicitly asked to review the Python API code — not run automatically on every edit.
applies_to: fastapi
---

This is an on-demand deep review — the baseline expectations this code should already meet come from `.cursor/rules/*.mdc` (this project's `backend-mvc` rule, FastAPI variant).

**FastAPI Patterns**
- Use `async def` for I/O-bound handlers; `def` for CPU-bound (runs in threadpool)
- Pydantic v2 models for all request/response schemas — no raw `dict`
- `Annotated[Type, Depends(...)]` for dependency injection
- `HTTPException` with a descriptive `detail`, not bare exceptions
- Path params validated via type annotations; query params via `Query(...)` with constraints
- `BackgroundTasks` for fire-and-forget work after the response

**Pydantic & Validation**
- `model_config = ConfigDict(strict=True)` where input must match exactly
- `@field_validator` for cross-field rules; `@model_validator` for whole-model rules
- Never expose internal models directly as API responses — use response schemas

**Async & Concurrency**
- `await` every coroutine — a missing `await` silently returns a coroutine object
- Use `asyncio.gather()` for concurrent I/O, not sequential `await` in a loop
- Database sessions not shared across concurrent requests
- Async DB drivers (`asyncpg`, `aiomysql`) or SQLAlchemy `AsyncSession`

**Dependency Injection**
- `Depends()` for database sessions, auth, config — never global state
- Lifespan context manager for startup/shutdown logic

**Error Handling**
- Custom exception handlers registered on the `app` instance
- Structured error response: `{"code": "...", "message": "...", "details": []}`
- Log exceptions with tracebacks; never swallow silently

**Security**
- `python-jose` or `PyJWT` for JWT; validate `exp`, `iss`, `aud`
- CORS restricted to known origins — never `allow_origins=["*"]` in production
- SQL queries via ORM or parameterized — never f-strings into queries
- Secrets from environment variables; never in source code

**Python Idioms**
- Type hints on every function signature
- Prefer comprehensions over explicit loops for transformations
- Use `pathlib.Path` over `os.path`
- `dataclasses` or Pydantic for internal data; plain `dict` only at the edges

Flag: missing `await`, global state, bare `except`, dict-based schemas, hardcoded secrets.
