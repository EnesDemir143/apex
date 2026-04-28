"""MarketDataFetcher orchestrates primary and fallback data providers."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from apex.domain.models.ohlcv import OHLCVBar, OHLCVResponse
from apex.infrastructure_layer.models.stock import Stock
from apex.infrastructure_layer.models.stock_price import StockPrice
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

    async def upsert_bars(
        self,
        session: AsyncSession,
        ticker: str,
        bars: list[OHLCVBar],
    ) -> tuple[int, int]:
        """Upsert OHLCV bars into stock_prices. Returns (inserted, updated)."""
        if not bars:
            return 0, 0

        # Resolve stock_id
        result = await session.execute(select(Stock.id).where(Stock.ticker == ticker))
        stock_id = result.scalar_one_or_none()
        if stock_id is None:
            raise ValueError(f"Stock not found: {ticker}")

        rows = [
            {
                "stock_id": stock_id,
                "date": bar.timestamp.date(),
                "open": Decimal(str(bar.open)),
                "high": Decimal(str(bar.high)),
                "low": Decimal(str(bar.low)),
                "close": Decimal(str(bar.close)),
                "adj_close": Decimal(str(bar.close)),  # adj_close = close unless provider supplies it
                "volume": Decimal(str(bar.volume)),
                "source": bar.source,
            }
            for bar in bars
        ]

        stmt = insert(StockPrice).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_stock_prices_stock_date",
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "adj_close": stmt.excluded.adj_close,
                "volume": stmt.excluded.volume,
                "source": stmt.excluded.source,
            },
        )
        await session.execute(stmt)
        await session.commit()

        inserted = len(rows)
        return inserted, 0
