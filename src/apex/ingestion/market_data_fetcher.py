"""MarketDataFetcher orchestrates primary and fallback data providers."""

from __future__ import annotations

from datetime import date

import structlog

from apex.domain.models.ohlcv import OHLCVResponse
from apex.ingestion.alpaca_client import AlpacaClient
from apex.ingestion.base_market_data_client import MarketDataClient
from apex.ingestion.yfinance_client import YFinanceClient

logger = structlog.get_logger(__name__)


class MarketDataFetcher:
    """Orchestrates market data retrieval with automatic failover."""

    def __init__(
        self,
        primary: MarketDataClient | None = None,
        fallback: MarketDataClient | None = None,
    ) -> None:
        self._primary = primary or AlpacaClient()
        self._fallback = fallback or YFinanceClient()

    async def fetch_bars(
        self,
        ticker: str,
        start: date,
        end: date,
        timeframe: str = "1D",
    ) -> OHLCVResponse:
        """Fetch bars from primary; fall back to secondary on failure."""
        try:
            bars = await self._primary.fetch_bars(ticker, start, end, timeframe)
            return OHLCVResponse(bars=bars, ticker=ticker, source=self._primary.name, degraded=False)
        except Exception as exc:
            logger.warning(
                "market_data.primary_failed.switching_fallback",
                primary=self._primary.name,
                fallback=self._fallback.name,
                ticker=ticker,
                error=str(exc),
            )
            bars = await self._fallback.fetch_bars(ticker, start, end, timeframe)
            return OHLCVResponse(bars=bars, ticker=ticker, source=self._fallback.name, degraded=True)
