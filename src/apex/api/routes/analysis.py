"""Analysis API routes."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apex.agents.workflow import create_workflow, workflow_run_config
from apex.core.constants import FALLBACK_CONFIDENCE, TICKERS_WHITELIST
from apex.domain.models import AnalysisResult, OHLCVBar, OHLCVResponse
from apex.domain.value_objects import Signal
from apex.infrastructure_layer.database import get_db_session
from apex.infrastructure_layer.models.stock import Stock
from apex.infrastructure_layer.models.stock_price import StockPrice

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
async def get_ohlcv(
    ticker: str,
    days: int = 60,
    session: AsyncSession = Depends(get_db_session),
) -> OHLCVResponse:
    """Return OHLCV bars for a ticker — real DB rows when available, synthetic fallback otherwise."""
    normalized = ticker.upper()
    logger.info("ohlcv.request", ticker=normalized, days=days)

    try:
        bars = await _db_market_data(session, normalized, days=min(days, 365))
        if bars:
            logger.info("ohlcv.response", ticker=normalized, bar_count=len(bars), source="db")
            return OHLCVResponse(ticker=normalized, bars=bars, source="db")
    except Exception as exc:
        logger.warning("ohlcv.db_error", ticker=normalized, error=str(exc))

    bars = _default_market_data(normalized, days=min(days, 365))
    logger.info("ohlcv.response", ticker=normalized, bar_count=len(bars), source="synthetic")
    return OHLCVResponse(ticker=normalized, bars=bars, source="synthetic")


async def _db_market_data(session: AsyncSession, ticker: str, days: int) -> list[OHLCVBar]:
    """Query stock_prices for the most recent *days* bars."""
    cutoff = date.today() - timedelta(days=days)
    stmt = (
        select(StockPrice)
        .join(Stock, StockPrice.stock_id == Stock.id)
        .where(Stock.ticker == ticker, StockPrice.date >= cutoff)
        .order_by(StockPrice.date.asc())
        .limit(days)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()
    return [
        OHLCVBar(
            ticker=ticker,
            timestamp=datetime(row.date.year, row.date.month, row.date.day, tzinfo=UTC),
            open=Decimal(str(row.open or 0)),
            high=Decimal(str(row.high or 0)),
            low=Decimal(str(row.low or 0)),
            close=Decimal(str(row.close or 0)),
            volume=int(row.volume or 0),
            source=row.source or "db",
        )
        for row in rows
    ]


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
