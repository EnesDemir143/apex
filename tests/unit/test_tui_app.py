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


def test_command_palette_filters_commands_by_prefix_like_slash_picker() -> None:
    """Slash picker keeps only commands whose names start with typed text."""
    from apex.tui.app import CommandPalette

    palette = CommandPalette()
    options = palette._options_for_query("ch")

    assert [option.id for option in options] == ["chat"]
    assert "/chat" in options[0].prompt.plain
    assert "return to main screen" in options[0].prompt.plain


def test_command_palette_empty_filter_has_disabled_row() -> None:
    """Unmatched slash searches keep the overlay informative, not blank."""
    from apex.tui.app import CommandPalette

    palette = CommandPalette()
    options = palette._options_for_query("does-not-exist")

    assert len(options) == 1
    assert options[0].id == "__no_match__"
    assert options[0].disabled is True


@pytest.mark.asyncio
async def test_command_palette_is_available_on_secondary_screens() -> None:
    """Setup and team screens must keep the same slash dropdown behavior."""
    from apex.tui.app import CommandPalette

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()

        app.switch_screen("setup")
        await pilot.pause()
        assert app.screen.query_one("#command-palette", CommandPalette)

        app.switch_screen("team")
        await pilot.pause()
        assert app.screen.query_one("#command-palette", CommandPalette)


@pytest.mark.asyncio
async def test_info_commands_open_dedicated_detail_screen() -> None:
    """Info/help/error commands should not overwrite the main report panel."""
    from textual.widgets import Static

    from apex.tui.commands import dispatch

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()

        app._handle_result(dispatch("/usage", app._state))
        await pilot.pause()

        assert app.screen.query_one("#detail-title", Static).content == "[bold]Usage[/bold]"
        content = app.screen.query_one("#detail-content", Static).content
        assert "Usage metrics" in str(content)


@pytest.mark.asyncio
async def test_main_report_placeholder_avoids_no_analysis_copy() -> None:
    """Main screen should not show the old no-analysis placeholder."""
    from textual.widgets import Static

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()
        content = app.screen.query_one("#report-content", Static).content

    assert "No analysis run yet" not in str(content)


def test_ticker_select_palette_filters_tickers_by_prefix() -> None:
    """The /select picker should only show tickers matching the typed prefix."""
    from apex.tui.app import TickerSelectPalette

    palette = TickerSelectPalette()
    options = palette._options_for_query("M")

    assert [option.id for option in options] == ["MSFT"]
    assert "MSFT" in options[0].prompt.plain


def test_ticker_select_palette_opens_for_select_command() -> None:
    """Typing /select should open ticker choices, including all whitelisted symbols."""
    from apex.core.constants import TICKERS_WHITELIST
    from apex.tui.app import TickerSelectPalette

    palette = TickerSelectPalette()

    assert palette._query_from_input("/select") == ""
    assert palette._query_from_input("/select n") == "N"
    assert [option.id for option in palette._options_for_query("")] == list(TICKERS_WHITELIST)


@pytest.mark.asyncio
async def test_select_result_switches_chat_ticker_header() -> None:
    """Selecting a ticker from any screen should return to chat and update the header ticker."""
    from apex.tui.commands import dispatch

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()
        app.switch_screen("setup")
        await pilot.pause()

        app._handle_result(dispatch("/select NVDA", app._state))
        await pilot.pause()

        assert app.screen.id == "chat"
        assert app._state.setup.ticker == "NVDA"
        assert app.screen.query_one("#ticker-selector", TickerSelector).ticker == "NVDA"
