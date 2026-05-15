"""Local market snapshot service for the Apex TUI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from apex.agents.indicators import (
    calculate_bollinger_bands,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
)
from apex.core.constants import TICKERS_WHITELIST
from apex.domain.models.ohlcv import OHLCVBar
from apex.ingestion.market_data_fetcher import MarketDataFetcher
from apex.services.sanitizer import canonicalize_ticker


@dataclass(frozen=True)
class LatestOHLCV:
    """Latest OHLCV values for a ticker."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass(frozen=True)
class IndicatorSummary:
    """Compact indicator values for terminal display."""

    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    sma20: float
    sma50: float
    ema12: float
    ema26: float
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float


@dataclass(frozen=True)
class MarketSnapshot:
    """Recent bars plus latest price and indicator summaries."""

    ticker: str
    bars: list[OHLCVBar]
    latest: LatestOHLCV
    indicators: IndicatorSummary
    source: str


async def get_market_snapshot(
    ticker: str,
    *,
    days: int = 60,
    fetcher: MarketDataFetcher | None = None,
) -> MarketSnapshot:
    """Return recent OHLCV and indicators without using the LLM workflow."""
    canonical = canonicalize_ticker(ticker)
    if canonical not in TICKERS_WHITELIST:
        raise ValueError(f"Ticker {canonical!r} is not in the whitelist: {TICKERS_WHITELIST}")

    end = date.today()
    start = end - timedelta(days=days)
    source = "stub"
    try:
        response = await (fetcher or MarketDataFetcher()).fetch_bars(canonical, start, end)
        bars = list(response.bars)
        source = response.source
    except Exception:
        bars = _default_snapshot_bars(canonical)

    if not bars:
        bars = _default_snapshot_bars(canonical)
        source = "stub"

    return _snapshot_from_bars(canonical, bars[-days:], source=source)


def _default_snapshot_bars(ticker: str) -> list[OHLCVBar]:
    """Return deterministic OHLCV bars for offline/no-credential TUI use."""
    base = datetime(2026, 1, 2, tzinfo=UTC)
    bars: list[OHLCVBar] = []
    for i in range(60):
        close = Decimal("150") + Decimal(i) + (Decimal(i % 5) / Decimal("10"))
        bars.append(
            OHLCVBar(
                ticker=ticker,
                timestamp=base + timedelta(days=i),
                open=close - Decimal("1.0"),
                high=close + Decimal("1.5"),
                low=close - Decimal("2.0"),
                close=close,
                volume=1_000_000 + i * 2500,
                source="local_fallback",
            )
        )
    return bars


def _snapshot_from_bars(ticker: str, bars: list[OHLCVBar], *, source: str) -> MarketSnapshot:
    latest_bar = bars[-1]
    closes = [bar.close for bar in bars]
    macd = calculate_macd(closes)
    sma = calculate_sma(closes, periods=(20, 50))
    ema = calculate_ema(closes, spans=(12, 26))
    bands = calculate_bollinger_bands(closes)
    indicators = IndicatorSummary(
        rsi=_series_last(calculate_rsi(closes)),
        macd=_series_last(macd["macd"]),
        macd_signal=_series_last(macd["signal"]),
        macd_histogram=_series_last(macd["histogram"]),
        sma20=_series_last(sma[20]),
        sma50=_series_last(sma[50]),
        ema12=_series_last(ema[12]),
        ema26=_series_last(ema[26]),
        bollinger_upper=_series_last(bands["upper"]),
        bollinger_middle=_series_last(bands["middle"]),
        bollinger_lower=_series_last(bands["lower"]),
    )
    return MarketSnapshot(
        ticker=ticker,
        bars=bars,
        latest=LatestOHLCV(
            timestamp=latest_bar.timestamp,
            open=latest_bar.open,
            high=latest_bar.high,
            low=latest_bar.low,
            close=latest_bar.close,
            volume=latest_bar.volume,
        ),
        indicators=indicators,
        source=source,
    )


def _series_last(series: object) -> float:
    """Return the final scalar from a pandas Series-like object."""
    return float(getattr(series, "iloc")[-1])
