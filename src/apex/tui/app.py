"""Apex Textual terminal cockpit — ApexTuiApp."""

from __future__ import annotations

import time
from typing import Any, cast

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, OptionList, Static
from textual.widgets.option_list import Option

from apex.core.constants import TICKERS_WHITELIST
from apex.tui.commands import COMMAND_HELP, CommandResult, dispatch
from apex.tui.state import TuiState
from apex.tui.widgets import (
    AgentProgressTable,
    EventLog,
    FooterStats,
    MarketPanel,
    ReportPanel,
    SetupPanel,
    TickerSelector,
)

CSS_PATH = "apex.tcss"


class TickerSelectPalette(Container):
    """Ticker picker shown after /select."""

    MAX_OPTIONS = 8

    class TickerSelected(Message):
        """Emitted when a ticker is selected from the picker."""

        def __init__(self, ticker: str, command: str = "select") -> None:
            super().__init__()
            self.ticker = ticker
            self.command = command

    DEFAULT_CSS = """
    TickerSelectPalette {
        display: none;
        layer: overlay;
        width: 44;
        height: auto;
        max-height: 14;
        background: #0d1117;
        border: round #30363d;
        padding: 0 1;
        offset: 1 13;
    }

    TickerSelectPalette.visible {
        display: block;
    }

    TickerSelectPalette #ticker-palette-title {
        height: 1;
        color: #8b949e;
        text-style: bold;
    }

    TickerSelectPalette #ticker-options {
        height: auto;
        max-height: 8;
        background: #0d1117;
    }

    TickerSelectPalette #ticker-palette-hint {
        height: 1;
        color: #6e7681;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Select ticker", id="ticker-palette-title")
        yield OptionList(*self._options_for_query(""), id="ticker-options")
        yield Static("↑↓ select  ·  enter choose  ·  esc close", id="ticker-palette-hint")

    def update_query(self, value: str) -> None:
        """Refresh ticker choices while the user types /select ..."""
        query = self._query_from_input(value)
        if query is None:
            self.hide_palette()
            return

        option_list = self.query_one("#ticker-options", OptionList)
        option_list.set_options(self._options_for_query(query))
        if option_list.option_count:
            option_list.highlighted = 0
        self.show_palette()

    def _query_from_input(self, value: str) -> str | None:
        text = value.strip()
        command = self._ticker_command(text)
        if command is None:
            return None
        lowered = text.lower()
        if lowered == f"/{command}":
            return ""
        if not lowered.startswith(f"/{command} "):
            return None
        return text.split(maxsplit=1)[1].strip().upper()

    def _ticker_command(self, text: str) -> str | None:
        lowered = text.lower()
        for command in ("select", "chart"):
            if lowered == f"/{command}" or lowered.startswith(f"/{command} "):
                return command
        return None

    def _options_for_query(self, query: str) -> list[Option]:
        matches: list[Option] = []
        for ticker in TICKERS_WHITELIST:
            if query and not ticker.startswith(query):
                continue
            matches.append(Option(self._option_label(ticker), id=ticker))
            if len(matches) >= self.MAX_OPTIONS:
                break

        if matches:
            return matches
        return [Option(Text("No tickers match", style="dim"), id="__no_match__", disabled=True)]

    def _option_label(self, ticker: str) -> Text:
        label = Text()
        label.append(ticker, style="bold #58a6ff")
        if ticker == "SPY":
            label.append("  S&P 500 ETF", style="#8b949e")
        return label

    def show_palette(self) -> None:
        self.add_class("visible")

    def hide_palette(self) -> None:
        self.remove_class("visible")


class CommandPalette(Container):
    """Command palette overlay inspired by opencode's slash-command picker."""

    MAX_OPTIONS = 8

    DEFAULT_CSS = """
    CommandPalette {
        display: none;
        layer: overlay;
        width: 74;
        height: auto;
        max-height: 16;
        background: #0d1117;
        border: round #30363d;
        padding: 0 1;
        offset: 1 13;
    }

    CommandPalette.visible {
        display: block;
    }

    CommandPalette #command-palette-title {
        height: 1;
        color: #8b949e;
        text-style: bold;
    }

    CommandPalette #command-options {
        height: auto;
        max-height: 10;
        background: #0d1117;
    }

    CommandPalette #command-palette-hint {
        height: 1;
        color: #6e7681;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Commands", id="command-palette-title")
        options = self._options_for_query("")
        yield OptionList(*options, id="command-options")
        yield Static("↑↓ select  ·  enter run  ·  esc close", id="command-palette-hint")

    def update_query(self, value: str) -> None:
        """Refresh visible commands for the current slash input."""
        if not value.startswith("/"):
            self.hide_palette()
            return

        query = value[1:].strip().lower()
        if " " in query:
            command_name = query.split(maxsplit=1)[0]
            if command_name == "select":
                self.hide_palette()
                return
            query = command_name
        options = self._options_for_query(query)
        option_list = self.query_one("#command-options", OptionList)
        option_list.set_options(options)
        if option_list.option_count:
            option_list.highlighted = 0
        self.show_palette()

    def _options_for_query(self, query: str) -> list[Option]:
        matches: list[Option] = []
        for cmd, desc in COMMAND_HELP.items():
            if query and not cmd.lower().startswith(query):
                continue
            matches.append(Option(self._option_label(cmd, desc), id=cmd))
            if len(matches) >= self.MAX_OPTIONS:
                break

        if matches:
            return matches
        return [Option(Text("No commands match", style="dim"), id="__no_match__", disabled=True)]

    def _option_label(self, cmd: str, desc: str) -> Text:
        description = desc.split(" — ", 1)[1] if " — " in desc else desc
        label = Text()
        label.append(f"/{cmd:<12}", style="bold #58a6ff")
        label.append(description, style="#8b949e")
        return label

    def show_palette(self) -> None:
        self.add_class("visible")

    def hide_palette(self) -> None:
        self.remove_class("visible")


class CommandPaletteScreenMixin:
    """Shared slash palette behavior for screens with #command-input."""

    def action_close_palette(self) -> None:
        """Close open slash palettes."""
        screen = cast(Screen[None], self)
        screen.query_one("#command-palette", CommandPalette).hide_palette()
        screen.query_one("#ticker-select-palette", TickerSelectPalette).hide_palette()
        screen.query_one("#command-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show and filter slash palettes for the current input."""
        screen = cast(Screen[None], self)
        command_palette = screen.query_one("#command-palette", CommandPalette)
        ticker_palette = screen.query_one("#ticker-select-palette", TickerSelectPalette)
        command_palette.update_query(event.value)
        ticker_palette.update_query(event.value)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle command or ticker selection from visible palettes."""
        screen = cast(Screen[None], self)
        if event.option_list.id == "ticker-options":
            self._select_ticker_option(screen, event.option_id)
            return

        screen.query_one("#command-palette", CommandPalette).hide_palette()

        if event.option_id == "__no_match__":
            return

        cmd = f"/{event.option_id}"
        input_widget = screen.query_one("#command-input", Input)
        if event.option_id == "select":
            input_widget.value = "/select "
            screen.query_one("#ticker-select-palette", TickerSelectPalette).update_query(input_widget.value)
            input_widget.focus()
            return

        input_widget.value = cmd
        screen.post_message(Input.Submitted(input_widget, cmd))

    def on_ticker_select_palette_ticker_selected(self, message: TickerSelectPalette.TickerSelected) -> None:
        """Submit the selected ticker as /select TICKER."""
        screen = cast(Screen[None], self)
        input_widget = screen.query_one("#command-input", Input)
        command = f"/{message.command} {message.ticker}"
        input_widget.value = command
        screen.query_one("#ticker-select-palette", TickerSelectPalette).hide_palette()
        screen.post_message(Input.Submitted(input_widget, command))

    def _select_ticker_option(self, screen: Screen[None], option_id: str | None) -> None:
        if option_id in (None, "__no_match__"):
            return
        screen.query_one("#ticker-select-palette", TickerSelectPalette).post_message(
            TickerSelectPalette.TickerSelected(str(option_id), command=self._ticker_command_for_input(screen))
        )

    def _ticker_command_for_input(self, screen: Screen[None]) -> str:
        value = screen.query_one("#command-input", Input).value.strip().lower()
        if value == "/chart" or value.startswith("/chart "):
            return "chart"
        return "select"


class ChatScreen(CommandPaletteScreenMixin, Screen[None]):
    """Main chat/analysis screen."""

    BINDINGS = [
        ("escape", "close_palette", "Close"),
    ]

    def __init__(self) -> None:
        super().__init__(id="chat")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield TickerSelector(id="ticker-selector")
        yield MarketPanel(id="market-panel")
        yield ReportPanel(id="report-panel")
        yield Input(
            placeholder="Type / for commands…",
            id="command-input",
        )
        yield FooterStats(id="footer-stats")
        yield Footer()
        yield CommandPalette(id="command-palette")
        yield TickerSelectPalette(id="ticker-select-palette")


class SetupScreen(CommandPaletteScreenMixin, Screen[None]):
    """Setup configuration screen."""

    BINDINGS = [
        ("escape", "close_palette", "Close"),
    ]

    def __init__(self) -> None:
        super().__init__(id="setup")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SetupPanel(id="setup-panel")
        yield Input(
            placeholder="Type /chat to return to main screen…",
            id="command-input",
        )
        yield Footer()
        yield CommandPalette(id="command-palette")
        yield TickerSelectPalette(id="ticker-select-palette")


class TeamScreen(CommandPaletteScreenMixin, Screen[None]):
    """Agent team progress screen."""

    BINDINGS = [
        ("escape", "close_palette", "Close"),
    ]

    def __init__(self) -> None:
        super().__init__(id="team")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield AgentProgressTable(id="agent-progress")
        yield EventLog(id="event-log")
        yield Input(
            placeholder="Type /chat to return to main screen…",
            id="command-input",
        )
        yield Footer()
        yield CommandPalette(id="command-palette")
        yield TickerSelectPalette(id="ticker-select-palette")


class CommandDetailScreen(CommandPaletteScreenMixin, Screen[None]):
    """Dedicated screen for slash command output."""

    BINDINGS = [
        ("escape", "close_palette", "Close"),
    ]

    DEFAULT_CSS = """
    CommandDetailScreen #detail-title {
        height: 3;
        background: #161b22;
        border-bottom: solid #30363d;
        padding: 0 1;
        color: #58a6ff;
        text-style: bold;
    }

    CommandDetailScreen #detail-content {
        height: 1fr;
        background: #0d1117;
        border: solid #30363d;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self, title: str, content: str) -> None:
        super().__init__()
        self._title = title
        self._content = content

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(f"[bold]{self._title}[/bold]", id="detail-title")
        yield Static(self._content, id="detail-content")
        yield Input(
            placeholder="Type / for commands or /chat to return…",
            id="command-input",
        )
        yield Footer()
        yield CommandPalette(id="command-palette")
        yield TickerSelectPalette(id="ticker-select-palette")


