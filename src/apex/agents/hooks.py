"""Security hooks for pre- and post-analysis validation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from apex.agents.state import AgentState
from apex.agents.tool_schemas import TradeDecisionInput
from apex.core.config import get_settings
from apex.core.constants import HOLD_CONFIDENCE_THRESHOLD, TICKERS_WHITELIST
from apex.services.cost_guard import BudgetLimiter

PROMPT_INJECTION_PATTERNS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "developer message",
    "system prompt",
    "reveal your instructions",
    "bypass",
    "jailbreak",
)


def pre_analysis_hook(state: AgentState) -> AgentState:
    """Block unsafe tickers, prompt injection attempts, and known budget overruns."""
    ticker = state["ticker"].upper()
    if ticker not in TICKERS_WHITELIST:
        raise ValueError(f"Ticker {ticker} is not whitelisted")

    injection_hits = _find_prompt_injection(state)
    if injection_hits:
        raise ValueError(f"Prompt injection pattern detected: {', '.join(injection_hits)}")

    _verify_budget_snapshot(state)
    return {**state, "ticker": ticker}


def post_analysis_hook(state: AgentState) -> AgentState:
    """Validate final output schema, confidence threshold, and instruction hierarchy."""
    decision = state.get("portfolio_decision")
    if not isinstance(decision, Mapping):
        raise ValueError("portfolio_decision is required before post-analysis validation")

    risk = state.get("risk_assessment")
    risk_score = float(risk.get("risk_score", 0.0)) if isinstance(risk, Mapping) else 0.0
    payload = TradeDecisionInput.model_validate({**decision, "risk_score": risk_score})
    if payload.confidence < HOLD_CONFIDENCE_THRESHOLD:
        raise ValueError(f"confidence validation failed: {payload.confidence} < {HOLD_CONFIDENCE_THRESHOLD}")

    reasoning_hits = _scan_text(payload.reasoning)
    if reasoning_hits:
        raise ValueError(f"Instruction hierarchy violation detected: {', '.join(reasoning_hits)}")

    return {**state, "portfolio_decision": payload.model_dump(mode="json")}


def _verify_budget_snapshot(state: AgentState) -> None:
    usage = state.get("usage", {})
    spent = float(usage.get("cost_usd", 0.0)) if isinstance(usage, Mapping) else 0.0
    # Reference the Phase 5 budget guard seam while keeping the synchronous hook lightweight.
    configured_limit = BudgetLimiter(daily_budget_usd=get_settings().llm_daily_budget_usd).daily_budget_usd
    if spent > configured_limit:
        raise ValueError(f"LLM budget exceeded before analysis: ${spent:.4f} > ${configured_limit:.4f}")


def _find_prompt_injection(value: Any) -> list[str]:
    hits: set[str] = set()
    for text in _iter_strings(value):
        hits.update(_scan_text(text))
    return sorted(hits)


def _scan_text(text: str) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in PROMPT_INJECTION_PATTERNS if pattern in lowered]


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from _iter_strings(nested)
    elif isinstance(value, Iterable) and not isinstance(value, bytes):
        for nested in value:
            yield from _iter_strings(nested)
