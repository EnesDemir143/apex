"""Risk-assessment LangGraph node."""

from __future__ import annotations

from typing import Any

from apex.agents._common import append_error, llm_trace_config, merge_usage
from apex.agents.indicators import closing_prices
from apex.agents.state import AgentState
from apex.services.llm_client import OpenAIClient


async def risk_agent(state: AgentState) -> AgentState:
    """Calculate risk metrics and ask the LLM for a risk assessment."""
    agent_name = "risk_agent"
    ticker = state["ticker"]
    try:
        metrics = calculate_risk_metrics(state["market_data"])
        prompt = (
            f"Assess risk for {ticker}. Return risk_score 0-1, risk_factors, and concise reasoning. Metrics: {metrics}"
        )
        response = await OpenAIClient().generate(
            prompt,
            system="You are a trading risk manager focused on downside protection.",
            config=llm_trace_config(agent_name, ticker),
        )
        assessment = {
            "ticker": ticker,
            "risk_score": _risk_score_from_metrics(metrics),
            "risk_factors": response.content,
            "metrics": metrics,
        }
        return {"risk_assessment": assessment, "usage": merge_usage(state, agent_name, response)}
    except Exception as exc:
        return append_error(state, f"{agent_name}: {exc}")


def calculate_risk_metrics(market_data: Any) -> dict[str, float]:
    """Calculate volatility, max drawdown, and a Sharpe-ratio stub."""
    close = closing_prices(market_data)
    returns = close.pct_change().dropna()
    volatility = float(returns.std()) if not returns.empty else 0.0
    cumulative_max = close.cummax()
    drawdowns = (close - cumulative_max) / cumulative_max
    max_drawdown = abs(float(drawdowns.min())) if not drawdowns.empty else 0.0
    sharpe_stub = float(returns.mean() / returns.std()) if not returns.empty and float(returns.std()) != 0.0 else 0.0
    return {
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "sharpe_ratio_stub": sharpe_stub,
    }


def _risk_score_from_metrics(metrics: dict[str, float]) -> float:
    return max(0.0, min(1.0, metrics["volatility"] + metrics["max_drawdown"]))
