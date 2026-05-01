"""E2E tests: full pipeline from HTTP request to BUY/SELL/HOLD response."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_e2e(e2e_client: AsyncClient) -> None:
    """Liveness probe returns 200."""
    resp = await e2e_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")


@pytest.mark.asyncio
async def test_analyze_returns_signal(e2e_client: AsyncClient) -> None:
    """POST /api/v1/analyze/AAPL returns a valid BUY/SELL/HOLD signal with confidence."""
    resp = await e2e_client.post("/api/v1/analyze/AAPL")
    assert resp.status_code == 200
    data = resp.json()

    assert data["ticker"] == "AAPL"
    assert data["signal"] in ("BUY", "SELL", "HOLD")
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["status"] in ("completed", "degraded", "rejected")


@pytest.mark.asyncio
async def test_analyze_non_whitelisted_ticker(e2e_client: AsyncClient) -> None:
    """Non-whitelisted ticker returns rejected status."""
    resp = await e2e_client.post("/api/v1/analyze/FAKEXYZ")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_ohlcv_returns_bars(e2e_client: AsyncClient) -> None:
    """GET /api/v1/ohlcv/AAPL returns a list of OHLCV bars."""
    resp = await e2e_client.get("/api/v1/ohlcv/AAPL?days=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert len(data["bars"]) > 0
    bar = data["bars"][0]
    assert "open" in bar and "close" in bar and "volume" in bar
