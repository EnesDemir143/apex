"""PredictionBand domain model."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PredictionBand(BaseModel):
    """Price prediction band for a ticker on a given date."""

    ticker: str
    target_date: date
    lower_bound: Decimal
    upper_bound: Decimal
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str = "v1"
