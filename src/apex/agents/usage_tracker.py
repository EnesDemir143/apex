"""Usage accounting for individual analysis agent turns."""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel, Field


class AnalysisTurnSummary(BaseModel):
    """Token, cost, and timing summary for one agent turn."""

    tokens_in: int = Field(ge=0)
    tokens_out: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
    errors: list[str] = Field(default_factory=list)
    duration_ms: int = Field(ge=0)
    agent_name: str


class UsageTracker:
    """Accumulate usage summaries for one analysis run."""

    def __init__(self) -> None:
        self._turns: list[AnalysisTurnSummary] = []

    @property
    def turns(self) -> tuple[AnalysisTurnSummary, ...]:
        """Return recorded turns in insertion order."""
        return tuple(self._turns)

    def add_turn(self, summary: AnalysisTurnSummary) -> None:
        """Record one agent turn."""
        self._turns.append(summary)

    def totals(self) -> dict[str, int | float]:
        """Return aggregate tokens and cost."""
        return {
            "tokens_in": sum(turn.tokens_in for turn in self._turns),
            "tokens_out": sum(turn.tokens_out for turn in self._turns),
            "cost_usd": sum(turn.cost_usd for turn in self._turns),
            "duration_ms": sum(turn.duration_ms for turn in self._turns),
            "error_count": sum(len(turn.errors) for turn in self._turns),
        }

    def by_agent(self) -> dict[str, dict[str, int | float]]:
        """Return aggregate usage grouped by agent name."""
        grouped: dict[str, dict[str, int | float]] = defaultdict(
            lambda: {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0, "duration_ms": 0, "error_count": 0}
        )
        for turn in self._turns:
            bucket = grouped[turn.agent_name]
            bucket["tokens_in"] += turn.tokens_in
            bucket["tokens_out"] += turn.tokens_out
            bucket["cost_usd"] += turn.cost_usd
            bucket["duration_ms"] += turn.duration_ms
            bucket["error_count"] += len(turn.errors)
        return dict(grouped)
