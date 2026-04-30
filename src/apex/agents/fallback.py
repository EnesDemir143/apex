"""Rule-based fallback decisions for degraded workflow paths."""

from __future__ import annotations

from typing import Any

from apex.agents.state import AgentState
from apex.domain.value_objects import Signal


def rule_based_fallback(state: AgentState) -> AgentState:
    """Return a conservative RSI-only decision with confidence 0.3."""
    rsi = _extract_rsi(state.get("technical_analysis"))
    if rsi is not None and rsi < 30:
        signal = Signal.BUY
    elif rsi is not None and rsi > 70:
        signal = Signal.SELL
    else:
        signal = Signal.HOLD

    return {
        "portfolio_decision": {
            "ticker": state["ticker"],
            "signal": signal.value,
            "confidence": 0.3,
            "reasoning": f"Rule-based fallback from RSI={rsi}",
            "source": "rule_based",
        }
    }


def _extract_rsi(payload: Any) -> float | None:
    if not isinstance(payload, dict):
        return None
    if "rsi" in payload:
        return _as_float(payload["rsi"])
    indicators = payload.get("indicators")
    if isinstance(indicators, dict):
        return _as_float(indicators.get("rsi"))
    return None


def _as_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None