class ChartScreen(CommandPaletteScreenMixin, Screen[None]):
    """Dedicated terminal-native chart screen."""

    BINDINGS = [
        Binding("escape", "close_or_exit_inspect", "Close"),
        Binding("equal,plus", "zoom_in", "Zoom In", show=False),
        Binding("minus", "zoom_out", "Zoom Out", show=False),
        Binding("left", "crosshair_left", "◀", show=True),
        Binding("right", "crosshair_right", "▶", show=True),
        Binding("shift+left", "pan_left", "Pan←", show=False),
        Binding("shift+right", "pan_right", "Pan→", show=False),
        Binding("tab", "inspect_prev", "Prev Bar", show=False, priority=True),
        Binding("shift+tab", "inspect_next", "Next Bar", show=False, priority=True),
        Binding("1", "timeframe_1m", "1m", show=True),
        Binding("5", "timeframe_5m", "5m", show=True),
        Binding("h", "timeframe_1h", "1h", show=True),
        Binding("d", "timeframe_1d", "1d", show=True),
        Binding("r", "refresh_chart", "Refresh", show=True),
    ]

    DEFAULT_CSS = """
    ChartScreen #chart-layout {
        height: 1fr;
        layout: horizontal;
    }
    ChartScreen #chart-panel {
        width: 1fr;
    }
    """

    def __init__(self, ticker: str) -> None:
        super().__init__(id="chart")
        self.ticker = ticker

    def compose(self) -> ComposeResult:
        from textual.containers import Horizontal as HBox
        yield Header(show_clock=True)
        with HBox(id="chart-layout"):
            chart_panel = ChartPanel(id="chart-panel")
            chart_panel.ticker = self.ticker
            yield chart_panel
            yield KeybindPanel(id="keybind-panel")
        yield Input(
            placeholder="/tf 1d|1h|5m  /refresh  /inspect  /set  /chart TICKER",
            id="command-input",
        )
        yield Footer()
        yield CommandPalette(id="command-palette", chart_only=True)
        yield TickerSelectPalette(id="ticker-select-palette")

    def _panel(self) -> ChartPanel:
        return self.query_one("#chart-panel", ChartPanel)

    # ── chart-specific command handler ────────────────────────────────────

    _TF_ALIASES: dict[str, str] = {
        "1m": "1m", "5m": "5m", "15m": "15m",
        "1h": "1h", "h": "1h",
        "4h": "4h",
        "1d": "1d", "d": "1d",
        "1w": "1w", "w": "1w",
    }

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Intercept chart-specific commands before global dispatch."""
        raw = event.value.strip()
        event.input.clear()
        if not raw:
            return
        if not raw.startswith("/"):
            raw = f"/{raw}"

        parts = raw.lstrip("/").split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:]

        # ── /set-tf-1d  or  /set-tf  (hyphenated format) ─────────────────
        if cmd.startswith("set-tf"):
            remainder = cmd[len("set-tf"):]  # "" | "-1d" | "-1m" etc.
            tf_token = remainder.lstrip("-") or (args[0].lower() if args else "")
            if not tf_token:
                self._chart_notify(
                    "Timeframe options:\n"
                    "  /set-tf-1m   /set-tf-5m   /set-tf-1h\n"
                    "  /set-tf-4h   /set-tf-1d   /set-tf-1w"
                )
                return
            tf = self._TF_ALIASES.get(tf_token)
            if tf:
                self._set_timeframe(tf)
            else:
                self._chart_notify(f"Unknown timeframe '{tf_token}'. Try: 1m 5m 1h 4h 1d 1w")
            return

        # ── /refresh (/r is already a keybind but command form works too)
        if cmd in ("refresh",):
            self.action_refresh_chart()
            return

        # ── /inspect  → bar-inspect mode
        if cmd == "inspect":
            self.action_enter_bar_inspect()
            return

        # ── /tf 1d  or  /timeframe 1d  → set timeframe directly
        if cmd in ("tf", "timeframe") and args:
            tf = self._TF_ALIASES.get(args[0].lower())
            if tf:
                self._set_timeframe(tf)
            else:
                self._chart_notify(f"Unknown timeframe '{args[0]}'. Try: 1m 5m 1h 4h 1d 1w")
            return

        # ── /set tf=1d  or  /set timeframe 1d
        if cmd == "set":
            if not args:
                self._chart_notify(
                    "Chart commands:\n"
                    "  /set tf 1m|5m|1h|4h|1d|1w   — set timeframe\n"
                    "  /tf 1d                        — alias\n"
                    "  /refresh                      — reload data\n"
                    "  /x                            — bar-inspect mode\n"
                    "  /zoom + | /zoom -             — zoom in/out"
                )
                return
            sub = args[0].lower()
            # /set tf 1d
            if sub in ("tf", "timeframe") and len(args) >= 2:
                tf = self._TF_ALIASES.get(args[1].lower())
                if tf:
                    self._set_timeframe(tf)
                else:
                    self._chart_notify(f"Unknown timeframe '{args[1]}'. Try: 1m 5m 1h 4h 1d 1w")
                return
            # /set tf=1d  (single token)
            if "=" in sub:
                key, _, val = sub.partition("=")
                if key in ("tf", "timeframe"):
                    tf = self._TF_ALIASES.get(val)
                    if tf:
                        self._set_timeframe(tf)
                    else:
                        self._chart_notify(f"Unknown timeframe '{val}'.")
                    return

        # ── /zoom +  /zoom -
        if cmd == "zoom":
            if args and args[0] in ("+", "in"):
                self.action_zoom_in()
            elif args and args[0] in ("-", "out"):
                self.action_zoom_out()
            return

        # Everything else → global dispatcher
        from apex.tui.commands import dispatch
        result = dispatch(raw, self.app._state)  # type: ignore[attr-defined]
        self.app._handle_result(result)  # type: ignore[attr-defined]

    def _chart_notify(self, msg: str) -> None:
        """Show a brief notification in the chart bar-info strip."""
        try:
            from textual.widgets import Static
            self._panel().query_one("#chart-bar-info", Static).update(
                f"[bold #58a6ff]ℹ[/bold #58a6ff]  {msg}"
            )
        except Exception:
            pass


    def action_crosshair_left(self) -> None:
        p = self._panel()
        bars = p._visible_bars()
        if not bars:
            return
        cur = p.crosshair if p.crosshair >= 0 else len(bars) - 1
        p.crosshair = max(0, cur - 1)

    def action_crosshair_right(self) -> None:
        p = self._panel()
        bars = p._visible_bars()
        if not bars:
            return
        cur = p.crosshair if p.crosshair >= 0 else len(bars) - 1
        nxt = cur + 1
        p.crosshair = -1 if nxt >= len(bars) else nxt

    # ── zoom ──────────────────────────────────────────────────────────────

    def action_zoom_in(self) -> None:
        p = self._panel()
        p.viewport_bars = max(10, p.viewport_bars - 10)

    def action_zoom_out(self) -> None:
        p = self._panel()
        p.viewport_bars = min(200, p.viewport_bars + 10)

    # ── pan (shift+arrow) ─────────────────────────────────────────────────

    def action_pan_left(self) -> None:
        p = self._panel()
        if p.snapshot:
            max_offset = max(0, len(p.snapshot.bars) - p.viewport_bars)
            p.offset = min(max_offset, p.offset + 10)

    def action_pan_right(self) -> None:
        p = self._panel()
        p.offset = max(0, p.offset - 10)

    # ── timeframe ─────────────────────────────────────────────────────────

    def action_timeframe_1m(self) -> None:
        self._set_timeframe("1m")

    def action_timeframe_5m(self) -> None:
        self._set_timeframe("5m")

    def action_timeframe_1h(self) -> None:
        self._set_timeframe("1h")

    def action_timeframe_1d(self) -> None:
        self._set_timeframe("1d")

    def _set_timeframe(self, tf: str) -> None:
        p = self._panel()
        p.timeframe = tf
        p.offset = 0
        p.crosshair = -1
        self.app.run_worker(self._fetch_for_timeframe(tf), exclusive=True, name="chart-fetch")

    async def _fetch_for_timeframe(self, tf: str) -> None:
        from apex.services.market_snapshot import get_market_snapshot
        days_map = {"1m": 5, "5m": 10, "1h": 30, "1d": 120}
        days = days_map.get(tf, 60)
        try:
            snapshot = await get_market_snapshot(self.ticker, days=days)
        except Exception as exc:
            self._panel().error = str(exc)
            return
        p = self._panel()
        p.error = ""
        p.snapshot = snapshot

    # ── bar-inspect mode ──────────────────────────────────────────────────

    def action_enter_bar_inspect(self) -> None:
        """Activate bar-inspect mode: set crosshair to last bar."""
        p = self._panel()
        bars = p._visible_bars()
        if bars:
            p.crosshair = len(bars) - 1
        p.bar_select_mode = True
        # focus chart so arrow/tab keys work without typing in input
        p.focus()

    def action_inspect_prev(self) -> None:
        """Move crosshair one bar to the left (older), wrapping around."""
        p = self._panel()
        if not p.bar_select_mode:
            return
        bars = p._visible_bars()
        if not bars:
            return
        cur = p.crosshair if p.crosshair >= 0 else len(bars) - 1
        # wrap: at bar 0 → jump to last bar
        p.crosshair = len(bars) - 1 if cur == 0 else cur - 1

    def action_inspect_next(self) -> None:
        """Move crosshair one bar to the right (newer), wrapping around."""
        p = self._panel()
        if not p.bar_select_mode:
            return
        bars = p._visible_bars()
        if not bars:
            return
        cur = p.crosshair if p.crosshair >= 0 else len(bars) - 1
        # wrap: at last bar → jump to bar 0
        p.crosshair = 0 if cur >= len(bars) - 1 else cur + 1

    def action_close_or_exit_inspect(self) -> None:
        """Escape: exit bar-inspect mode if active, otherwise close palette."""
        p = self._panel()
        if p.bar_select_mode:
            p.bar_select_mode = False
            p.crosshair = -1
            self.query_one("#command-input", Input).focus()
        else:
            self.action_close_palette()

    # ── refresh ───────────────────────────────────────────────────────────

    def action_refresh_chart(self) -> None:
        p = self._panel()
        p.snapshot = None
        p.error = ""
        p.crosshair = -1
        self.app.run_worker(self._fetch_for_timeframe(p.timeframe), exclusive=True, name="chart-fetch")


class ApexTuiApp(App[None]):
    """Apex terminal cockpit — app-first, Hermes-inspired."""

    CSS_PATH = CSS_PATH

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+r", "run_analysis", "Analyze", show=True),
        Binding("escape", "clear_input", "Clear", show=False),
    ]

    SCREENS = {
        "chat": ChatScreen,
        "setup": SetupScreen,
        "team": TeamScreen,
    }

    def __init__(self, initial_ticker: str = "AAPL") -> None:
        super().__init__()
        self._state = TuiState()
        self._state.setup.ticker = initial_ticker.upper()
        self._analysis_start: float = 0.0
        self._market_snapshot_cache: dict[str, Any] = {}

    def on_mount(self) -> None:
        self.push_screen("chat")
        # Sync ticker after screen is pushed
        self.call_after_refresh(lambda: self._sync_ticker(self._state.setup.ticker))

    # ── Input handling ────────────────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.clear()
        if not raw:
            return
        if not raw.startswith("/"):
            raw = f"/{raw}"
        result = dispatch(raw, self._state)
        self._handle_result(result)

    def _handle_result(self, result: CommandResult) -> None:
        if result.action == "screen":
            # Screen switching
            self.switch_screen(result.message)
            return

        if result.action == "exit":
            self.exit()
            return

        if result.action == "select":
            self._state.setup.ticker = result.ticker
            if self.screen.id != "chat":
                self.switch_screen("chat")
            self.call_after_refresh(lambda: self._sync_ticker(result.ticker))
            self._push_event(result.message)

        elif result.action == "chart":
            ticker = result.ticker or self._state.setup.ticker
            self._state.setup.ticker = ticker
            self._push_event(result.message)
            self._open_chart(ticker)

        elif result.action == "analyze":
            ticker = result.ticker or self._state.setup.ticker
            self._state.setup.ticker = ticker
            self._sync_ticker(ticker)
            self._push_event(result.message)
            self._run_analysis_worker(ticker)

        elif result.action == "bar_select":
            # Activate bar-inspect mode on the current ChartScreen if open
            try:
                from apex.tui.app import ChartScreen as _CS  # noqa: F401
                if isinstance(self.screen, ChartScreen):
                    self.screen.action_enter_bar_inspect()
                else:
                    self._show_output(
                        "Bar inspect mode is only available on the chart screen.\n"
                        "Open a chart first with /chart TICKER, then type /x.",
                        title="/x",
                    )
            except Exception:
                pass

        elif result.action in ("info", "help", "error"):
            self._show_output(result.message, title=result.title or result.action.title())
            self._push_event(result.message[:80])

    # ── Analysis worker ───────────────────────────────────────────────────

    def _run_analysis_worker(self, ticker: str) -> None:
        """Launch analysis in a background worker so the UI stays responsive."""
        self._analysis_start = time.monotonic()
        self._state.analysis.status = "running"
        self._state.analysis.ticker = ticker
        self._push_event(f"Starting analysis for {ticker}…")
        self._update_footer(done=0)
        self.run_worker(self._do_analysis(ticker), exclusive=True, name="analysis")

    async def _do_analysis(self, ticker: str) -> None:
        from apex.services.local_analysis import run_local_analysis

        setup = self._state.setup
        try:
            result: dict[str, Any] = await run_local_analysis(
                ticker,
                analysis_date=setup.analysis_date,
                extra_instructions=setup.global_instructions or None,
                agent_instructions=setup.agent_instructions or None,
            )
        except Exception as exc:
            self._state.analysis.status = "error"
            self._state.analysis.errors = [str(exc)]
            self._push_event(f"[red]Error:[/red] {exc}")
            self._show_output(f"Analysis failed: {exc}", title="Analysis Error")
            return

        self._state.analysis.status = "completed"
        self._state.analysis.signal = result["signal"]
        self._state.analysis.confidence = result["confidence"]
        self._state.analysis.errors = result.get("errors") or []
        self._state.analysis.usage = result.get("usage") or {}
        self._state.analysis.agent_outputs = result.get("agent_outputs") or {}
        self._state.analysis.analysis_date = result.get("analysis_date", "")

        elapsed = time.monotonic() - self._analysis_start
        signal = result["signal"]
        conf = result["confidence"]
        usage = result.get("usage") or {}
        tokens = usage.get("total_tokens", 0)
        cost = usage.get("cost_usd", 0.0)

        color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(signal, "white")
        report = (
            f"[bold]{ticker}[/bold] — [{color}]{signal}[/{color}]  "
            f"confidence: {conf:.0%}\n"
            f"Date: {result.get('analysis_date', '')}  "
            f"Tokens: {tokens}  Cost: ${cost:.4f}  Elapsed: {elapsed:.1f}s"
        )
        if self._state.analysis.errors:
            report += "\n[red]Errors:[/red] " + "; ".join(self._state.analysis.errors)

        self._state.current_report = report
        self._push_event(f"Analysis complete: {ticker} → {signal} ({conf:.0%})")
        self._show_report(report)
        self._update_footer(done=4, tokens=tokens, cost=cost, elapsed=elapsed)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _sync_ticker(self, ticker: str) -> None:
        try:
            screen = self.screen
            screen.query_one("#ticker-selector", TickerSelector).ticker = ticker
            screen.query_one("#market-panel", MarketPanel).ticker = ticker
        except Exception:
            pass
        self._refresh_market_snapshot(ticker)

    def _refresh_market_snapshot(self, ticker: str) -> None:
        cached = self._market_snapshot_cache.get(ticker)
        if cached is not None:
            self._set_market_snapshot(cached)
            return
        self.run_worker(self._load_market_snapshot(ticker), exclusive=True, name="market-snapshot")

    async def _load_market_snapshot(self, ticker: str) -> None:
        from apex.services.market_snapshot import get_market_snapshot

        try:
            snapshot = await get_market_snapshot(ticker)
        except Exception as exc:
            self._set_market_snapshot_error(ticker, str(exc))
            return
        self._market_snapshot_cache[snapshot.ticker] = snapshot
        self._set_market_snapshot(snapshot)

    def _set_market_snapshot(self, snapshot: Any) -> None:
        try:
            market_panel = self.screen.query_one("#market-panel", MarketPanel)
            market_panel.ticker = snapshot.ticker
            market_panel.error = ""
            market_panel.snapshot = snapshot
        except Exception:
            pass
        try:
            chart_panel = self.screen.query_one("#chart-panel", ChartPanel)
            chart_panel.ticker = snapshot.ticker
            chart_panel.error = ""
            chart_panel.snapshot = snapshot
        except Exception:
            pass

    def _set_market_snapshot_error(self, ticker: str, message: str) -> None:
        try:
            market_panel = self.screen.query_one("#market-panel", MarketPanel)
            market_panel.ticker = ticker
            market_panel.error = message
        except Exception:
            pass
        try:
            chart_panel = self.screen.query_one("#chart-panel", ChartPanel)
            chart_panel.ticker = ticker
            chart_panel.error = message
        except Exception:
            pass

    def _open_chart(self, ticker: str) -> None:
        self.push_screen(ChartScreen(ticker))
        self.call_after_refresh(lambda: self._refresh_market_snapshot(ticker))

    def _push_event(self, msg: str) -> None:
        self._state.add_event(msg)
        try:
            screen = self.screen
            screen.query_one("#event-log", EventLog).push_event(msg)
        except Exception:
            pass

    def _show_output(self, msg: str, title: str = "Output") -> None:
        self.push_screen(CommandDetailScreen(title=title, content=msg))

    def _show_report(self, content: str) -> None:
        try:
            screen = self.screen
            screen.query_one("#report-panel", ReportPanel).update_report(content)
        except Exception:
            pass

    def _update_footer(
        self,
        done: int = 0,
        tokens: int = 0,
        cost: float = 0.0,
        elapsed: float = 0.0,
    ) -> None:
        try:
            screen = self.screen
            screen.query_one("#footer-stats", FooterStats).update_stats(
                done=done, total=4, tokens=tokens, cost=cost, elapsed=elapsed
            )
        except Exception:
            pass

    # ── Actions ───────────────────────────────────────────────────────────

    def action_run_analysis(self) -> None:
        self._run_analysis_worker(self._state.setup.ticker)

    def action_clear_input(self) -> None:
        try:
            screen = self.screen
            screen.query_one("#command-input", Input).clear()
        except Exception:
            pass


def run_tui(ticker: str = "AAPL") -> None:
    """Launch the Apex TUI cockpit."""
    ApexTuiApp(initial_ticker=ticker).run()
