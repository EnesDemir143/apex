"""Seed 5 stock records into the database. Idempotent via upsert."""

from __future__ import annotations

import asyncio

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from apex.core.config import settings
from apex.infrastructure_layer.models.stock import Stock

STOCKS = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "exchange": "NASDAQ"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical", "exchange": "NASDAQ"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "exchange": "NASDAQ"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "exchange": "NASDAQ"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "exchange": "NASDAQ"},
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    async with AsyncSession(engine) as session:
        stmt = insert(Stock).values(STOCKS)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker"],
            set_={"name": stmt.excluded.name, "sector": stmt.excluded.sector, "exchange": stmt.excluded.exchange},
        )
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(text("SELECT ticker FROM stocks ORDER BY ticker"))
        tickers = [row[0] for row in result]
        print(f"Seeded stocks: {tickers}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
