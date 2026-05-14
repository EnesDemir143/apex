"""Server-independent local analysis service for Apex CLI/TUI."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from apex.agents.state import AgentState
from apex.agents.workflow import analyze_with_workflow, analyze_with_workflow_streaming
from apex.core.constants import TICKERS_WHITELIST
from apex.reports.writer import ReportWriter
from apex.services.history_store import HistoryStore, _compute_request_hash
from apex.services.sanitizer import canonicalize_ticker


def _default_market_data(ticker: str) -> list[Any]:
    """Return minimal deterministic OHLCV bars when no live data is available."""
    from datetime import timedelta
    from decimal import Decimal

    from apex.domain.models.ohlcv import OHLCVBar

    base = datetime(2026, 1, 2, tzinfo=UTC)
    return [
        OHLCVBar(
            ticker=ticker,
            timestamp=base + timedelta(days=i),
            open=Decimal("150") + Decimal(i),
            high=Decimal("152") + Decimal(i),
            low=Decimal("149") + Decimal(i),
            close=Decimal("151") + Decimal(i),
            volume=1_000_000 + i * 1000,
            source="local_fallback",
        )
        for i in range(80)
    ]


async def _fetch_market_data(ticker: str) -> list[Any]:
    """Attempt live fetch; fall back to deterministic stubs on any error."""
    from datetime import timedelta

    from apex.ingestion.market_data_fetcher import MarketDataFetcher

    end = date.today()
    start = end - timedelta(days=120)
    try:
        fetcher = MarketDataFetcher()
        response = await fetcher.fetch_bars(ticker, start, end)
        return list(response.bars)
    except Exception:
        return _default_market_data(ticker)


def _validate_analysis_date(analysis_date: date | str | None) -> date:
    """Normalize and validate as-of date; reject future dates."""
    today = date.today()
    if analysis_date is None:
        return today
    if isinstance(analysis_date, str):
        parsed = date.fromisoformat(analysis_date)
    else:
        parsed = analysis_date
    if parsed > today:
        raise ValueError(f"analysis_date {parsed} is in the future")
    return parsed


def _build_enabled_agents(agent_instructions: dict[str, str] | None) -> list[str]:
    default_agents = ["technical_agent", "fundamental_agent", "risk_agent", "portfolio_manager"]
    if not agent_instructions:
        return default_agents
    return sorted(agent_instructions.keys()) if agent_instructions else default_agents


async def run_local_analysis(
    ticker: str,
    mode: str = "full",
    analysis_date: date | str | None = None,
    extra_instructions: str | None = None,
    agent_instructions: dict[str, str] | None = None,
    save_report: bool = False,
    force: bool = False,
    output_language: str = "English",
    quant_enabled: bool = False,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Run the LangGraph workflow locally without FastAPI/Postgres/Redis.

    Args:
        ticker: Stock ticker symbol (must be in TICKERS_WHITELIST).
        mode: Analysis mode — "full" (default) or "quick" (reserved for future use).
        analysis_date: As-of date for the analysis; defaults to today; future dates rejected.
        extra_instructions: Optional global prompt note surfaced to all agents.
        agent_instructions: Optional per-agent prompt notes, e.g. {"risk": "focus on VIX"}.
        output_language: Report language — "English" (default) or "Turkish".
        quant_enabled: Enable optional quant ML agent (requires trained models).
        progress: Optional callback called with agent label as each finishes.

    Returns:
        Dict with keys: ticker, signal, confidence, errors, usage, agent_outputs, analysis_date.
    """
    canonical = canonicalize_ticker(ticker)
    if canonical not in TICKERS_WHITELIST:
        raise ValueError(f"Ticker {canonical!r} is not in the whitelist: {TICKERS_WHITELIST}")

    as_of = _validate_analysis_date(analysis_date)
    as_of_str = as_of.isoformat()

    request_hash = _compute_request_hash(
        ticker=canonical,
        analysis_date=as_of_str,
        mode=mode,
        extra_instructions=extra_instructions,
        agent_instructions=agent_instructions,
        enabled_agents=_build_enabled_agents(agent_instructions),
    )

    history = HistoryStore()
    if not force and save_report:
        cached = history.find_by_hash(request_hash)
        if cached and cached.get("report_dir"):
            report_dir = Path(str(cached["report_dir"]))
            if report_dir.exists() and (report_dir / "complete_report.md").exists():
                return {
                    "ticker": canonical,
                    "signal": cached.get("signal", "HOLD"),
                    "confidence": cached.get("confidence", 0.0),
                    "errors": [],
                    "usage": {"cached": True, "request_hash": request_hash},
                    "agent_outputs": {},
                    "analysis_date": as_of_str,
                    "mode": mode,
                    "request_hash": request_hash,
                    "cached": True,
                    "report_path": str(report_dir),
                }

    market_data = await _fetch_market_data(canonical)

    state: AgentState = {
        "ticker": canonical,
        "market_data": market_data,
        "errors": [],
        "usage": {},
        "quant_enabled": quant_enabled,
    }

    if extra_instructions or agent_instructions:
        state["usage"] = {
            **state["usage"],
            "_extra_instructions": extra_instructions,
            "_agent_instructions": agent_instructions or {},
        }

    if progress:
        result = await analyze_with_workflow_streaming(state, progress=progress)
    else:
        result = await analyze_with_workflow(state)

    decision = result.get("portfolio_decision") or {}
    output = {
        "ticker": canonical,
        "signal": decision.get("signal", "HOLD"),
        "confidence": decision.get("confidence", 0.0),
        "errors": result.get("errors") or [],
        "usage": result.get("usage") or {},
        "agent_outputs": {
            "technical": result.get("technical_analysis"),
            "fundamental": result.get("fundamental_analysis"),
            "risk": result.get("risk_assessment"),
            "quant": result.get("quant_analysis"),
            "portfolio": decision,
        },
        "quant_analysis": result.get("quant_analysis"),
        "analysis_date": as_of_str,
        "mode": mode,
        "request_hash": request_hash,
        "cached": False,
        "language": output_language,
    }

    if save_report:
        writer = ReportWriter()
        report_dir = writer.save(result=output, state=dict(result), language=output_language)
        history.append(output, report_dir=str(report_dir))
        output["report_path"] = str(report_dir)

    return output


def run_local_analysis_sync(
    ticker: str,
    mode: str = "full",
    analysis_date: date | str | None = None,
    extra_instructions: str | None = None,
    agent_instructions: dict[str, str] | None = None,
    save_report: bool = False,
    force: bool = False,
    output_language: str = "English",
    quant_enabled: bool = False,
) -> dict[str, Any]:
    """Synchronous wrapper around run_local_analysis for CLI use."""
    return asyncio.run(
        run_local_analysis(
            ticker,
            mode=mode,
            analysis_date=analysis_date,
            extra_instructions=extra_instructions,
            agent_instructions=agent_instructions,
            save_report=save_report,
            force=force,
            output_language=output_language,
            quant_enabled=quant_enabled,
        )
    )
