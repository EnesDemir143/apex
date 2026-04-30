"""Tests for Redis-backed circuit breaker behavior."""

from __future__ import annotations

import pytest

from apex.agents.circuit_breaker import CircuitBreaker, CircuitOpenError


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str) -> None:
        self.store[key] = value

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            deleted += int(self.store.pop(key, None) is not None)
        return deleted

    async def incr(self, key: str) -> int:
        value = int(self.store.get(key, "0")) + 1
        self.store[key] = str(value)
        return value


@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions() -> None:
    breaker = CircuitBreaker(FakeRedis(), name="unit", failure_threshold=3, recovery_timeout=60)

    async def fail() -> None:
        raise RuntimeError("boom")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            await breaker.call(fail)

    assert await breaker.get_state() == CircuitBreaker.OPEN
    with pytest.raises(CircuitOpenError):
        await breaker.call(fail)

    await breaker.record_success()
    assert await breaker.get_state() == CircuitBreaker.CLOSED
