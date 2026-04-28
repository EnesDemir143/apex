"""Stock ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apex.infrastructure_layer.models.base import Base

if TYPE_CHECKING:
    from apex.infrastructure_layer.models.analysis_run import AnalysisRun
    from apex.infrastructure_layer.models.embedding import Embedding
    from apex.infrastructure_layer.models.prediction_band import PredictionBandLog
    from apex.infrastructure_layer.models.stock_price import StockPrice
    from apex.infrastructure_layer.models.trade import Trade


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(100))
    exchange: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    prices: Mapped[list[StockPrice]] = relationship(back_populates="stock")  # noqa: F821
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(back_populates="stock")  # noqa: F821
    embeddings: Mapped[list[Embedding]] = relationship(back_populates="stock")  # noqa: F821
    trades: Mapped[list[Trade]] = relationship(back_populates="stock")  # noqa: F821
    prediction_bands: Mapped[list[PredictionBandLog]] = relationship(back_populates="stock")  # noqa: F821
