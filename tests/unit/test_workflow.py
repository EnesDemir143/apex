"""Tests for the assembled LangGraph workflow."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from apex.agents.workflow import MAX_AGENT_ITERATIONS, WORKFLOW_TIMEOUT_SECONDS, create_workflow, workflow_run_config
from apex.api.app import create_app
from apex.domain.models import OHLCVBar
from apex.services.llm_client import FakeLLMClient


def _bars(ticker: str = "AAPL") -> list[OHLCVBar]:
    start = datetime.now(UTC) - timedelta(days=40)
    return [
        OHLCVBar(
            ticker=ticker,
            timestamp=start + timedelta(days=idx),
            open=Decimal("100") + Decimal(idx),
            high=Decimal("101") + Decimal(idx),
            low=Decimal("99") + Decimal(idx),
            close=Decimal("100") + Decimal(idx),
            volume=1_000_000 + idx,
            source="fake",
        )
        for idx in range(35)
    ]


def test_workflow_config_includes_trace_and_iteration_guards() -> None:
    config = workflow_run_config("aapl")

    assert config["metadata"] == {"ticker": "AAPL", "project": "apex"}
    assert config["run_name"] == "analyze_AAPL"
    assert config["recursion_limit"] == MAX_AGENT_ITERATIONS
    assert WORKFLOW_TIMEOUT_SECONDS == 120


@pytest.mark.asyncio
async def test_full_pipeline_with_fake_llm_client(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    fundamental = importlib.import_module("apex.agents.fundamental")
    portfolio_manager = importlib.import_module("apex.agents.portfolio_manager")
    risk = importlib.import_module("apex.agents.risk")
    technical = importlib.import_module("apex.agents.technical")

    monkeypatch.setattr(technical, "OpenAIClient", lambda: FakeLLMClient("BUY confidence 0.8"))
    monkeypatch.setattr(fundamental, "OpenAIClient", lambda: FakeLLMClient("BUY confidence 0.7"))
    monkeypatch.setattr(risk, "OpenAIClient", lambda: FakeLLMClient("risk_score 0.2"))
    monkeypatch.setattr(portfolio_manager, "OpenAIClient", lambda: FakeLLMClient("BUY confidence 0.75"))

    workflow = create_workflow()
    result = await workflow.ainvoke({"ticker": "AAPL", "market_data": _bars(), "errors": [], "usage": {}})

    assert result["portfolio_decision"]["signal"] in {"BUY", "SELL", "HOLD"}
    assert result["portfolio_decision"]["confidence"] == 0.75
    assert "technical_analysis" in result


@pytest.mark.asyncio
async def test_analyze_route_returns_signal_confidence_and_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    import apex.api.routes.analysis as analysis

    class FakeWorkflow:
        async def ainvoke(self, state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
            assert config and config["metadata"]["project"] == "apex"
            return {
                **state,
                "portfolio_decision": {"ticker": "AAPL", "signal": "HOLD", "confidence": 0.6},
                "usage": {"tokens_in": 3, "tokens_out": 4, "cost_usd": 0.01},
            }

    monkeypatch.setattr(analysis, "create_workflow", lambda: FakeWorkflow())
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/analyze/AAPL")

    assert response.status_code == 200
    payload = response.json()
    assert payload["signal"] == "HOLD"
    assert payload["confidence"] == 0.6
    assert payload["summary"]["usage_summary"]["tokens_in"] == 3
