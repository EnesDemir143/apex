"""PredictionBandLog ORM model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apex.infrastructure_layer.models.base import Base

if TYPE_CHECKING:
    from apex.infrastructure_layer.models.analysis_run import AnalysisRun
    from apex.infrastructure_layer.models.stock import Stock


class PredictionBandLog(Base):
    __tablename__ = "prediction_band_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False
    )
    predicted_for: Mapped[date] = mapped_column(Date, nullable=False)
    band_upper: Mapped[float | None] = mapped_column(Numeric(18, 8))
    band_lower: Mapped[float | None] = mapped_column(Numeric(18, 8))
    band_mid: Mapped[float | None] = mapped_column(Numeric(18, 8))
    actual_close: Mapped[float | None] = mapped_column(Numeric(18, 8))
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stock: Mapped[Stock] = relationship(back_populates="prediction_bands")  # noqa: F821
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="prediction_bands")  # noqa: F821
