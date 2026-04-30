"""Context compaction helpers for agent workflow state."""

from __future__ import annotations

from typing import Any, cast

from apex.agents.state import AgentState


def compact_agent_context(state: AgentState, token_budget: int = 4096) -> AgentState:
    """Compact verbose agent outputs once rough token usage exceeds 80% of budget."""
    rough_tokens = _rough_token_count(state)
    if rough_tokens <= int(token_budget * 0.8):
        return state

    compacted: dict[str, Any] = dict(state)
    for key in ("technical_analysis", "fundamental_analysis", "risk_assessment"):
        payload = compacted.get(key)
        if isinstance(payload, dict):
            compacted[key] = _compact_payload(payload)
    compacted["compaction_applied"] = True
    return cast(AgentState, compacted)


def _compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    keep = {key: payload[key] for key in ("ticker", "signal", "confidence", "risk_score", "metrics") if key in payload}
    reasoning = payload.get("reasoning") or payload.get("risk_factors")
    if reasoning is not None:
        text = str(reasoning)
        keep["reasoning"] = text[:400] + ("..." if len(text) > 400 else "")
    return keep


def _rough_token_count(value: Any) -> int:
    return max(1, len(str(value)) // 4)
