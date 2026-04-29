"""Pydantic schemas that constrain agent tool inputs and outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field

from apex.domain.value_objects import Signal


class TradeDecisionInput(BaseModel):
    """Validated final trade decision payload for isolated tool boundaries."""

    ticker: str = Field(min_length=1)
    signal: Signal
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1)
    risk_score: float = Field(ge=0.0, le=1.0)
