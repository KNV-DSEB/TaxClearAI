"""Async SQLAlchemy engine + session factory.

Engines connect lazily (no connection is opened until the first query), so
importing this module is safe even before a real DATABASE_URL points at a
running database — see AGENTS.md "Architecture Rules" for the repository
pattern this powers.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings

settings = get_settings()

_engine = create_async_engine(
    settings.database_url or "postgresql+asyncpg://localhost/placeholder",
    pool_pre_ping=True,
)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Shared declarative base — see src/models/base.py for common columns."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session
