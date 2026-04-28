"""FastAPI dependency injection placeholders."""

from __future__ import annotations

from collections.abc import AsyncGenerator


async def get_db_session() -> AsyncGenerator[None]:
    """Placeholder DB session dependency — implemented in Phase 5."""
    yield None


async def get_redis() -> AsyncGenerator[None]:
    """Placeholder Redis dependency — implemented in Phase 5."""
    yield None
