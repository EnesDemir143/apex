"""Repository for stock persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex.infrastructure_layer.models import Stock


class StockRepository:
    """CRUD operations for Stock ORM rows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_ticker(self, ticker: str) -> Stock | None:
        """Return a stock by ticker symbol."""
        result = await self.session.execute(select(Stock).where(Stock.ticker == ticker.upper()))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Stock]:
        """Return all stocks ordered by ticker."""
        result = await self.session.execute(select(Stock).order_by(Stock.ticker))
        return list(result.scalars().all())

    async def create(
        self,
        *,
        ticker: str,
        name: str | None = None,
        sector: str | None = None,
        exchange: str | None = None,
    ) -> Stock:
        """Create and flush a stock row."""
        stock = Stock(ticker=ticker.upper(), name=name, sector=sector, exchange=exchange)
        self.session.add(stock)
        await self.session.flush()
        return stock
