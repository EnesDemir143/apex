"""Alpaca primary market data provider using alpaca-py."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import structlog
from alpaca.data import StockHistoricalDataClient
from alpaca.data.models import BarSet
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from apex.core.config import settings
from apex.domain.models.ohlcv import OHLCVBar
from apex.ingestion.base_market_data_client import MarketDataClient

logger = structlog.get_logger(__name__)

_TIMEFRAME_MAP: dict[str, TimeFrame] = {
    "1D": TimeFrame.Day,
    "1H": TimeFrame.Hour,
    "1Min": TimeFrame(1, TimeFrameUnit.Minute),
}


class AlpacaClient(MarketDataClient):
    """Fetches OHLCV bars from Alpaca Markets using alpaca-py."""

    def __init__(self) -> None:
        self._client = StockHistoricalDataClient(
            api_key=settings.alpaca_api_key.get_secret_value(),
            secret_key=settings.alpaca_secret_key.get_secret_value(),
        )

    @property
    def name(self) -> str:
        return "alpaca"

    async def fetch_bars(
        self,
        ticker: str,
        start: date,
        end: date,
        timeframe: str = "1D",
    ) -> list[OHLCVBar]:
        tf = _TIMEFRAME_MAP.get(timeframe, TimeFrame.Day)
        request = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=tf,
            start=datetime(start.year, start.month, start.day, tzinfo=UTC),
            end=datetime(end.year, end.month, end.day, tzinfo=UTC),
        )
        try:
            result = self._client.get_stock_bars(request)
            bar_set = result if isinstance(result, BarSet) else BarSet({})
            bars = bar_set.data.get(ticker, [])
            return [
                OHLCVBar(
                    ticker=ticker,
                    timestamp=b.timestamp,
                    open=Decimal(str(b.open)),
                    high=Decimal(str(b.high)),
                    low=Decimal(str(b.low)),
                    close=Decimal(str(b.close)),
                    volume=int(b.volume),
                    source="alpaca",
                )
                for b in bars
            ]
        except Exception as exc:
            logger.error("alpaca.fetch_bars.failed", ticker=ticker, error=str(exc))
            raise
