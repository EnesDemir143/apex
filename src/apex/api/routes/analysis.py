"""Analysis API routes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import structlog
from fastapi import APIRouter
from pydantic import BaseModel, Field

from apex.agents.workflow import create_workflow, workflow_run_config
from apex.core.constants import FALLBACK_CONFIDENCE, TICKERS_WHITELIST
from apex.domain.models import AnalysisResult, OHLCVBar, OHLCVResponse
from apex.domain.value_objects import Signal

router = APIRouter(prefix="/api/v1", tags=["analysis"])
logger = structlog.get_logger(__name__)


class AnalyzeRequest(BaseModel):
    """Optional request body for analysis tuning."""

    horizon_days: int = Field(default=5, ge=1, le=365)


@router.post("/analyze/{ticker}", response_model=AnalysisResult)
async def analyze_ticker(ticker: str, request: AnalyzeRequest | None = None) -> AnalysisResult:
    """Run the Apex agent workflow and return a structured analysis result."""
    del request
    normalized = ticker.upper()
    logger.info("analysis.request", ticker=normalized)

    if normalized not in TICKERS_WHITELIST:
        logger.warning("analysis.rejected", ticker=normalized, reason="not_whitelisted")
        return AnalysisResult(
            ticker=normalized,
            signal=Signal.SELL,
            confidence=FALLBACK_CONFIDENCE,
            summary={"status": "rejected", "reason": "ticker not whitelisted"},
            status="rejected",
        )

    initial_state = {"ticker": normalized, "market_data": _default_market_data(normalized), "errors": [], "usage": {}}
    workflow = create_workflow()
    final_state: dict[str, Any] = await workflow.ainvoke(initial_state, config=workflow_run_config(normalized))
    decision = final_state.get("portfolio_decision") or {}
    usage = final_state.get("usage", {})
    errors = final_state.get("errors", [])

    result = AnalysisResult(
        ticker=normalized,
        signal=Signal(str(decision.get("signal", Signal.HOLD.value))),
        confidence=float(decision.get("confidence", FALLBACK_CONFIDENCE)),
        summary={
            "usage_summary": usage,
            "agent_outputs": {
                "technical": final_state.get("technical_analysis"),
                "fundamental": final_state.get("fundamental_analysis"),
                "risk": final_state.get("risk_assessment"),
                "portfolio": decision,
            },
            "errors": errors,
        },
        total_tokens=int(usage.get("tokens_in", 0)) + int(usage.get("tokens_out", 0)),
        cost_usd=float(usage.get("cost_usd", 0.0)),
        status="completed" if not errors else "degraded",
    )
    logger.info(
        "analysis.complete",
        ticker=normalized,
        signal=result.signal,
        confidence=result.confidence,
        total_tokens=result.total_tokens,
        cost_usd=result.cost_usd,
        status=result.status,
    )
    return result


@router.get("/ohlcv/{ticker}", response_model=OHLCVResponse)
async def get_ohlcv(ticker: str, days: int = 60) -> OHLCVResponse:
    """Return OHLCV bars for a ticker (synthetic when DB unavailable)."""
    normalized = ticker.upper()
    logger.info("ohlcv.request", ticker=normalized, days=days)
    bars = _default_market_data(normalized, days=min(days, 365))
    logger.info("ohlcv.response", ticker=normalized, bar_count=len(bars))
    return OHLCVResponse(ticker=normalized, bars=bars, source="synthetic")


def _default_market_data(ticker: str, days: int = 35) -> list[OHLCVBar]:
    """Create deterministic local OHLCV bars for API smoke analysis."""
    start = datetime.now(UTC) - timedelta(days=days + 5)
    bars: list[OHLCVBar] = []
    for idx in range(days):
        close = Decimal("100") + Decimal(idx) / Decimal("2")
        bars.append(
            OHLCVBar(
                ticker=ticker,
                timestamp=start + timedelta(days=idx),
                open=close - Decimal("0.5"),
                high=close + Decimal("1.0"),
                low=close - Decimal("1.0"),
                close=close,
                volume=1_000_000 + idx,
                source="synthetic",
            )
        )
    return bars
