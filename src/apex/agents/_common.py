"""Shared helpers for standalone agent nodes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from langchain_core.runnables import RunnableConfig

from apex.agents.state import AgentState
from apex.domain.value_objects import Signal
from apex.services.llm_client import LLMResponse


def append_error(state: AgentState, message: str) -> AgentState:
    """Return a partial state update with an appended error message."""
    return {"errors": [*state.get("errors", []), message]}


def latest_value(values: Any) -> float | None:
    """Return the last scalar value from a pandas-like series or list."""
    if hasattr(values, "iloc"):
        value = values.iloc[-1]
    elif isinstance(values, list | tuple):
        value = values[-1] if values else None
    else:
        value = values
    return None if value is None else float(value)


def llm_trace_config(agent_name: str, ticker: str) -> RunnableConfig:
    """Build LangSmith trace metadata for a single agent invocation."""
    return {"run_name": agent_name, "metadata": {"ticker": ticker, "agent": agent_name}}


def signal_from_text(text: str, default: Signal = Signal.HOLD) -> Signal:
    """Extract a trading signal from free-form LLM text."""
    normalized = text.upper()
    for signal in Signal:
        if signal.value in normalized:
            return signal
    return default


def confidence_from_text(text: str, default: float = 0.5) -> float:
    """Extract a conservative confidence value from free-form LLM text."""
    tokens = text.replace("%", " ").replace(",", " ").split()
    for token in tokens:
        try:
            value = float(token)
        except ValueError:
            continue
        if 0.0 <= value <= 1.0:
            return value
        if 1.0 < value <= 100.0:
            return value / 100.0
    return default


def usage_from_response(agent_name: str, response: LLMResponse) -> dict[str, Any]:
    """Convert a normalized LLM response into usage metadata."""
    return {
        "agent_name": agent_name,
        "tokens_in": response.input_tokens,
        "tokens_out": response.output_tokens,
        "cost_usd": response.cost_usd,
    }


def merge_usage(state: AgentState, agent_name: str, response: LLMResponse) -> dict[str, Any]:
    """Append one LLM usage entry to the state's usage dictionary."""
    usage = dict(state.get("usage", {}))
    turns = list(usage.get("turns", []))
    turns.append(usage_from_response(agent_name, response))
    usage["turns"] = turns
    usage["tokens_in"] = int(usage.get("tokens_in", 0)) + response.input_tokens
    usage["tokens_out"] = int(usage.get("tokens_out", 0)) + response.output_tokens
    usage["cost_usd"] = float(usage.get("cost_usd", 0.0)) + response.cost_usd
    return usage


def decision_from_parts(
    *,
    ticker: str,
    signal: Signal,
    confidence: float,
    reasoning: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a normalized decision payload."""
    payload: dict[str, Any] = {
        "ticker": ticker,
        "signal": signal.value,
        "confidence": max(0.0, min(1.0, confidence)),
        "reasoning": reasoning,
    }
    if extra:
        payload.update(extra)
    return payload
