"""Portfolio API routes."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apex.domain.models import Portfolio, PortfolioPosition

router = APIRouter(prefix="/api/v1", tags=["portfolio"])


class PortfolioResponse(BaseModel):
    """Portfolio response envelope."""

    portfolio: Portfolio
    source: str = Field(default="stub")


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio() -> PortfolioResponse:
    """Return stub portfolio data."""
    return PortfolioResponse(portfolio=Portfolio(positions=[PortfolioPosition(ticker="AAPL")]))
