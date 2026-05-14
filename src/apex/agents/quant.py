"""Optional Quant ML Agent — ensemble model inference as a LangGraph node.

Disabled by default. When enabled, loads the trained quant ensemble from
models/quant/ and produces a BUY/SELL/HOLD signal alongside the LLM agents.
"""

from __future__ import annotations

import time
from typing import Any

from apex.agents.state import AgentState
from apex.ml.device import DeviceResolver
from apex.ml.model_registry import ModelRegistry


async def quant_agent(state: AgentState) -> AgentState:
    """Run quant ensemble inference and return structured output.

    This agent is optional — it only runs when ``quant_enabled`` is True
    in the AgentState and when a trained model is available on disk.

    Returns:
        Partial state update with ``quant_analysis`` key or empty dict
        if disabled / unavailable.
    """
    agent_name = "quant_agent"
    enabled = state.get("quant_enabled", False)

    if not enabled:
        return {
            "quant_analysis": {
                "signal": "HOLD",
                "confidence": 0.0,
                "reasoning": "Quant agent disabled",
                "model_available": False,
            }
        }

    try:
        market_data = state.get("market_data")
        if not market_data:
            return {
                "quant_analysis": {
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reasoning": "No market data available",
                    "model_available": False,
                }
            }

        # Convert market data to list of bar-like objects
        bars = _extract_bars(market_data)
        if not bars or len(bars) < 50:
            return {
                "quant_analysis": {
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reasoning": f"Insufficient bars for feature lookback: got {len(bars) if bars else 0}, need ≥50",
                    "model_available": False,
                }
            }

        registry = ModelRegistry()
        start = time.monotonic()
        prediction = registry.predict(bars)
        elapsed_ms = (time.monotonic() - start) * 1000

        analysis: dict[str, Any] = {
            "signal": prediction.signal,
            "confidence": prediction.confidence,
            "reasoning": prediction.reasoning,
            "top_features": prediction.top_features,
            "model_version": prediction.model_version,
            "device": prediction.device,
            "latency_ms": prediction.latency_ms,
            "model_available": prediction.model_available,
            "source": "quant_ml",
        }

        return {"quant_analysis": analysis}

    except Exception as exc:
        return {
            "quant_analysis": {
                "signal": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Quant agent error: {exc}",
                "model_available": False,
                "source": "error",
            }
        }


def _extract_bars(market_data: Any) -> list[Any]:
    """Normalise diverse market data shapes into a flat bar list."""
    # If it's a Mapping with 'bars' key
    if isinstance(market_data, dict):
        bars = market_data.get("bars", market_data.get("market_data"))
        if bars is not None:
            return _extract_bars(bars)
        return []

    # Already a list
    if isinstance(market_data, list):
        return market_data

    # Object with .bars attribute
    if hasattr(market_data, "bars"):
        return list(market_data.bars)

    # Iterable of bar-like objects
    try:
        result = list(market_data)
        if result and hasattr(result[0], "close"):
            return result
    except (TypeError, IndexError):
        pass

    return []
