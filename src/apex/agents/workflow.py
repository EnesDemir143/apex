"""LangGraph workflow assembly for Apex multi-agent analysis."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any, cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from apex.agents.compaction import compact_agent_context
from apex.agents.fundamental import fundamental_agent
from apex.agents.hooks import post_analysis_hook, pre_analysis_hook
from apex.agents.portfolio_manager import portfolio_manager
from apex.agents.quant import quant_agent
from apex.agents.risk import risk_agent
from apex.agents.state import AgentState
from apex.agents.technical import technical_agent
from apex.infrastructure_layer.models import AgentDecision
from apex.services.analysis_repository import AnalysisRepository

WorkflowConfig = RunnableConfig

MAX_AGENT_ITERATIONS = 25
WORKFLOW_TIMEOUT_SECONDS = 120


def _build_graph() -> Any:
    graph = StateGraph(AgentState)
    graph.add_node("pre_hook", pre_analysis_hook)
    graph.add_node("technical", technical_agent)
    graph.add_node("fundamental", fundamental_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("quant", quant_agent)
    graph.add_node("compact_context", compact_agent_context)
    graph.add_node("portfolio_manager", portfolio_manager)
    graph.add_node("post_hook", post_analysis_hook)

    graph.set_entry_point("pre_hook")
    graph.add_edge("pre_hook", "technical")
    graph.add_edge("pre_hook", "fundamental")
    graph.add_edge("pre_hook", "risk")
    graph.add_edge("pre_hook", "quant")
    graph.add_edge("technical", "compact_context")
    graph.add_edge("fundamental", "compact_context")
    graph.add_edge("risk", "compact_context")
    graph.add_edge("quant", "compact_context")
    graph.add_edge("compact_context", "portfolio_manager")
    graph.add_edge("portfolio_manager", "post_hook")
    graph.add_edge("post_hook", END)
    return graph


def create_workflow() -> Any:
    """Create the compiled LangGraph StateGraph for one analysis run.

    Execution order is pre-hook -> parallel technical/fundamental/risk branches ->
    context compaction -> portfolio manager synthesis -> post-hook validation. The
    final post-hook position keeps the existing validation contract, which requires
    a portfolio_decision.
    """
    return _build_graph().compile()


def create_workflow_with_checkpointer(checkpointer: Any) -> Any:
    """Create the workflow compiled with a LangGraph checkpointer."""
    return _build_graph().compile(checkpointer=checkpointer)


def workflow_run_config(ticker: str) -> WorkflowConfig:
    """Return LangSmith config and max-iteration guard for an end-to-end workflow trace."""
    normalized = ticker.upper()
    return {
        "run_name": f"analyze_{normalized}",
        "metadata": {"ticker": normalized, "project": "apex"},
        "recursion_limit": MAX_AGENT_ITERATIONS,
    }


async def analyze_with_workflow(state: AgentState) -> AgentState:
    """Run the compiled workflow with LangSmith metadata and a 120s timeout guard."""
    workflow = create_workflow()
    async with asyncio.timeout(WORKFLOW_TIMEOUT_SECONDS):
        return cast(AgentState, await workflow.ainvoke(state, config=workflow_run_config(state["ticker"])))


async def persist_workflow_results(session: AsyncSession, *, stock_id: int, state: AgentState) -> Any:
    """Persist the analysis run and each agent decision emitted by the workflow."""
    decision = state.get("portfolio_decision") or {}
    usage = state.get("usage", {})
    analysis = await AnalysisRepository(session).create(
        stock_id=stock_id,
        predicted_signal=_string_or_none(decision.get("signal")),
        final_confidence=_float_or_none(decision.get("confidence")),
        status="completed" if not state.get("errors") else "degraded",
        summary={
            "portfolio_decision": decision,
            "errors": state.get("errors", []),
            "agent_outputs": _agent_outputs(state),
        },
    )

    analysis.total_tokens = int(usage.get("tokens_in", 0)) + int(usage.get("tokens_out", 0))
    analysis.cost_usd = _float_or_none(usage.get("cost_usd"))
    analysis.compaction_applied = bool(state.get("compaction_applied", False))

    usage_by_agent = {turn.get("agent_name"): turn for turn in usage.get("turns", []) if isinstance(turn, Mapping)}
    for agent_name, payload in _agent_outputs(state).items():
        turn = usage_by_agent.get(agent_name, {})
        session.add(
            AgentDecision(
                analysis_run_id=analysis.id,
                agent_name=agent_name,
                prompt_version=1,
                signal=_string_or_none(payload.get("signal")),
                confidence=_float_or_none(payload.get("confidence")),
                reasoning=payload,
                indicators=payload.get("indicators") if isinstance(payload.get("indicators"), dict) else None,
                tokens_input=int(turn.get("tokens_in", 0)) if turn else None,
                tokens_output=int(turn.get("tokens_out", 0)) if turn else None,
                cost_usd=_float_or_none(turn.get("cost_usd")) if turn else None,
                is_fallback=payload.get("source") == "rule_based",
            )
        )
    await session.flush()
    return analysis


def _agent_outputs(state: AgentState) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}
    for key, agent_name in (
        ("technical_analysis", "technical_agent"),
        ("fundamental_analysis", "fundamental_agent"),
        ("risk_assessment", "risk_agent"),
        ("quant_analysis", "quant_agent"),
        ("portfolio_decision", "portfolio_manager"),
    ):
        value = state.get(key)
        if isinstance(value, dict):
            outputs[agent_name] = value
    return outputs


def _float_or_none(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _string_or_none(value: Any) -> str | None:
    return None if value is None else str(value)
