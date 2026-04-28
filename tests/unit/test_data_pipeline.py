"""Unit tests for data pipeline with VCR.py cassettes."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import vcr

from apex.domain.models.ohlcv import OHLCVBar
from apex.ingestion.market_calendar import get_nyse_trading_days, is_trading_day
from apex.ingestion.market_data_fetcher import MarketDataFetcher

CASSETTES_DIR = Path(__file__).parent.parent / "cassettes"
CASSETTES_DIR.mkdir(exist_ok=True)


def _make_bar(ticker: str, day: date, close: float = 150.0) -> OHLCVBar:
    return OHLCVBar(
        ticker=ticker,
        timestamp=datetime(day.year, day.month, day.day, tzinfo=UTC),
        open=Decimal(str(close - 1)),
        high=Decimal(str(close + 2)),
        low=Decimal(str(close - 2)),
        close=Decimal(str(close)),
        volume=1_000_000,
        source="alpaca",
    )


# ---------------------------------------------------------------------------
# Market calendar tests (no network, no DB)
# ---------------------------------------------------------------------------


def test_nyse_trading_days_excludes_weekend() -> None:
    """Saturday and Sunday should not appear in NYSE trading days."""
    days = get_nyse_trading_days(date(2024, 1, 1), date(2024, 1, 7))
    for d in days:
        assert d.weekday() < 5, f"{d} is a weekend but returned as trading day"


def test_nyse_trading_days_excludes_holiday() -> None:
    """New Year's Day 2024 (Jan 1) is a NYSE holiday."""
    days = get_nyse_trading_days(date(2024, 1, 1), date(2024, 1, 3))
    assert date(2024, 1, 1) not in days


def test_is_trading_day_known_trading_day() -> None:
    assert is_trading_day(date(2024, 1, 2)) is True  # First trading day of 2024


def test_is_trading_day_weekend() -> None:
    assert is_trading_day(date(2024, 1, 6)) is False  # Saturday


# ---------------------------------------------------------------------------
# MarketDataFetcher.fetch_bars — primary success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_bars_primary_success() -> None:
    bar = _make_bar("AAPL", date(2024, 1, 2))
    primary = AsyncMock()
    primary.name = "alpaca"
    primary.fetch_bars = AsyncMock(return_value=[bar])

    fetcher = MarketDataFetcher(primary=primary, fallback=AsyncMock())
    response = await fetcher.fetch_bars("AAPL", date(2024, 1, 2), date(2024, 1, 2))

    assert response.degraded is False
    assert response.source == "alpaca"
    assert len(response.bars) == 1


@pytest.mark.asyncio
async def test_fetch_bars_fallback_on_primary_failure() -> None:
    bar = _make_bar("AAPL", date(2024, 1, 2))
    primary = AsyncMock()
    primary.name = "alpaca"
    primary.fetch_bars = AsyncMock(side_effect=RuntimeError("API down"))

    fallback = AsyncMock()
    fallback.name = "yfinance"
    fallback.fetch_bars = AsyncMock(return_value=[bar])

    fetcher = MarketDataFetcher(primary=primary, fallback=fallback)
    response = await fetcher.fetch_bars("AAPL", date(2024, 1, 2), date(2024, 1, 2))

    assert response.degraded is True
    assert response.source == "yfinance"


# ---------------------------------------------------------------------------
# MarketDataFetcher.upsert_bars — idempotency
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_bars_idempotent() -> None:
    """Calling upsert_bars twice with the same data should not raise."""
    bars = [_make_bar("AAPL", date(2024, 1, 2))]

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = 1  # stock_id = 1
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    fetcher = MarketDataFetcher()

    # First upsert
    inserted1, _ = await fetcher.upsert_bars(mock_session, "AAPL", bars)
    # Second upsert (same data)
    inserted2, _ = await fetcher.upsert_bars(mock_session, "AAPL", bars)

    assert inserted1 == 1
    assert inserted2 == 1
    assert mock_session.commit.call_count == 2


@pytest.mark.asyncio
async def test_upsert_bars_empty_list() -> None:
    """Empty bar list returns (0, 0) without touching the DB."""
    mock_session = AsyncMock()
    fetcher = MarketDataFetcher()
    inserted, updated = await fetcher.upsert_bars(mock_session, "AAPL", [])
    assert inserted == 0
    assert updated == 0
    mock_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_bars_unknown_ticker_raises() -> None:
    """upsert_bars raises ValueError when ticker not in DB."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # not found
    mock_session.execute = AsyncMock(return_value=mock_result)

    fetcher = MarketDataFetcher()
    with pytest.raises(ValueError, match="Stock not found"):
        await fetcher.upsert_bars(mock_session, "UNKNOWN", [_make_bar("UNKNOWN", date(2024, 1, 2))])


# ---------------------------------------------------------------------------
# VCR cassette test — Alpaca API (recorded, replayed offline)
# ---------------------------------------------------------------------------


@vcr.use_cassette(
    str(CASSETTES_DIR / "alpaca_aapl_bars.yaml"),
    record_mode="none",
    allow_playback_repeats=True,
)
def test_alpaca_cassette_placeholder() -> None:
    """Placeholder: cassette will be recorded on first live run.

    To record: set record_mode='new_episodes' and provide real API keys.
    In CI this test is skipped if the cassette file doesn't exist.
    """
    cassette_path = CASSETTES_DIR / "alpaca_aapl_bars.yaml"
    if not cassette_path.exists():
        pytest.skip("Cassette not recorded yet — run with live API keys first")
