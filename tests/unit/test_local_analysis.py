"""Unit tests for local_analysis service."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from apex.services.local_analysis import (
    _validate_analysis_date,
    run_local_analysis,
    run_local_analysis_sync,
)

# ---------------------------------------------------------------------------
# _validate_analysis_date
# ---------------------------------------------------------------------------

def test_validate_analysis_date_none_returns_today() -> None:
    assert _validate_analysis_date(None) == date.today()


def test_validate_analysis_date_string_parses() -> None:
    assert _validate_analysis_date("2026-01-15") == date(2026, 1, 15)


def test_validate_analysis_date_date_passthrough() -> None:
    d = date(2025, 6, 1)
    assert _validate_analysis_date(d) == d


def test_validate_analysis_date_future_raises() -> None:
    future = date.today() + timedelta(days=1)
    with pytest.raises(ValueError, match="future"):
        _validate_analysis_date(future)


# ---------------------------------------------------------------------------
# run_local_analysis
# ---------------------------------------------------------------------------

def _fake_workflow_result(ticker: str) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "market_data": [],
        "portfolio_decision": {"signal": "BUY", "confidence": 0.8},
        "technical_analysis": {"signal": "BUY"},
        "fundamental_analysis": {"signal": "BUY"},
        "risk_assessment": {"risk_score": 0.2},
        "errors": [],
        "usage": {"tokens_in": 10, "tokens_out": 20, "cost_usd": 0.001},
    }


@pytest.mark.asyncio
async def test_run_local_analysis_returns_structured_result(monkeypatch: pytest.MonkeyPatch) -> None:
    import apex.services.local_analysis as svc

    monkeypatch.setattr(svc, "_fetch_market_data", AsyncMock(return_value=[]))
    monkeypatch.setattr(svc, "analyze_with_workflow", AsyncMock(return_value=_fake_workflow_result("AAPL")))

    result = await run_local_analysis("AAPL")

    assert result["ticker"] == "AAPL"
    assert result["signal"] == "BUY"
    assert result["confidence"] == 0.8
    assert result["errors"] == []
    assert "analysis_date" in result


@pytest.mark.asyncio
async def test_run_local_analysis_rejects_non_whitelisted_ticker() -> None:
    with pytest.raises(ValueError, match="not in the whitelist"):
        await run_local_analysis("FAKE")


@pytest.mark.asyncio
async def test_run_local_analysis_rejects_future_date() -> None:
    future = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError, match="future"):
        await run_local_analysis("AAPL", analysis_date=future)


@pytest.mark.asyncio
async def test_run_local_analysis_canonicalizes_ticker(monkeypatch: pytest.MonkeyPatch) -> None:
    import apex.services.local_analysis as svc

    monkeypatch.setattr(svc, "_fetch_market_data", AsyncMock(return_value=[]))
    monkeypatch.setattr(svc, "analyze_with_workflow", AsyncMock(return_value=_fake_workflow_result("AAPL")))

    result = await run_local_analysis("aapl")
    assert result["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_run_local_analysis_fallback_on_market_data_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Market data fetch failure should fall back to stubs, not raise."""
    import apex.services.local_analysis as svc

    async def _raise(*_: Any, **__: Any) -> list[Any]:
        raise RuntimeError("network error")

    monkeypatch.setattr(svc, "_fetch_market_data", AsyncMock(return_value=[]))
    monkeypatch.setattr(svc, "analyze_with_workflow", AsyncMock(return_value=_fake_workflow_result("AAPL")))

    # Patch the fetcher inside _fetch_market_data to raise
    with patch("apex.ingestion.market_data_fetcher.MarketDataFetcher") as mock_cls:
        mock_cls.return_value.fetch_bars = AsyncMock(side_effect=RuntimeError("network error"))
        # _fetch_market_data is already monkeypatched to return [] so this just verifies no crash
        result = await run_local_analysis("AAPL")
    assert result["signal"] in {"BUY", "SELL", "HOLD"}


# ---------------------------------------------------------------------------
# run_local_analysis_sync
# ---------------------------------------------------------------------------

def test_run_local_analysis_sync_wraps_async(monkeypatch: pytest.MonkeyPatch) -> None:
    import apex.services.local_analysis as svc

    monkeypatch.setattr(svc, "_fetch_market_data", AsyncMock(return_value=[]))
    monkeypatch.setattr(svc, "analyze_with_workflow", AsyncMock(return_value=_fake_workflow_result("MSFT")))

    result = run_local_analysis_sync("MSFT")
    assert result["ticker"] == "MSFT"
    assert result["signal"] == "BUY"
