from typing import AsyncGenerator
import time
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base

# Primary async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Fallback SQLite engine for seamless local development
_fallback_engine = None
_postgres_unavailable_since: float | None = None
_postgres_retry_interval_seconds = 60


async def get_engine():
    global engine, _fallback_engine, _postgres_unavailable_since
    # Once PostgreSQL fails, use the local development fallback immediately for
    # a short cooldown instead of adding a failed network authentication attempt
    # to every request.
    postgres_in_cooldown = (
        _postgres_unavailable_since is not None
        and time.monotonic() - _postgres_unavailable_since < _postgres_retry_interval_seconds
    )
    if postgres_in_cooldown:
        # Do not reset the timestamp here: otherwise sustained traffic would
        # keep PostgreSQL permanently in cooldown and it could never recover.
        return await _get_fallback_engine()

    try:
        async with engine.connect() as conn:
            _postgres_unavailable_since = None
            return engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection error: {e}. Switching to local SQLite fallback database.")
        _postgres_unavailable_since = time.monotonic()
        return await _get_fallback_engine()


async def _get_fallback_engine():
    global _fallback_engine
    if _fallback_engine is None:
        sqlite_url = "sqlite+aiosqlite:///./data/enterprise_rag.db"
        _fallback_engine = create_async_engine(sqlite_url, echo=False)
        async with _fallback_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    return _fallback_engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency generator for FastAPI routes to yield an async database session."""
    active_engine = await get_engine()
    session_factory = async_sessionmaker(
        bind=active_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
