"""Daily LLM budget guard."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from apex.core.config import get_settings
from apex.core.exceptions import LLMBudgetExceededError


class BudgetLimiter:
    """Track and enforce daily LLM spend."""

    def __init__(
        self,
        daily_budget_usd: float | None = None,
        redis_client: Any | None = None,
        key_prefix: str = "apex:budget",
    ) -> None:
        self.daily_budget_usd = (
            daily_budget_usd if daily_budget_usd is not None else get_settings().llm_daily_budget_usd
        )
        self.redis = redis_client
        self.key_prefix = key_prefix
        self._memory_usage: dict[str, float] = {}

    async def check_and_record(self, *, input_tokens: int, output_tokens: int, cost_usd: float) -> float:
        """Record a request if it fits inside the daily budget, returning the new total."""
        del input_tokens, output_tokens
        today_key = self._daily_key()
        current = await self._get_usage(today_key)
        projected = current + cost_usd
        if projected > self.daily_budget_usd:
            raise LLMBudgetExceededError(
                f"LLM daily budget exceeded: projected ${projected:.4f} > limit ${self.daily_budget_usd:.4f}"
            )
        await self._set_usage(today_key, projected)
        return projected

    async def current_usage(self) -> float:
        """Return current spend for the UTC day."""
        return await self._get_usage(self._daily_key())

    def _daily_key(self) -> str:
        return f"{self.key_prefix}:{datetime.now(UTC).date().isoformat()}"

    async def _get_usage(self, key: str) -> float:
        if self.redis is None:
            return self._memory_usage.get(key, 0.0)
        value = await self.redis.get(key)
        return float(value or 0.0)

    async def _set_usage(self, key: str, value: float) -> None:
        if self.redis is None:
            self._memory_usage[key] = value
            return
        await self.redis.set(key, str(value), ex=_seconds_until_tomorrow())


def _seconds_until_tomorrow() -> int:
    now = datetime.now(UTC)
    tomorrow = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
    return max(1, int((tomorrow - now).total_seconds()))
