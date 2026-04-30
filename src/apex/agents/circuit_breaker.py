"""Redis-backed circuit breaker for workflow resilience."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from time import time
from typing import Any, TypeVar

T = TypeVar("T")


class CircuitOpenError(RuntimeError):
    """Raised when the circuit is open and calls must use fallback."""


class CircuitBreaker:
    """Circuit breaker with Redis-persisted state."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        redis_client: Any,
        *,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
    ) -> None:
        self.redis = redis_client
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """Call func unless the circuit is OPEN; record success/failure transitions."""
        state = await self.get_state()
        if state == self.OPEN:
            if await self._can_try_half_open():
                await self._set_state(self.HALF_OPEN)
            else:
                raise CircuitOpenError(f"Circuit {self.name} is open")

        try:
            result = await func(*args, **kwargs)
        except Exception:
            await self.record_failure()
            raise
        await self.record_success()
        return result

    async def get_state(self) -> str:
        """Return CLOSED, OPEN, or HALF_OPEN."""
        state = await self.redis.get(self._state_key())
        return state if state in {self.CLOSED, self.OPEN, self.HALF_OPEN} else self.CLOSED

    async def record_success(self) -> None:
        """Close the circuit and clear failure counters after a successful call."""
        await self.redis.delete(self._failure_key())
        await self.redis.delete(self._opened_at_key())
        await self._set_state(self.CLOSED)

    async def record_failure(self) -> None:
        """Increment failures and open the circuit when threshold is reached."""
        failures = int(await self.redis.incr(self._failure_key()))
        if failures >= self.failure_threshold:
            await self._set_state(self.OPEN)
            await self.redis.set(self._opened_at_key(), str(time()))

    async def _can_try_half_open(self) -> bool:
        opened_at = await self.redis.get(self._opened_at_key())
        if opened_at is None:
            return True
        return (time() - float(opened_at)) >= self.recovery_timeout

    async def _set_state(self, state: str) -> None:
        await self.redis.set(self._state_key(), state)

    def _state_key(self) -> str:
        return f"apex:circuit:{self.name}:state"

    def _failure_key(self) -> str:
        return f"apex:circuit:{self.name}:failures"

    def _opened_at_key(self) -> str:
        return f"apex:circuit:{self.name}:opened_at"
