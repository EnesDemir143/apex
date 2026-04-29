"""Phase 6 standalone agent tests."""

from __future__ import annotations

import pytest
from importlib import import_module

from apex.agents import fundamental_agent, portfolio_manager, risk_agent, technical_agent
from apex.agents.indicators import calculate_bollinger_bands, calculate_macd, calculate_rsi
from apex.agents.usage_tracker import AnalysisTurnSummary, UsageTracker
from apex.services.llm_client import LLMResponse


class StubLLMClient:
    """Capture LangSmith config while returning a deterministic response."""

    calls: list[dict[str, object]] = []

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        config: dict[str, object] | None = None,
    ) -> LLMResponse:
        del prompt, system, temperature, max_tokens
        StubLLMClient.calls.append(config or {})
        return LLMResponse(content="HOLD confidence 0.60", model="stub", input_tokens=10, output_tokens=5, cost_usd=0.001)


def test_indicators_produce_series_and_expected_keys() -> None:
    prices = list(range(1, 31))

    assert float(calculate_rsi(prices).iloc[-1]) == pytest.approx(50.0)
    assert set(calculate_macd(prices)) == {"macd", "signal", "histogram"}
    assert set(calculate_bollinger_bands(prices)) == {"upper", "middle", "lower"}


@pytest.mark.asyncio
async def test_agents_return_partial_state_and_trace_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    fundamental_module = import_module("apex.agents.fundamental")
    portfolio_module = import_module("apex.agents.portfolio_manager")
    risk_module = import_module("apex.agents.risk")
    technical_module = import_module("apex.agents.technical")

    StubLLMClient.calls = []
    for module in (technical_module, fundamental_module, risk_module, portfolio_module):
        monkeypatch.setattr(module, "OpenAIClient", StubLLMClient)

    state = {"ticker": "AAPL", "market_data": {"close": list(range(100, 130))}, "errors": [], "usage": {}}
    state.update(await technical_agent(state))
    state.update(await fundamental_agent(state))
    state.update(await risk_agent(state))
    state.update(await portfolio_manager(state))

    assert state["technical_analysis"]["signal"] == "HOLD"
    assert state["fundamental_analysis"]["signal"] == "HOLD"
    assert state["risk_assessment"]["risk_score"] >= 0.0
    assert state["portfolio_decision"]["confidence"] == pytest.approx(0.6)
    assert {call["metadata"]["agent"] for call in StubLLMClient.calls} == {
        "technical_agent",
        "fundamental_agent",
        "risk_agent",
        "portfolio_manager",
    }


def test_usage_tracker_accumulates_turns() -> None:
    tracker = UsageTracker()
    tracker.add_turn(
        AnalysisTurnSummary(
            tokens_in=10,
            tokens_out=5,
            cost_usd=0.001,
            errors=[],
            duration_ms=100,
            agent_name="technical_agent",
        )
    )
    tracker.add_turn(
        AnalysisTurnSummary(
            tokens_in=2,
            tokens_out=1,
            cost_usd=0.002,
            errors=["warn"],
            duration_ms=50,
            agent_name="technical_agent",
        )
    )

    assert tracker.totals() == {
        "tokens_in": 12,
        "tokens_out": 6,
        "cost_usd": 0.003,
        "duration_ms": 150,
        "error_count": 1,
    }
    assert tracker.by_agent()["technical_agent"]["error_count"] == 1
