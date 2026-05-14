"""AnalysisRun ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apex.infrastructure_layer.models.base import Base

if TYPE_CHECKING:
    from apex.infrastructure_layer.models.agent_decision import AgentDecision
    from apex.infrastructure_layer.models.llm_usage_log import LLMUsageLog
    from apex.infrastructure_layer.models.prediction_band import PredictionBandLog
    from apex.infrastructure_layer.models.stock import Stock
    from apex.infrastructure_layer.models.trade import Trade


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    final_signal: Mapped[str | None] = mapped_column(String(10))  # BUY/SELL/HOLD
    final_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[float | None] = mapped_column(Numeric(18, 8))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    environment: Mapped[str] = mapped_column(String(20), nullable=False, default="sandbox")
    compaction_applied: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stock: Mapped[Stock] = relationship(back_populates="analysis_runs")  # noqa: F821
    agent_decisions: Mapped[list[AgentDecision]] = relationship(back_populates="analysis_run")  # noqa: F821
    trades: Mapped[list[Trade]] = relationship(back_populates="analysis_run")  # noqa: F821
    prediction_bands: Mapped[list[PredictionBandLog]] = relationship(back_populates="analysis_run")  # noqa: F821
    llm_usage_logs: Mapped[list[LLMUsageLog]] = relationship(back_populates="analysis_run")  # noqa: F821
