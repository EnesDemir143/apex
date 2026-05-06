"""Apex Textual terminal cockpit — ApexTuiApp."""

from __future__ import annotations

import time
from typing import Any, cast

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, OptionList, Static
from textual.widgets.option_list import Option

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
        if not value.startswith("/") or " " in value:
            self.hide_palette()
            return

        query = value[1:].strip().lower()
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
        """Close command palette."""
        screen = cast(Screen[None], self)
        palette = screen.query_one("#command-palette", CommandPalette)
        palette.hide_palette()
        screen.query_one("#command-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show and filter the command palette for slash input."""
        screen = cast(Screen[None], self)
        palette = screen.query_one("#command-palette", CommandPalette)
        palette.update_query(event.value)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle command selection from palette."""
        screen = cast(Screen[None], self)
        palette = screen.query_one("#command-palette", CommandPalette)
        palette.hide_palette()

        if event.option_id == "__no_match__":
            return

        cmd = f"/{event.option_id}"
        input_widget = screen.query_one("#command-input", Input)
        input_widget.value = cmd
        screen.post_message(Input.Submitted(input_widget, cmd))


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

        if result.action == "select":
            self._state.setup.ticker = result.ticker
            self._sync_ticker(result.ticker)
            self._push_event(result.message)

        elif result.action == "analyze":
            ticker = result.ticker or self._state.setup.ticker
            self._state.setup.ticker = ticker
            self._sync_ticker(ticker)
            self._push_event(result.message)
            self._run_analysis_worker(ticker)

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
