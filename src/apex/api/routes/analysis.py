"""Analysis API routes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apex.agents.workflow import create_workflow, workflow_run_config
from apex.core.constants import FALLBACK_CONFIDENCE, TICKERS_WHITELIST
from apex.domain.models import AnalysisResult, OHLCVBar
from apex.domain.value_objects import Signal

router = APIRouter(prefix="/api/v1", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    """Optional request body for analysis tuning."""

    horizon_days: int = Field(default=5, ge=1, le=365)


@router.post("/analyze/{ticker}", response_model=AnalysisResult)
async def analyze_ticker(ticker: str, request: AnalyzeRequest | None = None) -> AnalysisResult:
    """Run the Apex agent workflow and return a structured analysis result."""
    del request
    normalized = ticker.upper()
    if normalized not in TICKERS_WHITELIST:
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

    return AnalysisResult(
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
            "errors": final_state.get("errors", []),
        },
        total_tokens=int(usage.get("tokens_in", 0)) + int(usage.get("tokens_out", 0)),
        cost_usd=float(usage.get("cost_usd", 0.0)),
        status="completed" if not final_state.get("errors") else "degraded",
    )


def _default_market_data(ticker: str) -> list[OHLCVBar]:
    """Create deterministic local OHLCV bars for API smoke analysis."""
    start = datetime.now(UTC) - timedelta(days=40)
    bars: list[OHLCVBar] = []
    for idx in range(35):
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
