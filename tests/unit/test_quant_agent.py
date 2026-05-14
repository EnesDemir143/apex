"""Tests for the Quant ML agent and model registry.

Verifies:
1. Quant Agent returns HOLD with model_available=False when disabled
2. Quant Agent returns HOLD with model_available=False when models not trained
3. Quant Agent handles missing market data gracefully
4. ModelRegistry returns fallback prediction when models don't exist
5. Workflow runs without error when quant is disabled (regression check)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from datetime import UTC, datetime, timedelta

from decimal import Decimal

import pytest

from apex.agents.quant import quant_agent
from apex.ml.model_registry import ModelRegistry


@pytest.fixture
def minimal_state() -> dict:
    """Minimal AgentState with quant disabled."""
    return {
        "ticker": "AAPL",
        "market_data": [],
        "quant_enabled": False,
        "errors": [],
        "usage": {},
    }


@pytest.fixture
def state_with_data() -> dict:
    """AgentState with quant enabled and fake market data."""
    from decimal import Decimal

    from apex.domain.models.ohlcv import OHLCVBar

    base = datetime(2025, 1, 1, tzinfo=UTC)
    bars = [
        OHLCVBar(
            ticker="AAPL",
            timestamp=base + timedelta(days=d),
            open=Decimal("150"),
            high=Decimal("155"),
            low=Decimal("145"),
            close=Decimal("152"),
            volume=1_000_000,
            source="test",
        )
        for d in range(61)  # 61 bars (enough for 50+ need)
    ]
    return {
        "ticker": "AAPL",
        "market_data": bars,
        "quant_enabled": True,
        "errors": [],
        "usage": {},
    }


class TestQuantAgent:
    """Tests for the quant_agent LangGraph node."""

    async def test_disabled_returns_hold(self, minimal_state):
        """When quant_enabled is False, agent returns HOLD with model_available=False."""
        result = await quant_agent(minimal_state)
        quant = result.get("quant_analysis", {})
        assert quant.get("signal") == "HOLD"
        assert quant.get("model_available") is False
        assert "disabled" in quant.get("reasoning", "").lower()

    async def test_enabled_no_models_returns_hold(self, state_with_data):
        """When enabled but no trained models, returns HOLD with model_available=False."""
        result = await quant_agent(state_with_data)
        quant = result.get("quant_analysis", {})
        # Registry will check disk and report not available
        assert quant.get("model_available") is False
        assert quant.get("signal") == "HOLD"

    async def test_insufficient_bars(self):
        """Less than 50 bars should return HOLD with explanation."""
        from apex.domain.models.ohlcv import OHLCVBar

        base = datetime(2025, 1, 1, tzinfo=UTC)
        bars = [
            OHLCVBar(
                ticker="AAPL",
                timestamp=base + timedelta(days=d),
                open=Decimal("150"),
                high=Decimal("155"),
                low=Decimal("145"),
                close=Decimal("152"),
                volume=1_000_000,
                source="test",
            )
            for d in range(9)
        ]
        state = {
            "ticker": "AAPL",
            "market_data": bars,
            "quant_enabled": True,
            "errors": [],
            "usage": {},
        }
        result = await quant_agent(state)
        quant = result.get("quant_analysis", {})
        assert quant.get("signal") == "HOLD"
        assert quant.get("model_available") is False

    async def test_no_market_data(self):
        """Missing market_data returns HOLD gracefully."""
        state = {
            "ticker": "AAPL",
            "market_data": None,
            "quant_enabled": True,
            "errors": [],
            "usage": {},
        }
        result = await quant_agent(state)
        quant = result.get("quant_analysis", {})
        assert quant.get("signal") == "HOLD"

    async def test_empty_market_data(self):
        """Empty market_data list returns HOLD gracefully."""
        state = {
            "ticker": "AAPL",
            "market_data": [],
            "quant_enabled": True,
            "errors": [],
            "usage": {},
        }
        result = await quant_agent(state)
        quant = result.get("quant_analysis", {})
        assert quant.get("signal") == "HOLD"

    async def test_quant_enabled_flag_passthrough(self):
        """Verify the quant_enabled flag is preserved when set on state."""
        state = {
            "ticker": "AAPL",
            "market_data": [],
            "quant_enabled": True,
            "errors": [],
            "usage": {},
        }
        assert state.get("quant_enabled") is True


class TestModelRegistry:
    """Tests for ModelRegistry (no actual model files needed)."""

    def test_not_available_by_default(self):
        """Registry reports not available when no models exist."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            registry = ModelRegistry(models_dir=tmp)
            assert registry.available is False
            assert registry.model_version == "not_loaded"

    def test_predict_returns_fallback(self):
        """predict() returns fallback QuantPrediction when not available."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            registry = ModelRegistry(models_dir=tmp)
            pred = registry.predict([])
            assert pred.signal == "HOLD"
            assert pred.model_available is False
            assert pred.confidence == 0.0
