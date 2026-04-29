"""Portfolio domain model."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from apex.domain.models.analysis import AnalysisResult


class PortfolioPosition(BaseModel):
    """A single position in the portfolio."""

    ticker: str
    quantity: Decimal = Decimal("0")
    avg_entry_price: Decimal | None = None
    current_price: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    latest_analysis: AnalysisResult | None = None


class Portfolio(BaseModel):
    """Aggregate portfolio view."""

    positions: list[PortfolioPosition] = Field(default_factory=list)
    total_value: Decimal = Decimal("0")
    total_pnl: Decimal = Decimal("0")
