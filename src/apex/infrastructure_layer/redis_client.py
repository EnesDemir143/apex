"""Redis client factory and FastAPI dependency."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as redis

from apex.core.config import settings

_redis_client: Any | None = None


def create_redis_client() -> Any:
    """Create a Redis client configured for text responses."""
    return redis.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
    )


def get_redis_client() -> Any:
    """Return the process-wide Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = create_redis_client()
    return _redis_client


async def get_redis() -> AsyncGenerator[Any]:
    """Yield the process-wide Redis client for FastAPI dependencies."""
    yield get_redis_client()


async def close_redis() -> None:
    """Close the process-wide Redis client if it was opened."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
