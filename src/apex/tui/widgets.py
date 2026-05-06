"""Reusable Textual widgets for the Apex TUI cockpit."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static


class TickerSelector(Widget):
    """Top-bar ticker selector showing the active ticker."""

    DEFAULT_CSS = """
    TickerSelector {
        height: 3;
        border: solid $accent;
        padding: 0 1;
    }
    """

    ticker: reactive[str] = reactive("AAPL")

    def compose(self) -> ComposeResult:
        yield Label(self._label(), id="ticker-label")

    def _label(self) -> str:
        return f"[bold cyan]▶ {self.ticker}[/bold cyan]  (type /select TICKER to change)"

    def watch_ticker(self, value: str) -> None:
        try:
            self.query_one("#ticker-label", Label).update(self._label())
        except Exception:
            pass


class MarketPanel(Widget):
    """Placeholder for price/volume/indicator display."""

    DEFAULT_CSS = """
    MarketPanel {
        height: 7;
        border: solid $panel;
        padding: 0 1;
    }
    """

    ticker: reactive[str] = reactive("AAPL")

    def compose(self) -> ComposeResult:
        yield Static(self._content(), id="market-content")

    def _content(self) -> str:
        return (
            f"[bold]{self.ticker}[/bold]  Price/Volume/Indicators placeholder\n"
            "  Open: —   High: —   Low: —   Close: —   Vol: —\n"
            "  RSI: —   MACD: —   BB: —   SMA20: —   EMA50: —"
        )

    def watch_ticker(self, value: str) -> None:
        try:
            self.query_one("#market-content", Static).update(self._content())
        except Exception:
            pass


class SetupPanel(Widget):
    """Setup panel: ticker, date, depth, provider/model, LangSmith, agents, instructions."""

    DEFAULT_CSS = """
    SetupPanel {
        height: auto;
        border: solid $panel;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        from datetime import date

        from apex.core.config import get_settings
        from apex.core.constants import TICKERS_WHITELIST

        s = get_settings()
        key_present = bool(s.langchain_api_key.get_secret_value())
        ls_status = "✓ configured" if key_present else "✗ not set"
        tickers = " | ".join(TICKERS_WHITELIST)
        yield Static(
            f"[bold]Setup[/bold]\n"
            f"  Tickers available: {tickers}\n"
            f"  Date: {date.today()}  Depth: Standard\n"
            f"  Provider: OpenAI  Model: {s.llm_model}\n"
            f"  LangSmith: {ls_status}  Project: {s.langchain_project}\n"
            f"  Agents: technical, fundamental, risk, portfolio (portfolio always on)\n"
            f"  Global instructions: (none)  Per-agent: (none)\n"
            f"  [dim]Edit via /settings or the setup form[/dim]",
            id="setup-content",
        )


class AgentProgressTable(Widget):
    """Team-based agent progress table."""

    DEFAULT_CSS = """
    AgentProgressTable {
        height: 10;
        border: solid $panel;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(self._table_text(), id="progress-content")

    def _table_text(self) -> str:
        rows = [
            ("Analysis", "Technical Agent", "idle"),
            ("Analysis", "Fundamental Agent", "idle"),
            ("Risk", "Risk Agent", "idle"),
            ("Decision", "Portfolio Manager", "idle"),
        ]
        lines = ["[bold]Team          Agent                Status[/bold]"]
        for team, agent, status in rows:
            lines.append(f"  {team:<14}{agent:<22}{status}")
        return "\n".join(lines)

    def update_status(self, agent: str, status: str) -> None:
        """Update a single agent's status row."""
        try:
            self.query_one("#progress-content", Static).update(self._table_text())
        except Exception:
            pass


class EventLog(Widget):
    """Timestamped event log panel."""

    DEFAULT_CSS = """
    EventLog {
        height: 10;
        border: solid $panel;
        padding: 0 1;
        overflow-y: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield ListView(id="event-list")

    def push_event(self, msg: str) -> None:
        try:
            lv = self.query_one("#event-list", ListView)
            lv.append(ListItem(Label(msg)))
            lv.scroll_end(animate=False)
        except Exception:
            pass


class ReportPanel(Widget):
    """Current report / result display panel."""

    DEFAULT_CSS = """
    ReportPanel {
        height: 12;
        border: solid $panel;
        padding: 0 1;
        overflow-y: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[dim]Run /analyze TICKER to create a report.[/dim]", id="report-content")

    def update_report(self, content: str) -> None:
        try:
            self.query_one("#report-content", Static).update(content)
        except Exception:
            pass


class FooterStats(Widget):
    """Footer: agents done, tokens, cost, elapsed, LangSmith hint."""

    DEFAULT_CSS = """
    FooterStats {
        height: 3;
        border: solid $panel;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(self._footer_text(0, 4, 0, 0.0, 0.0), id="footer-content")

    def _footer_text(
        self,
        done: int,
        total: int,
        tokens: int,
        cost: float,
        elapsed: float,
    ) -> str:
        return (
            f"Agents: {done}/{total}  |  Tokens: {tokens}  |  "
            f"Cost: ${cost:.4f}  |  Elapsed: {elapsed:.1f}s  |  "
            f"[dim]/langsmith for tracing status[/dim]"
        )

    def update_stats(
        self,
        done: int = 0,
        total: int = 4,
        tokens: int = 0,
        cost: float = 0.0,
        elapsed: float = 0.0,
    ) -> None:
        try:
            self.query_one("#footer-content", Static).update(
                self._footer_text(done, total, tokens, cost, elapsed)
            )
        except Exception:
            pass
