"""Textual pilot smoke tests for ApexTuiApp."""

from __future__ import annotations

import pytest

from apex.tui.app import ApexTuiApp
from apex.tui.widgets import (
    FooterStats,
    MarketPanel,
    ReportPanel,
    TickerSelector,
)


@pytest.mark.asyncio
async def test_app_mounts_core_widgets() -> None:
    """All core widgets must be present after mount."""
    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        assert screen.query_one("#ticker-selector", TickerSelector)
        assert screen.query_one("#market-panel", MarketPanel)
        assert screen.query_one("#report-panel", ReportPanel)
        assert screen.query_one("#footer-stats", FooterStats)


@pytest.mark.asyncio
async def test_screen_switching_commands() -> None:
    """/setup, /team, /chat commands return screen action."""
    from apex.tui.commands import dispatch
    from apex.tui.state import TuiState

    state = TuiState()

    result = dispatch("/setup", state)
    assert result.action == "screen"
    assert result.message == "setup"

    result = dispatch("/team", state)
    assert result.action == "screen"
    assert result.message == "team"

    result = dispatch("/chat", state)
    assert result.action == "screen"
    assert result.message == "chat"


@pytest.mark.asyncio
async def test_state_defaults() -> None:
    """TuiState defaults are sane on startup."""
    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app._state.setup.ticker == "AAPL"
        assert app._state.analysis.status == "idle"
        assert "portfolio" in app._state.setup.enabled_agents
