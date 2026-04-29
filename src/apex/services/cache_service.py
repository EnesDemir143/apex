"""Redis-backed cache service."""

from __future__ import annotations

from typing import Any


class CacheService:
    """Small Redis cache wrapper with Apex key prefixing."""

    def __init__(self, redis_client: Any, key_prefix: str = "apex:", default_ttl: int = 3600) -> None:
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

    async def get(self, key: str) -> str | None:
        """Return a cached string value, if present."""
        value = await self.redis.get(self._key(key))
        return value if isinstance(value, str) or value is None else str(value)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set a cached string value with optional TTL."""
        await self.redis.set(self._key(key), value, ex=ttl if ttl is not None else self.default_ttl)

    async def invalidate(self, key: str) -> int:
        """Delete a cached value and return the number of keys removed."""
        return int(await self.redis.delete(self._key(key)))

    def _key(self, key: str) -> str:
        return f"{self.key_prefix}{key}"
