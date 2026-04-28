"""Integration tests for market data client imports and OHLCV model."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from apex.domain.models.ohlcv import OHLCVBar, OHLCVResponse
from apex.ingestion.base_market_data_client import MarketDataClient


def test_ohlcv_bar_valid() -> None:
    """OHLCVBar accepts valid data."""
    bar = OHLCVBar(
        ticker="AAPL",
        timestamp=datetime(2024, 1, 2, tzinfo=UTC),
        open=Decimal("185.00"),
        high=Decimal("187.50"),
        low=Decimal("184.00"),
        close=Decimal("186.00"),
        volume=1_000_000,
    )
    assert bar.ticker == "AAPL"
    assert bar.source == "alpaca"


def test_ohlcv_bar_rejects_high_lt_low() -> None:
    """OHLCVBar raises ValidationError when high < low."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OHLCVBar(
            ticker="AAPL",
            timestamp=datetime(2024, 1, 2, tzinfo=UTC),
            open=Decimal("185.00"),
            high=Decimal("183.00"),  # high < low — invalid
            low=Decimal("184.00"),
            close=Decimal("186.00"),
            volume=100,
        )


def test_ohlcv_bar_rejects_negative_close() -> None:
    """OHLCVBar raises ValidationError when close <= 0."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OHLCVBar(
            ticker="AAPL",
            timestamp=datetime(2024, 1, 2, tzinfo=UTC),
            open=Decimal("185.00"),
            high=Decimal("187.00"),
            low=Decimal("184.00"),
            close=Decimal("-1.00"),
            volume=100,
        )


def test_market_data_client_is_abstract() -> None:
    """MarketDataClient cannot be instantiated directly."""
    with pytest.raises(TypeError):
        MarketDataClient()  # type: ignore[abstract]


def test_ohlcv_response_degraded_flag() -> None:
    """OHLCVResponse carries degraded flag correctly."""
    resp = OHLCVResponse(bars=[], ticker="AAPL", source="yfinance", degraded=True)
    assert resp.degraded is True
