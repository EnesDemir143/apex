"""Shared LangGraph state for Apex analysis agents."""

from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """State passed between standalone LangGraph agent nodes."""

    ticker: str
    market_data: Any
    technical_analysis: dict[str, Any] | None
    fundamental_analysis: dict[str, Any] | None
    risk_assessment: dict[str, Any] | None
    portfolio_decision: dict[str, Any] | None
    errors: list[str]
    compaction_applied: bool
    usage: dict[str, Any]
