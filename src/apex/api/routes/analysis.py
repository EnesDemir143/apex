"""Analysis API routes."""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from apex.core.constants import FALLBACK_CONFIDENCE, TICKERS_WHITELIST
from apex.domain.models import AnalysisResult
from apex.domain.value_objects import Signal

router = APIRouter(prefix="/api/v1", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    """Optional request body for analysis tuning."""

    horizon_days: int = Field(default=5, ge=1, le=365)


@router.post("/analyze/{ticker}", response_model=AnalysisResult)
async def analyze_ticker(ticker: str, request: AnalyzeRequest | None = None) -> AnalysisResult:
    """Return a stub analysis result for a ticker."""
    del request
    normalized = ticker.upper()
    signal = Signal.HOLD if normalized in TICKERS_WHITELIST else Signal.SELL
    return AnalysisResult(
        ticker=normalized,
        signal=signal,
        confidence=FALLBACK_CONFIDENCE,
        summary={"status": "stub", "reason": "Phase 5 route wiring; agents arrive in Phase 6"},
        status="stub",
    )
