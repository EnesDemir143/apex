"""Unit tests for local market snapshot service."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from apex.domain.models.ohlcv import OHLCVBar, OHLCVResponse
from apex.services.market_snapshot import get_market_snapshot


class FailingFetcher:
    async def fetch_bars(self, ticker: str, start: object, end: object) -> OHLCVResponse:
        raise RuntimeError("offline")


class StaticFetcher:
    async def fetch_bars(self, ticker: str, start: object, end: object) -> OHLCVResponse:
        bars = [
            OHLCVBar(
                ticker=ticker,
                timestamp=datetime(2026, 1, 2 + i, tzinfo=UTC),
                open=Decimal("100") + Decimal(i),
                high=Decimal("102") + Decimal(i),
                low=Decimal("99") + Decimal(i),
                close=Decimal("101") + Decimal(i),
                volume=1000 + i,
                source="test",
            )
            for i in range(5)
        ]
        return OHLCVResponse(bars=bars, ticker=ticker, source="test", degraded=False)


@pytest.mark.asyncio
async def test_market_snapshot_uses_deterministic_fallback() -> None:
    snapshot = await get_market_snapshot("AAPL", fetcher=FailingFetcher())  # type: ignore[arg-type]

    assert snapshot.ticker == "AAPL"
    assert snapshot.source in ("stub", "fallback")
    assert len(snapshot.bars) == 60
    assert snapshot.latest.close == Decimal("209.4")
    assert snapshot.indicators.sma20 > 0


@pytest.mark.asyncio
async def test_market_snapshot_uses_fetcher_bars() -> None:
    snapshot = await get_market_snapshot("MSFT", fetcher=StaticFetcher())  # type: ignore[arg-type]

    assert snapshot.ticker == "MSFT"
    assert snapshot.source == "test"
    assert len(snapshot.bars) == 5
    assert snapshot.latest.volume == 1004


@pytest.mark.asyncio
async def test_market_snapshot_rejects_non_whitelisted_ticker() -> None:
    with pytest.raises(ValueError, match="whitelist"):
        await get_market_snapshot("FAKE", fetcher=FailingFetcher())  # type: ignore[arg-type]
