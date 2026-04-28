"""yfinance fallback market data provider."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import structlog
import yfinance as yf

from apex.domain.models.ohlcv import OHLCVBar
from apex.ingestion.base_market_data_client import MarketDataClient

logger = structlog.get_logger(__name__)


class YFinanceClient(MarketDataClient):
    """Fetches OHLCV bars from Yahoo Finance as a fallback provider."""

    @property
    def name(self) -> str:
        return "yfinance"

    async def fetch_bars(
        self,
        ticker: str,
        start: date,
        end: date,
        timeframe: str = "1D",  # noqa: ARG002
    ) -> list[OHLCVBar]:
        logger.warning("yfinance.fallback.activated", ticker=ticker)
        df = yf.download(
            ticker,
            start=start.isoformat(),
            end=end.isoformat(),
            progress=False,
            auto_adjust=True,
        )
        if df.empty:
            return []

        bars: list[OHLCVBar] = []
        for ts, row in df.iterrows():
            bars.append(
                OHLCVBar(
                    ticker=ticker,
                    timestamp=ts.to_pydatetime(),
                    open=Decimal(str(row["Open"])),
                    high=Decimal(str(row["High"])),
                    low=Decimal(str(row["Low"])),
                    close=Decimal(str(row["Close"])),
                    volume=int(row["Volume"]),
                    source="yfinance",
                )
            )
        return bars
