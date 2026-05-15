"""Textual pilot smoke tests for ApexTuiApp."""

from __future__ import annotations

import pytest

from apex.tui.app import ApexTuiApp
from apex.tui.widgets import (
    ChartPanel,
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

    assert [option.id for option in options] == ["chat", "chart"]
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


def test_ticker_select_palette_opens_for_chart_command() -> None:
    """Typing /chart should reuse ticker picker suggestions."""
    from apex.tui.app import TickerSelectPalette

    palette = TickerSelectPalette()

    assert palette._query_from_input("/chart") == ""
    assert palette._query_from_input("/chart n") == "N"
    assert [option.id for option in palette._options_for_query("N")] == ["NVDA"]


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


@pytest.mark.asyncio
async def test_chart_result_opens_chart_screen_and_syncs_ticker() -> None:
    """The /chart command opens a chart screen without terminal interaction."""
    from apex.tui.commands import dispatch

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()

        app._handle_result(dispatch("/chart NVDA", app._state))
        await pilot.pause()

        from apex.tui.app import ChartScreen
        assert isinstance(app.screen, ChartScreen)
        assert app._state.setup.ticker == "NVDA"
        assert app.screen.query_one("#chart-panel", ChartPanel).ticker == "NVDA"


@pytest.mark.asyncio
async def test_market_panel_receives_snapshot_after_mount(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main market panel should leave placeholder state for a selected ticker."""
    from datetime import UTC, datetime
    from decimal import Decimal

    from apex.domain.models.ohlcv import OHLCVBar
    from apex.services.market_snapshot import IndicatorSummary, LatestOHLCV, MarketSnapshot

    async def fake_snapshot(ticker: str) -> MarketSnapshot:
        bar = OHLCVBar(
            ticker=ticker,
            timestamp=datetime(2026, 1, 2, tzinfo=UTC),
            open=Decimal("100"),
            high=Decimal("102"),
            low=Decimal("99"),
            close=Decimal("101"),
            volume=1234,
            source="test",
        )
        return MarketSnapshot(
            ticker=ticker,
            bars=[bar],
            latest=LatestOHLCV(
                timestamp=bar.timestamp,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
            ),
            indicators=IndicatorSummary(
                rsi=50.0,
                macd=1.0,
                macd_signal=0.5,
                macd_histogram=0.5,
                sma20=101.0,
                sma50=101.0,
                ema12=101.0,
                ema26=101.0,
                bollinger_upper=102.0,
                bollinger_middle=101.0,
                bollinger_lower=100.0,
            ),
            source="test",
        )

    monkeypatch.setattr("apex.services.market_snapshot.get_market_snapshot", fake_snapshot)
    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause(0.2)

        panel = app.screen.query_one("#market-panel", MarketPanel)
        assert panel.ticker == "AAPL"
        assert panel.snapshot is not None
        assert panel.snapshot.latest.volume > 0


@pytest.mark.asyncio
async def test_market_panel_shows_fetching_copy_while_snapshot_loads() -> None:
    """Ticker changes should clear stale OHLCV and show an explicit fetching state."""
    from textual.widgets import Static

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()
        panel = app.screen.query_one("#market-panel", MarketPanel)

        panel.ticker = "MSFT"
        await pilot.pause()

        content = str(app.screen.query_one("#market-content", Static).content)
        assert "MSFT" in content
        assert "Fetching market snapshot" in content
        assert "Open: —" in content


@pytest.mark.asyncio
async def test_market_snapshot_cache_reuses_loaded_ticker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Selecting a previously loaded ticker should render from cache without refetching."""
    from datetime import UTC, datetime
    from decimal import Decimal

    from apex.domain.models.ohlcv import OHLCVBar
    from apex.services.market_snapshot import IndicatorSummary, LatestOHLCV, MarketSnapshot

    calls: list[str] = []

    async def fake_snapshot(ticker: str) -> MarketSnapshot:
        calls.append(ticker)
        bar = OHLCVBar(
            ticker=ticker,
            timestamp=datetime(2026, 1, 2, tzinfo=UTC),
            open=Decimal("100"),
            high=Decimal("102"),
            low=Decimal("99"),
            close=Decimal("101"),
            volume=1234,
            source="test",
        )
        return MarketSnapshot(
            ticker=ticker,
            bars=[bar],
            latest=LatestOHLCV(
                timestamp=bar.timestamp,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
            ),
            indicators=IndicatorSummary(
                rsi=50.0,
                macd=1.0,
                macd_signal=0.5,
                macd_histogram=0.5,
                sma20=101.0,
                sma50=101.0,
                ema12=101.0,
                ema26=101.0,
                bollinger_upper=102.0,
                bollinger_middle=101.0,
                bollinger_lower=100.0,
            ),
            source="test",
        )

    monkeypatch.setattr("apex.services.market_snapshot.get_market_snapshot", fake_snapshot)
    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause(0.2)

        app._sync_ticker("MSFT")
        await pilot.pause(0.2)
        app._sync_ticker("AAPL")
        await pilot.pause()

    assert calls == ["AAPL", "MSFT"]


@pytest.mark.asyncio
async def test_setup_panel_shows_default_language() -> None:
    """Setup owns language display now that /settings was removed."""
    from textual.widgets import Static

    app = ApexTuiApp(initial_ticker="AAPL")
    async with app.run_test() as pilot:
        await pilot.pause()
        app.switch_screen("setup")
        await pilot.pause()
        content = app.screen.query_one("#setup-content", Static).content

    assert "Language: English" in str(content)


def test_command_palette_includes_exit() -> None:
    """The slash picker should expose /exit."""
    from apex.tui.app import CommandPalette

    palette = CommandPalette()
    options = palette._options_for_query("ex")

    assert [option.id for option in options] == ["exit"]
    assert "/exit" in options[0].prompt.plain
