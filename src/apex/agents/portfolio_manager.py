"""Portfolio-manager supervisor node for final signal synthesis."""

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
from apex.domain.value_objects import Signal
from apex.services.llm_client import OpenAIClient


async def portfolio_manager(state: AgentState) -> AgentState:
    """Synthesize specialist analyses into a final BUY/SELL/HOLD decision.

    When quant_analysis is present and has a non-HOLD signal, it is included
    as an additional input for the portfolio manager.
    """
    agent_name = "portfolio_manager"
    ticker = state["ticker"]
    try:
        inputs: dict[str, Any] = {
            "technical": state.get("technical_analysis"),
            "fundamental": state.get("fundamental_analysis"),
            "risk": state.get("risk_assessment"),
            "errors": state.get("errors", []),
        }

        # Include quant analysis when available and non-HOLD
        quant = state.get("quant_analysis")
        if quant and quant.get("model_available") and quant.get("signal") != "HOLD":
            inputs["quant"] = quant

        prompt = (
            f"Synthesize the specialist outputs for {ticker}. "
            "Return BUY, SELL, or HOLD with confidence 0-1 and concise reasoning. "
            f"Inputs: {inputs}"
        )
        response = await OpenAIClient().generate(
            prompt,
            system="You are the final portfolio manager; prioritize capital preservation.",
            config=llm_trace_config(agent_name, ticker),
        )
        fallback_signal = _majority_signal(inputs)
        decision = decision_from_parts(
            ticker=ticker,
            signal=signal_from_text(response.content, default=fallback_signal),
            confidence=confidence_from_text(response.content, default=_aggregate_confidence(inputs)),
            reasoning=response.content,
            extra={"inputs": inputs},
        )
        return {"portfolio_decision": decision, "usage": merge_usage(state, agent_name, response)}
    except Exception as exc:
        return append_error(state, f"{agent_name}: {exc}")


def _majority_signal(inputs: dict[str, Any]) -> Signal:
    values = [
        str(payload.get("signal"))
        for key in ("technical", "fundamental")
        if isinstance((payload := inputs.get(key)), dict)
    ]
    for signal in Signal:
        if values.count(signal.value) >= 2:
            return signal
    return Signal.HOLD


def _aggregate_confidence(inputs: dict[str, Any]) -> float:
    confidences = [
        float(payload["confidence"])
        for key in ("technical", "fundamental")
        if isinstance((payload := inputs.get(key)), dict) and "confidence" in payload
    ]
    if not confidences:
        return 0.5
    risk = inputs.get("risk")
    risk_penalty = float(risk.get("risk_score", 0.0)) * 0.2 if isinstance(risk, dict) else 0.0
    return max(0.0, min(1.0, (sum(confidences) / len(confidences)) - risk_penalty))
