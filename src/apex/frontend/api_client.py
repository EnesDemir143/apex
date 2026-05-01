"""HTTP client for Apex FastAPI backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
import streamlit as st

BASE_URL = "http://localhost:8001"
_TIMEOUT = 30.0

# Company name lookup for whitelisted tickers
_TICKER_NAMES: dict[str, str] = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.",
    "TSLA": "Tesla Inc.",
    "SPY":  "SPDR S&P 500 ETF",
    "GOOGL": "Alphabet Inc.",
}


@st.cache_data(ttl=60)
def fetch_analysis(ticker: str) -> dict[str, Any] | None:
    """POST /api/v1/analyze/{ticker} and return the JSON result."""
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(f"{BASE_URL}/api/v1/analyze/{ticker.upper()}")
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]
    except httpx.HTTPError:
        return None


@st.cache_data(ttl=30)
def fetch_health() -> dict[str, Any]:
    """GET /health and return status dict."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{BASE_URL}/health")
            return resp.json()  # type: ignore[no-any-return]
    except httpx.HTTPError:
        return {"status": "unreachable"}


def clear_analysis_cache(ticker: str) -> None:
    """Invalidate cached analysis for a ticker."""
    fetch_analysis.clear()  # type: ignore[attr-defined]


@st.cache_data(ttl=300)
def fetch_ohlcv(ticker: str, days: int = 60) -> list[dict[str, Any]]:
    """GET /api/v1/ohlcv/{ticker} and return list of bar dicts."""
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(f"{BASE_URL}/api/v1/ohlcv/{ticker.upper()}", params={"days": days})
            resp.raise_for_status()
            data = resp.json()
            return data.get("bars", [])  # type: ignore[no-any-return]
    except httpx.HTTPError:
        return []


def _confidence_to_risk(confidence: float) -> str:
    if confidence >= 0.7:
        return "Low"
    if confidence >= 0.5:
        return "Medium"
    return "High"


def _agent_outputs_to_agreement(agent_outputs: dict[str, Any] | None) -> str:
    if not agent_outputs:
        return "?/4"
    # Count agents that produced output (non-null)
    count = sum(1 for v in agent_outputs.values() if v)
    return f"{count}/4"


@st.cache_data(ttl=300)
def fetch_all_signals(tickers: tuple[str, ...]) -> list[dict[str, Any]]:
    """Call fetch_analysis for each ticker; return list of signal row dicts.

    Shape matches TOP_SIGNALS / ALL_SIGNALS in mock_data:
    {symbol, name, signal, confidence, risk, agreement, last_analysis}
    Returns empty list on total failure; skips individual failed tickers.
    """
    rows: list[dict[str, Any]] = []
    for ticker in tickers:
        result = fetch_analysis(ticker)
        if result is None:
            continue
        agent_outputs: dict[str, Any] | None = (
            result.get("summary", {}).get("agent_outputs") if result.get("summary") else None
        )
        confidence: float = result.get("confidence", 0.0) or 0.0
        rows.append({
            "symbol":        ticker,
            "name":          _TICKER_NAMES.get(ticker, ticker),
            "signal":        result.get("signal", "HOLD"),
            "confidence":    confidence,
            "risk":          _confidence_to_risk(confidence),
            "agreement":     _agent_outputs_to_agreement(agent_outputs),
            "last_analysis": datetime.now().strftime("%H:%M"),
        })
    return rows


@st.cache_data(ttl=30)
def fetch_observability() -> dict[str, Any]:
    """Call /health and return dict matching OBSERVABILITY shape.

    Falls back to a default dict with 'unreachable' status on error.
    """
    health = fetch_health()
    status = health.get("status", "unreachable")
    return {
        "api_latency_ms":   None,          # not available from /health
        "cache_hit_rate":   None,
        "llm_cost_today":   None,
        "agent_runs_today": None,
        "failed_runs":      None,
        "data_provider":    "Healthy" if status == "ok" else status.capitalize(),
        "_health_raw":      health,
    }
