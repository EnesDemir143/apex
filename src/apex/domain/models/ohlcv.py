"""OHLCV bar and response Pydantic models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, model_validator


class OHLCVBar(BaseModel):
    """Single OHLCV candlestick bar with data quality validation."""

    ticker: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    source: str = "alpaca"

    @field_validator("close")
    @classmethod
    def close_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("close must be > 0")
        return v

    @field_validator("volume")
    @classmethod
    def volume_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("volume must be >= 0")
        return v

    @model_validator(mode="after")
    def high_gte_low(self) -> OHLCVBar:
        if self.high < self.low:
            raise ValueError("high must be >= low")
        return self


class OHLCVResponse(BaseModel):
    """Container for a list of OHLCV bars with metadata."""

    bars: list[OHLCVBar]
    ticker: str
    source: str
    degraded: bool = False
