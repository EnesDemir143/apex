"""Repository for analysis run persistence operations.

v1 scope: prediction and analysis only — no trade execution.
Buy/sell execution is planned for v2 (see BET5 backlog: TRADE-01).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex.infrastructure_layer.models import AnalysisRun


class AnalysisRepository:
    """Persistence operations for AnalysisRun records.

    Stores prediction results (BUY/SELL/HOLD signals with confidence scores)
    produced by the agent pipeline. Does not execute or record actual trades —
    that is out of scope for v1.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        stock_id: int,
        predicted_signal: str | None = None,
        final_confidence: float | None = None,
        status: str = "completed",
        summary: dict[str, object] | None = None,
    ) -> AnalysisRun:
        """Persist a completed analysis/prediction run.

        Args:
            stock_id: FK to the stock being analysed.
            predicted_signal: Agent pipeline output — BUY/SELL/HOLD prediction.
                              This is a prediction, not a trade order.
            final_confidence: Confidence score [0, 1] for the predicted signal.
            status: Run status (completed, failed, degraded).
            summary: Optional JSON blob with per-agent details.
        """
        analysis = AnalysisRun(
            stock_id=stock_id,
            final_signal=predicted_signal,  # ORM column kept as-is; semantics: prediction
            final_confidence=final_confidence,
            status=status,
            summary=summary,
        )
        self.session.add(analysis)
        await self.session.flush()
        return analysis

    async def get_by_stock(self, stock_id: int) -> list[AnalysisRun]:
        """Return analysis runs for a stock, newest first."""
        result = await self.session.execute(
            select(AnalysisRun).where(AnalysisRun.stock_id == stock_id).order_by(AnalysisRun.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest(self, stock_id: int) -> AnalysisRun | None:
        """Return the newest analysis run for a stock."""
        result = await self.session.execute(
            select(AnalysisRun).where(AnalysisRun.stock_id == stock_id).order_by(AnalysisRun.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get(self, analysis_id: UUID) -> AnalysisRun | None:
        """Return an analysis run by ID."""
        return await self.session.get(AnalysisRun, analysis_id)
