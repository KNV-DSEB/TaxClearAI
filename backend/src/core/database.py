"""Async SQLAlchemy engine + session factory.

Engines connect lazily (no connection is opened until the first query), so
importing this module is safe even before a real DATABASE_URL points at a
running database — see AGENTS.md "Architecture Rules" for the repository
pattern this powers.
"""

import urllib.parse
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings

settings = get_settings()


def _normalize_db_url(url: str | None) -> str:
    if not url:
        return "postgresql+asyncpg://localhost/placeholder"
    parsed = urllib.parse.urlsplit(url)
    scheme = parsed.scheme
    if scheme in ("postgres", "postgresql"):
        scheme = "postgresql+asyncpg"
    query_params = urllib.parse.parse_qs(parsed.query)
    cleaned_params: dict[str, str] = {}
    if "sslmode" in query_params or "ssl" in query_params:
        cleaned_params["ssl"] = "require"
    for k, v in query_params.items():
        if k not in ("channel_binding", "sslmode", "ssl"):
            cleaned_params[k] = v[0]
    new_query = urllib.parse.urlencode(cleaned_params)
    return urllib.parse.urlunsplit((scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))


_engine = create_async_engine(
    _normalize_db_url(settings.database_url),
    pool_pre_ping=True,
)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Shared declarative base — see src/models/base.py for common columns."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session
