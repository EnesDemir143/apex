"""Watchlist API routes."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apex.domain.models import Watchlist, WatchlistItem

router = APIRouter(prefix="/api/v1", tags=["watchlist"])


class WatchlistResponse(BaseModel):
    """Watchlist response envelope."""

    watchlist: Watchlist
    source: str = Field(default="stub")


@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist() -> WatchlistResponse:
    """Return stub watchlist data for analysis-only tracking."""
    return WatchlistResponse(watchlist=Watchlist(items=[WatchlistItem(ticker="AAPL")]))
