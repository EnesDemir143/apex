"""Distributed lock backed by Redis for concurrent analysis guard."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

_LOCK_PREFIX = "apex:lock:"


class DistributedLock:
    """Thin wrapper around redis.lock() with a configurable timeout.

    Usage::

        lock = DistributedLock(redis_client, "analyze:AAPL", timeout=30)
        async with lock:
            ...  # exclusive section
    """

    def __init__(self, redis: Any, name: str, timeout: float = 30.0) -> None:
        self._redis = redis
        self._name = f"{_LOCK_PREFIX}{name}"
        self._timeout = timeout
        self._lock: Any = None

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[None]:
        """Async context manager that acquires the lock and releases on exit."""
        lock = self._redis.lock(self._name, timeout=self._timeout)
        acquired = await lock.acquire(blocking=True)
        if not acquired:
            raise RuntimeError(f"Could not acquire lock: {self._name}")
        logger.debug("lock.acquired", name=self._name, timeout=self._timeout)
        try:
            yield
        finally:
            await lock.release()
            logger.debug("lock.released", name=self._name)

    async def __aenter__(self) -> DistributedLock:
        self._lock = self._redis.lock(self._name, timeout=self._timeout)
        acquired = await self._lock.acquire(blocking=True)
        if not acquired:
            raise RuntimeError(f"Could not acquire lock: {self._name}")
        logger.debug("lock.acquired", name=self._name, timeout=self._timeout)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._lock is not None:
            await self._lock.release()
            logger.debug("lock.released", name=self._name)
            self._lock = None
