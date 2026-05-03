"""Shared pytest fixtures. Tests run against an in-process SQLite database."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture(scope="session", autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Create a fresh in-memory schema and yield a session bound to it."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Yield an HTTPX AsyncClient bound to the FastAPI app, using the test session."""

    async def _override_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = _override_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_session, None)
