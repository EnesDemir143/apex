"""Domain value objects: Signal enum and Indicator model."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Signal(StrEnum):
    """Trading signal produced by the agent workflow."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Indicator(BaseModel):
    """A single technical or fundamental indicator with its computed value."""

    name: str
    value: float
    interpretation: str = ""
