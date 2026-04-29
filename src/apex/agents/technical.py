"""Technical-analysis LangGraph node."""

from __future__ import annotations

from typing import Any

from apex.agents._common import (
    append_error,
    confidence_from_text,
    decision_from_parts,
    latest_value,
    llm_trace_config,
    merge_usage,
    signal_from_text,
)
from apex.agents.indicators import (
    calculate_bollinger_bands,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
    closing_prices,
)
from apex.agents.state import AgentState
from apex.services.llm_client import OpenAIClient


async def technical_agent(state: AgentState) -> AgentState:
    """Calculate indicators and ask the LLM for a technical interpretation."""
    agent_name = "technical_agent"
    ticker = state["ticker"]
    try:
        close = closing_prices(state["market_data"])
        rsi = calculate_rsi(close)
        macd = calculate_macd(close)
        bollinger = calculate_bollinger_bands(close)
        sma = calculate_sma(close)
        ema = calculate_ema(close)
        indicator_snapshot = {
            "rsi": latest_value(rsi),
            "macd": latest_value(macd["macd"]),
            "macd_signal": latest_value(macd["signal"]),
            "bollinger_upper": latest_value(bollinger["upper"]),
            "bollinger_middle": latest_value(bollinger["middle"]),
            "bollinger_lower": latest_value(bollinger["lower"]),
            "sma": {period: latest_value(series) for period, series in sma.items()},
            "ema": {span: latest_value(series) for span, series in ema.items()},
        }
        prompt = (
            f"Analyze technical indicators for {ticker}. "
            f"Return BUY, SELL, or HOLD with confidence 0-1 and concise reasoning. "
            f"Indicators: {indicator_snapshot}"
        )
        response = await OpenAIClient().generate(
            prompt,
            system="You are a disciplined technical trading analyst.",
            config=llm_trace_config(agent_name, ticker),
        )
        analysis = decision_from_parts(
            ticker=ticker,
            signal=signal_from_text(response.content),
            confidence=confidence_from_text(response.content),
            reasoning=response.content,
            extra={"indicators": indicator_snapshot},
        )
        return {"technical_analysis": analysis, "usage": merge_usage(state, agent_name, response)}
    except Exception as exc:
        return append_error(state, f"{agent_name}: {exc}")


def summarize_technical_inputs(state: AgentState) -> dict[str, Any]:
    """Return indicator inputs without invoking an LLM."""
    close = closing_prices(state["market_data"])
    return {
        "rsi": latest_value(calculate_rsi(close)),
        "macd": latest_value(calculate_macd(close)["macd"]),
        "bollinger": latest_value(calculate_bollinger_bands(close)["middle"]),
    }
