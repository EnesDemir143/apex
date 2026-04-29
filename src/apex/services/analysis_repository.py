"""Repository for analysis run persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex.infrastructure_layer.models import AnalysisRun


class AnalysisRepository:
    """CRUD operations for AnalysisRun ORM rows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        stock_id: int,
        final_signal: str | None = None,
        final_confidence: float | None = None,
        status: str = "completed",
        summary: dict[str, object] | None = None,
    ) -> AnalysisRun:
        """Create and flush an analysis run."""
        analysis = AnalysisRun(
            stock_id=stock_id,
            final_signal=final_signal,
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
