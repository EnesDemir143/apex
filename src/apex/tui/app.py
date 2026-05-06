"""Apex Textual terminal cockpit — ApexTuiApp."""

from __future__ import annotations

import time
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, OptionList
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
    """Command palette overlay."""

    DEFAULT_CSS = """
    CommandPalette {
        display: none;
        layer: overlay;
        align: center middle;
        width: 60;
        height: auto;
        max-height: 20;
        background: $panel;
        border: thick $accent;
        offset: 50% 50%;
    }

    CommandPalette.visible {
        display: block;
    }
    """

    def compose(self) -> ComposeResult:
        options = [Option(desc, id=cmd) for cmd, desc in COMMAND_HELP.items()]
        yield OptionList(*options, id="command-options")

    def show_palette(self) -> None:
        self.add_class("visible")
        self.query_one("#command-options", OptionList).focus()

    def hide_palette(self) -> None:
        self.remove_class("visible")

CSS_PATH = "apex.tcss"


class ChatScreen(Screen[None]):
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

    def action_close_palette(self) -> None:
        """Close command palette."""
        palette = self.query_one("#command-palette", CommandPalette)
        palette.hide_palette()
        self.query_one("#command-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show palette when / is typed."""
        if event.value == "/":
            palette = self.query_one("#command-palette", CommandPalette)
            palette.show_palette()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle command selection from palette."""
        palette = self.query_one("#command-palette", CommandPalette)
        palette.hide_palette()

        cmd = f"/{event.option_id}"
        input_widget = self.query_one("#command-input", Input)
        input_widget.value = cmd
        # Trigger submit by posting the event
        self.post_message(Input.Submitted(input_widget, cmd))


class SetupScreen(Screen[None]):
    """Setup configuration screen."""

    BINDINGS = []

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


class TeamScreen(Screen[None]):
    """Agent team progress screen."""

    BINDINGS = []

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

CSS_PATH = "apex.tcss"


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
            self._show_output(result.message)
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
            self._show_output(f"Analysis failed: {exc}")
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

    def _show_output(self, msg: str) -> None:
        try:
            screen = self.screen
            screen.query_one("#report-panel", ReportPanel).update_report(msg)
        except Exception:
            pass

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
