"""Tests for analysis-only watchlist models and route."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from apex.api.app import create_app
from apex.domain.models import Watchlist, WatchlistItem


def test_watchlist_model_has_no_portfolio_ownership_fields() -> None:
    """Watchlist items track tickers for analysis, not owned quantities."""
    item = WatchlistItem(ticker="AAPL")
    watchlist = Watchlist(items=[item])

    payload = watchlist.model_dump()

    assert payload == {"items": [{"ticker": "AAPL", "current_price": None, "latest_analysis": None}]}
    assert "quantity" not in WatchlistItem.model_fields
    assert "avg_entry_price" not in WatchlistItem.model_fields
    assert "unrealized_pnl" not in WatchlistItem.model_fields


@pytest.mark.asyncio
async def test_watchlist_route_returns_analysis_only_stub() -> None:
    """GET /api/v1/watchlist exposes tracked tickers instead of portfolio holdings."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/watchlist")

    assert response.status_code == 200
    assert response.json() == {
        "watchlist": {"items": [{"ticker": "AAPL", "current_price": None, "latest_analysis": None}]},
        "source": "stub",
    }
