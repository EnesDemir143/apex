"""Fundamental-analysis LangGraph node with an MVP RAG stub and local knowledge."""

from __future__ import annotations

from typing import Any

from apex.agents._common import (
    append_error,
    confidence_from_text,
    decision_from_parts,
    llm_trace_config,
    merge_usage,
    signal_from_text,
)
from apex.agents.state import AgentState
from apex.services.llm_client import OpenAIClient
from apex.services.local_knowledge import find_knowledge, format_knowledge_context
from apex.services.market_news import ensure_market_news


async def fundamental_agent(state: AgentState) -> AgentState:
    """Analyze fundamental context for the ticker."""
    agent_name = "fundamental_agent"
    ticker = state["ticker"]
    try:
        ensure_market_news(ticker)
        context = retrieve_fundamental_context(ticker)
        local_items = find_knowledge(ticker)
        local_context = format_knowledge_context(local_items)

        if local_context:
            context["local_knowledge_sources"] = [item["path"] for item in local_items]
            context["summary"] = local_context[:3000]
            prompt = (
                f"Analyze fundamentals for {ticker} incorporating the user's local knowledge. "
                "Return BUY, SELL, or HOLD with confidence 0-1 and concise reasoning. "
                f"Local knowledge:\n{local_context}"
            )
        else:
            context["summary"] = "No local knowledge found; use market-data context and conservative uncertainty."
            prompt = (
                f"Analyze fundamentals for {ticker}. "
                "Return BUY, SELL, or HOLD with confidence 0-1 and concise reasoning. "
                "No local knowledge available — use general market context and conservative uncertainty."
            )

        response = await OpenAIClient().generate(
            prompt,
            system="You are a conservative fundamental equity analyst.",
            config=llm_trace_config(agent_name, ticker),
        )
        analysis = decision_from_parts(
            ticker=ticker,
            signal=signal_from_text(response.content),
            confidence=confidence_from_text(response.content),
            reasoning=response.content,
            extra={"rag_context": context},
        )
        return {"fundamental_analysis": analysis, "usage": merge_usage(state, agent_name, response)}
    except Exception as exc:
        return append_error(state, f"{agent_name}: {exc}")


def retrieve_fundamental_context(ticker: str) -> dict[str, Any]:
    """Return MVP fundamental context until the full RAG pipeline ships."""
    return {
        "ticker": ticker,
        "source": "rag_stub",
        "summary": "No live fundamentals indexed yet; use market-data context and conservative uncertainty.",
    }
