"""Watchlist domain models for analysis-only tracked tickers."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from apex.domain.models.analysis import AnalysisResult


class WatchlistItem(BaseModel):
    """A ticker tracked for analysis without portfolio ownership assumptions."""

    ticker: str
    current_price: Decimal | None = None
    latest_analysis: AnalysisResult | None = None


class Watchlist(BaseModel):
    """Aggregate view of tickers monitored by the analysis system."""

    items: list[WatchlistItem] = Field(default_factory=list)
