"""StockPrice ORM model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apex.infrastructure_layer.models.base import Base

if TYPE_CHECKING:
    from apex.infrastructure_layer.models.stock import Stock


class StockPrice(Base):
    __tablename__ = "stock_prices"
    __table_args__ = (UniqueConstraint("stock_id", "date", name="uq_stock_prices_stock_date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[float | None] = mapped_column(Numeric(18, 8))
    high: Mapped[float | None] = mapped_column(Numeric(18, 8))
    low: Mapped[float | None] = mapped_column(Numeric(18, 8))
    close: Mapped[float | None] = mapped_column(Numeric(18, 8))
    adj_close: Mapped[float | None] = mapped_column(Numeric(18, 8))
    volume: Mapped[float | None] = mapped_column(Numeric(24, 8))
    source: Mapped[str | None] = mapped_column(String(50))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stock: Mapped[Stock] = relationship(back_populates="prices")  # noqa: F821
