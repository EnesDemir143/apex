"""Analysis domain model."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from apex.domain.value_objects import Indicator, Signal


class AnalysisResult(BaseModel):
    """Result produced by the 4-agent workflow for a single ticker."""

    run_id: UUID | None = None
    ticker: str
    signal: Signal
    confidence: float = Field(ge=0.0, le=1.0)
    summary: dict[str, Any] = Field(default_factory=dict)
    indicators: list[Indicator] = Field(default_factory=list)
    total_tokens: int = 0
    cost_usd: float = Field(default=0.0, ge=0.0)
    latency_ms: int | None = None
    status: str = "completed"
    created_at: datetime | None = None
