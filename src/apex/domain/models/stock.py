"""Stock domain model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Stock(BaseModel):
    """Lightweight domain representation of a stock."""

    id: int | None = None
    ticker: str
    name: str | None = None
    sector: str | None = None
    exchange: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
