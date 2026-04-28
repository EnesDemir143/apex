"""Abstract base class for market data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from apex.domain.models.ohlcv import OHLCVBar


class MarketDataClient(ABC):
    """Abstract interface for fetching OHLCV market data."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g. 'alpaca', 'yfinance')."""

    @abstractmethod
    async def fetch_bars(
        self,
        ticker: str,
        start: date,
        end: date,
        timeframe: str = "1D",
    ) -> list[OHLCVBar]:
        """Fetch OHLCV bars for a ticker over the given date range."""
