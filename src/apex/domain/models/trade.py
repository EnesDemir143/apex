"""Trade domain model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from apex.domain.value_objects import Signal


class Trade(BaseModel):
    """Domain representation of a trade record."""

    id: int | None = None
    ticker: str
    signal: Signal
    confidence: float | None = None
    entry_price: Decimal | None = None
    exit_price: Decimal | None = None
    pnl: Decimal | None = None
    status: str = "proposed"
    analysis_run_id: UUID | None = None
    created_at: datetime | None = None
