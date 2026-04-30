"""Shared LangGraph state for Apex analysis agents."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict


def merge_errors(left: list[str] | None, right: list[str] | None) -> list[str]:
    """Merge parallel agent error lists without dropping either branch."""
    return [*(left or []), *(right or [])]


def merge_usage(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    """Merge parallel LLM usage dictionaries emitted by agent nodes."""
    if not left:
        return dict(right or {})
    if not right:
        return dict(left)

    merged = dict(left)
    merged["turns"] = [*left.get("turns", []), *right.get("turns", [])]
    for key in ("tokens_in", "tokens_out"):
        merged[key] = int(left.get(key, 0)) + int(right.get(key, 0))
    merged["cost_usd"] = float(left.get("cost_usd", 0.0)) + float(right.get("cost_usd", 0.0))
    return merged


def merge_compaction(left: bool | None, right: bool | None) -> bool:
    """Keep compaction marked once any workflow branch applies it."""
    return bool(left) or bool(right)


class AgentState(TypedDict, total=False):
    """State passed between standalone LangGraph agent nodes."""

    ticker: str
    market_data: Any
    technical_analysis: dict[str, Any] | None
    fundamental_analysis: dict[str, Any] | None
    risk_assessment: dict[str, Any] | None
    portfolio_decision: dict[str, Any] | None
    errors: Annotated[list[str], merge_errors]
    compaction_applied: Annotated[bool, merge_compaction]
    usage: Annotated[dict[str, Any], merge_usage]
