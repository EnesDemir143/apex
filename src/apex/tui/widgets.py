"""Reusable Textual widgets for the Apex TUI cockpit."""

from __future__ import annotations

from decimal import Decimal

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static
from textual.containers import Horizontal

from apex.services.market_snapshot import MarketSnapshot


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
    """Price/volume/indicator display for the selected ticker."""

    DEFAULT_CSS = """
    MarketPanel {
        height: 7;
        border: solid $panel;
        padding: 0 1;
    }
    """

    ticker: reactive[str] = reactive("AAPL")
    snapshot: reactive[MarketSnapshot | None] = reactive(None)
    error: reactive[str] = reactive("")
    loading_dots: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        yield Static(self._content(), id="market-content")

    def on_mount(self) -> None:
        self.set_interval(0.45, self._tick_loading)

    def _content(self) -> str:
        if self.error:
            return f"[bold]{self.ticker}[/bold]  Market data unavailable\n  [red]{self.error}[/red]"
        if self.snapshot is None:
            dots = "." * (self.loading_dots + 1)
            return (
                f"[bold]{self.ticker}[/bold]  Fetching market snapshot{dots}\n"
                "  Open: —   High: —   Low: —   Close: —   Vol: —\n"
                "  RSI: —   MACD: —   BB: —   SMA20: —   EMA26: —"
            )
        latest = self.snapshot.latest
        indicators = self.snapshot.indicators
        return (
            f"[bold]{self.snapshot.ticker}[/bold]  source: {self.snapshot.source}\n"
            f"  Open: {_money(latest.open)}   High: {_money(latest.high)}   "
            f"Low: {_money(latest.low)}   Close: {_money(latest.close)}   Vol: {_volume(latest.volume)}\n"
            f"  RSI: {indicators.rsi:.1f}   MACD: {indicators.macd:.2f}/{indicators.macd_signal:.2f}   "
            f"BB: {indicators.bollinger_lower:.1f}-{indicators.bollinger_upper:.1f}   "
            f"SMA20: {indicators.sma20:.2f}   EMA26: {indicators.ema26:.2f}"
        )

    def watch_ticker(self, value: str) -> None:
        self.snapshot = None
        self.error = ""
        self._refresh()

    def watch_snapshot(self, value: MarketSnapshot | None) -> None:
        self._refresh()

    def watch_error(self, value: str) -> None:
        self._refresh()

    def watch_loading_dots(self, value: int) -> None:
        if self.snapshot is None and not self.error:
            self._refresh()

    def _tick_loading(self) -> None:
        if self.snapshot is None and not self.error:
            self.loading_dots = (self.loading_dots + 1) % 3

    def _refresh(self) -> None:
        try:
            self.query_one("#market-content", Static).update(self._content())
        except Exception:
            pass


class ChartPanel(Widget):
    """investing.com-style vertical chart: header → candles → date axis → volume → RSI/MACD."""

    DEFAULT_CSS = """
    ChartPanel {
        height: 1fr;
        layout: vertical;
        padding: 0;
    }
    #chart-header {
        height: 3;
        background: #161b22;
        layout: horizontal;
    }
    #chart-header-left {
        width: 1fr;
        padding: 0 1;
    }
    #chart-header-right {
        width: auto;
        padding: 0 1;
        border-left: solid #30363d;
    }
    #chart-body {
        height: 1fr;
        background: #0d1117;
        padding: 0 1 0 8;
        overflow-y: hidden;
    }
    #chart-date-axis {
        height: 2;
        background: #0d1117;
        padding: 0 0 0 8;
    }
    #chart-bar-info {
        height: 3;
        background: #0d1117;
        border-top: solid #21262d;
        padding: 0 1 0 8;
        color: #c9d1d9;
    }
    #chart-volume {
        height: 6;
        background: #0d1117;
        border-top: solid #30363d;
        padding: 0 1 0 8;
    }
    #chart-sub {
        height: 10;
        background: #0d1117;
        border-top: solid #30363d;
        padding: 0 1 0 8;
    }
    """

    ticker: reactive[str] = reactive("AAPL")
    snapshot: reactive[MarketSnapshot | None] = reactive(None)
    error: reactive[str] = reactive("")
    loading_dots: reactive[int] = reactive(0)
    timeframe: reactive[str] = reactive("1d")
    viewport_bars: reactive[int] = reactive(40)
    offset: reactive[int] = reactive(0)
    # crosshair: index into visible bars (-1 = latest / no selection)
    crosshair: reactive[int] = reactive(-1)
    # bar_select_mode: True when /x has been activated
    bar_select_mode: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        with Horizontal(id="chart-header"):
            yield Static("", id="chart-header-left")
            yield Static("", id="chart-header-right")
        yield Static("", id="chart-body")
        yield Static("", id="chart-date-axis")
        yield Static("", id="chart-bar-info")
        yield Static("", id="chart-volume")
        yield Static("", id="chart-sub")

    def on_mount(self) -> None:
        self.set_interval(0.45, self._tick_loading)
        self._refresh()

    def watch_snapshot(self, _: MarketSnapshot | None) -> None:
        self.crosshair = -1
        self._refresh()

    def watch_error(self, _: str) -> None:
        self._refresh()

    def watch_loading_dots(self, _: int) -> None:
        if self.snapshot is None and not self.error:
            self._refresh()

    def watch_timeframe(self, _: str) -> None:
        self._refresh()

    def watch_viewport_bars(self, _: int) -> None:
        self._refresh()

    def watch_offset(self, _: int) -> None:
        self._refresh()

    def watch_crosshair(self, _: int) -> None:
        self._refresh()

    def watch_bar_select_mode(self, _: bool) -> None:
        self._refresh()

    def _tick_loading(self) -> None:
        if self.snapshot is None and not self.error:
            self.loading_dots = (self.loading_dots + 1) % 3

    def _visible_bars(self) -> list:
        if not self.snapshot:
            return []
        bars = self.snapshot.bars
        end = len(bars) - self.offset
        start = max(0, end - self.viewport_bars)
        return bars[start:end]

    def _selected_bar(self):
        bars = self._visible_bars()
        if not bars:
            return None
        if self.crosshair < 0 or self.crosshair >= len(bars):
            return bars[-1]
        return bars[self.crosshair]

    # ── refresh ───────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        try:
            left, right = self._header_content()
            self.query_one("#chart-header-left", Static).update(left)
            self.query_one("#chart-header-right", Static).update(right)
            self.query_one("#chart-body", Static).update(self._body_content())
            self.query_one("#chart-date-axis", Static).update(self._date_axis_content())
            self.query_one("#chart-bar-info", Static).update(self._bar_info_content())
            self.query_one("#chart-volume", Static).update(self._volume_content())
            self.query_one("#chart-sub", Static).update(self._sub_content())
        except Exception:
            pass

    # ── header ────────────────────────────────────────────────────────────

    def _header_content(self) -> tuple[str, str]:
        if self.snapshot is None:
            dots = "." * (self.loading_dots + 1)
            left = f"[bold cyan]{self.ticker}[/bold cyan]  [dim]loading{dots}[/dim]"
            return (left, "")

        bar = self._selected_bar()
        snap = self.snapshot
        latest = snap.latest

        # price change vs previous bar
        bars = self._visible_bars()
        if len(bars) >= 2:
            prev_close = float(bars[-2].close) if self.crosshair < 0 else (
                float(bars[self.crosshair - 1].close) if self.crosshair > 0 else float(bars[0].close)
            )
        else:
            prev_close = float(latest.close)

        cur_close = float(bar.close) if bar else float(latest.close)
        change = cur_close - prev_close
        pct = (change / prev_close * 100) if prev_close else 0.0
        color = "green" if change >= 0 else "red"
        sign = "+" if change >= 0 else ""
        arrow = "▲" if change >= 0 else "▼"

        # Left: ticker, price, change
        left = (
            f"[bold cyan]{snap.ticker}[/bold cyan]  "
            f"[bold white]{cur_close:.2f}[/bold white]  "
            f"[{color}]{arrow} {sign}{change:.2f} ({sign}{pct:.2f}%)[/{color}]\n"
            f"[dim]{self.timeframe}  src:{snap.source}[/dim]"
        )

        # Right: OHLCV
        if bar:
            ts = bar.timestamp.strftime("%b %d %H:%M") if hasattr(bar.timestamp, "strftime") else ""
            right = (
                f"[dim]{ts}[/dim]\n"
                f"O [yellow]{_money(bar.open)}[/yellow]  "
                f"H [green]{_money(bar.high)}[/green]  "
                f"L [red]{_money(bar.low)}[/red]  "
                f"C [white]{_money(bar.close)}[/white]  "
                f"V [dim]{_volume(bar.volume)}[/dim]  [dim]USD[/dim]"
            )
        else:
            right = ""

        return (left, right)

    # ── candle body ───────────────────────────────────────────────────────

    def _body_content(self) -> str:
        if self.error:
            return f"[red]{self.error}[/red]"
        if self.snapshot is None:
            return ""

        bars = self._visible_bars()
        if not bars:
            return "[dim]No bars[/dim]"

        cx = self.crosshair
        return _render_candles_with_axes(bars, chart_height=16, crosshair=cx)

    def _date_axis_content(self) -> str:
        if not self.snapshot:
            return ""
        bars = self._visible_bars()
        if not bars:
            return ""
        n = len(bars)
        total_cols = n * 2  # 2-char wide candles
        separator = "[dim]" + "─" * total_cols + "[/dim]"
        date_axis = _build_date_axis(bars, width=total_cols, candle_w=2)
        return separator + "\n" + date_axis

    def _bar_info_content(self) -> str:
        """Render selected bar OHLCV detail strip below the date axis."""
        bars = self._visible_bars()
        if not bars:
            if self.bar_select_mode:
                return "[dim]  No bars loaded. Press /x after chart loads.[/dim]"
            return ""

        # Always show info for current crosshair; if no crosshair, show latest
        if self.crosshair >= 0 and self.crosshair < len(bars):
            bar = bars[self.crosshair]
            idx = self.crosshair
        else:
            bar = bars[-1]
            idx = len(bars) - 1

        # Only render content when bar_select_mode is active OR crosshair is set
        if not self.bar_select_mode and self.crosshair < 0:
            return ""

        try:
            ts = bar.timestamp.strftime("%Y-%m-%d %H:%M") if hasattr(bar.timestamp, "strftime") else str(bar.timestamp)
        except Exception:
            ts = str(bar.timestamp)

        o   = float(bar.open)
        h   = float(bar.high)
        lo  = float(bar.low)
        c   = float(bar.close)
        vol = bar.volume
        chg = c - o
        pct = (chg / o * 100) if o else 0.0
        color = "green" if chg >= 0 else "red"
        sign  = "+" if chg >= 0 else ""
        mode_hint = " [bold #58a6ff][inspect][/bold #58a6ff]  Tab ← →  Esc exit" if self.bar_select_mode else ""

        line1 = (
            f"  [dim]{ts}[/dim]  "
            f"Bar [bold]{idx + 1}[/bold]/{len(bars)}"
            f"{mode_hint}"
        )
        line2 = (
            f"  O [yellow]{o:.2f}[/yellow]"
            f"  H [green]{h:.2f}[/green]"
            f"  L [red]{lo:.2f}[/red]"
            f"  C [bold white]{c:.2f}[/bold white]"
            f"  [{color}]{sign}{chg:.2f} ({sign}{pct:.2f}%)[/{color}]"
            f"  Vol [dim]{_volume(vol)}[/dim]"
        )
        return line1 + "\n" + line2

    # ── volume ────────────────────────────────────────────────────────────

    def _volume_content(self) -> str:
        if not self.snapshot:
            return ""
        bars = self._visible_bars()
        if not bars:
            return ""
        volumes = [b.volume for b in bars]
        opens   = [float(b.open)  for b in bars]
        closes  = [float(b.close) for b in bars]
        cx = self.crosshair
        return _render_volume_panel(volumes, opens, closes, crosshair=cx)

    # ── RSI / MACD sub-panel ──────────────────────────────────────────────

    def _sub_content(self) -> str:
        if not self.snapshot:
            return ""
        bars = self._visible_bars()
        if not bars:
            return ""

        closes = [float(b.close) for b in bars]
        ind = self.snapshot.indicators

        from apex.agents.indicators import calculate_rsi
        from decimal import Decimal
        try:
            rsi_raw = calculate_rsi([Decimal(str(c)) for c in closes])
            rsi_values = [float(v) for v in rsi_raw.dropna().tolist()]
        except Exception:
            rsi_values = []

        fast = _ema_series(closes, 12)
        slow = _ema_series(closes, 26)
        hist = [f - s for f, s in zip(fast, slow)]

        rsi_line = _render_mini_line(rsi_values, height=3, lo=0.0, hi=100.0) if rsi_values else "—"
        macd_line = _render_macd_mini(closes, ind=ind)

        return (
            f"[bold]RSI[/bold] {ind.rsi:.1f}  "
            f"[bold]MACD[/bold] {ind.macd:.2f} sig {ind.macd_signal:.2f}  "
            f"[bold]SMA20[/bold] {ind.sma20:.2f}  [bold]SMA50[/bold] {ind.sma50:.2f}\n"
            f"{rsi_line}\n"
            f"{macd_line}"
        )


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
            f"  Language: English (default)\n"
            f"  Provider: OpenAI  Model: {s.llm_model}\n"
            f"  LangSmith: {ls_status}  Project: {s.langchain_project}\n"
            f"  Agents: technical, fundamental, risk, portfolio (portfolio always on)\n"
            f"  Global instructions: (none)  Per-agent: (none)\n"
            f"  [dim]Turkish output is planned for a later phase[/dim]",
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


class KeybindPanel(Widget):
    """Right-side panel showing chart keyboard shortcuts."""

    DEFAULT_CSS = """
    KeybindPanel {
        width: 22;
        background: #0d1117;
        border-left: solid #30363d;
        padding: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(self._content(), id="keybind-content")

    def _content(self) -> str:
        lines = [
            "[bold #58a6ff]── Keybinds ──[/bold #58a6ff]",
            "",
            "[dim]Navigate[/dim]",
            "  [cyan]← →[/cyan]  crosshair",
            "  [cyan]⇧← ⇧→[/cyan] pan",
            "  [cyan]+ -[/cyan]  zoom",
            "",
            "[dim]Timeframe keys[/dim]",
            "  [cyan]1[/cyan] 1m  [cyan]5[/cyan] 5m",
            "  [cyan]h[/cyan] 1h  [cyan]d[/cyan] 1d",
            "  [cyan]r[/cyan] refresh",
            "",
            "[dim]Inspect mode[/dim]",
            "  [cyan]/x[/cyan]  enter",
            "  [cyan]Tab[/cyan] prev bar",
            "  [cyan]⇧Tab[/cyan] next bar",
            "  [cyan]Esc[/cyan] exit",
            "",
            "[dim]Chart commands[/dim]",
            "  [cyan]/tf[/cyan] 1m|5m|1h|4h|1d",
            "  [cyan]/set tf[/cyan] 1d",
            "  [cyan]/refresh[/cyan]",
            "  [cyan]/zoom[/cyan] + | -",
            "  [cyan]/set[/cyan] (show help)",
            "",
            "[dim]Navigation[/dim]",
            "  [cyan]/chart[/cyan] TICKER",
            "  [cyan]/select[/cyan] TICKER",
            "  [cyan]/chat[/cyan]",
        ]
        return "\n".join(lines)



def _money(value: int | float | Decimal) -> str:
    return f"{float(value):.2f}"


def _volume(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def _sparkline(values: list[float], *, width: int = 48) -> str:
    if not values:
        return "—"
    sample = values[-width:]
    blocks = "▁▂▃▄▅▆▇█"
    low = min(sample)
    high = max(sample)
    if high == low:
        return blocks[0] * len(sample)
    scale = (len(blocks) - 1) / (high - low)
    return "".join(blocks[int((value - low) * scale)] for value in sample)


def _volume_bars(values: list[int], *, width: int = 48) -> str:
    if not values:
        return "—"
    sample = values[-width:]
    high = max(sample)
    if high <= 0:
        return "▁" * len(sample)
    blocks = "▁▂▃▄▅▆▇█"
    return "".join(blocks[int((value / high) * (len(blocks) - 1))] for value in sample)


# ── ASCII candlestick renderer ────────────────────────────────────────────────

def _render_candles(bars: list, *, chart_height: int = 22) -> str:
    """Thin wrapper kept for backward compat."""
    return _render_candles_with_axes(bars, chart_height=chart_height)


def _render_candles_with_axes(bars: list, *, chart_height: int = 22, crosshair: int = -1) -> str:
    """Render 2-char-wide candlesticks with right price axis and optional crosshair."""
    if not bars:
        return ""

    highs  = [float(b.high)  for b in bars]
    lows   = [float(b.low)   for b in bars]
    opens  = [float(b.open)  for b in bars]
    closes = [float(b.close) for b in bars]

    price_high = max(highs)
    price_low  = min(lows)
    price_range = price_high - price_low or 1.0
    n = len(bars)
    # Each candle occupies 2 columns: body/wick + gap
    CANDLE_W = 2
    total_cols = n * CANDLE_W
    PRICE_AXIS_W = 9  # chars for right price label

    def to_row(price: float) -> int:
        frac = (price - price_low) / price_range
        return max(0, min(chart_height - 1, chart_height - 1 - round(frac * (chart_height - 1))))

    # grid: rows × total_cols chars (each cell = 1 char)
    grid: list[list[str]] = [[" "] * total_cols for _ in range(chart_height)]

    for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
        col = i * CANDLE_W  # left column of this candle
        bullish = c >= o
        co = "[green]" if bullish else "[red]"
        cc = "[/green]" if bullish else "[/red]"

        wick_top = to_row(h)
        wick_bot = to_row(l)
        body_top = to_row(max(o, c))
        body_bot = to_row(min(o, c))
        if body_top == body_bot:
            body_bot = min(chart_height - 1, body_top + 1)

        for row in range(chart_height):
            if body_top <= row <= body_bot:
                grid[row][col] = co + "█" + cc
            elif wick_top <= row <= wick_bot:
                grid[row][col] = co + "╎" + cc
            # col+1 stays space (gap between candles)

    # crosshair vertical line (spans both chars of the candle)
    if 0 <= crosshair < n:
        col = crosshair * CANDLE_W
        for row in range(chart_height):
            if grid[row][col] == " ":
                grid[row][col] = "[dim]┆[/dim]"
            if col + 1 < total_cols and grid[row][col + 1] == " ":
                grid[row][col + 1] = "[dim]┆[/dim]"

    # assemble rows with right price axis
    lines: list[str] = []
    for row_idx, row in enumerate(grid):
        if row_idx % 4 == 0:
            price = price_high - (row_idx / max(chart_height - 1, 1)) * price_range
            label = f"[dim]{price:>8.2f}[/dim]"
        else:
            label = " " * PRICE_AXIS_W
        lines.append("".join(row) + label)

    # Bottom separator (date axis rendered in its own widget)
    separator = "[dim]" + "─" * total_cols + "[/dim]" + " " * PRICE_AXIS_W
    lines.append(separator)

    return "\n".join(lines)


def _build_date_axis(bars: list, *, width: int, candle_w: int = 2) -> str:
    """Build a date label row aligned to bar positions (accounts for candle_w chars per bar)."""
    if not bars:
        return ""

    n_bars = len(bars)
    row = [" "] * width

    # Detect if intraday by checking if consecutive bars are same day
    is_intraday = False
    if n_bars >= 2:
        try:
            d1 = bars[0].timestamp.date()
            d2 = bars[1].timestamp.date()
            is_intraday = (d1 == d2)
        except Exception:
            pass

    label_w = 5  # "HH:MM" or "MM/DD" are both 5 chars
    # Minimum gap between label starts = label_w + 1 space → in bar units
    min_bar_gap = max(1, (label_w + 2) // candle_w)
    # How many labels can we fit?
    max_labels = max(1, n_bars // min_bar_gap)
    # Clamp to at most 8 labels
    n_labels = min(8, max_labels)
    # Evenly spaced bar indices
    if n_labels <= 1:
        indices = [n_bars // 2]
    else:
        step = n_bars // n_labels
        indices = list(range(0, n_bars, step))[:n_labels]

    for bar_idx in indices:
        ts = bars[bar_idx].timestamp
        try:
            label = ts.strftime("%H:%M") if is_intraday else ts.strftime("%m/%d")
        except Exception:
            label = str(ts)[:5]
        # pixel position = bar_idx * candle_w, centre label
        pixel = bar_idx * candle_w
        start = max(0, pixel - len(label) // 2)
        for j, ch in enumerate(label):
            if start + j < width:
                row[start + j] = ch

    return "[cyan]" + "".join(row) + "[/cyan]"


def _render_volume_panel(
    volumes: list[int],
    opens: list[float],
    closes: list[float],
    *,
    height: int = 4,
    crosshair: int = -1,
) -> str:
    """Render volume bars colored by candle direction."""
    if not volumes:
        return ""
    max_vol = max(volumes) or 1
    n = len(volumes)
    grid: list[list[str]] = [[" "] * n for _ in range(height)]
    blocks = " ▁▂▃▄▅▆▇█"

    for i, (vol, o, c) in enumerate(zip(volumes, opens, closes)):
        frac = vol / max_vol
        filled = round(frac * height)
        bullish = c >= o
        co = "[green]" if bullish else "[red]"
        cc = "[/green]" if bullish else "[/red]"
        for row in range(height):
            depth = height - 1 - row  # 0 = bottom
            if depth < filled:
                grid[row][i] = co + "█" + cc
            elif depth == filled and frac > 0:
                idx = round(frac * height * (len(blocks) - 1)) % len(blocks)
                grid[row][i] = co + blocks[idx] + cc

    if 0 <= crosshair < n:
        for row in range(height):
            if grid[row][crosshair] == " ":
                grid[row][crosshair] = "[dim]┆[/dim]"

    # vol axis label on right
    lines = []
    for row_idx, row in enumerate(grid):
        if row_idx == 0:
            label = f"[dim]{_volume(max_vol):>8}[/dim]"
        elif row_idx == height - 1:
            label = "[dim]       0[/dim]"
        else:
            label = ""
        lines.append("".join(row) + label)

    return "\n".join(lines)


def _render_mini_line(values: list[float], *, height: int = 8, lo: float | None = None, hi: float | None = None) -> str:
    """Render a multi-row ASCII line chart from a value series."""
    if not values or height < 2:
        return _sparkline(values)

    lo = lo if lo is not None else min(values)
    hi = hi if hi is not None else max(values)
    rng = hi - lo or 1.0

    def to_row(v: float) -> int:
        return max(0, min(height - 1, height - 1 - round(((v - lo) / rng) * (height - 1))))

    rows: list[list[str]] = [[" "] * len(values) for _ in range(height)]
    prev_row = to_row(values[0])
    for col, v in enumerate(values):
        cur_row = to_row(v)
        rows[cur_row][col] = "─"
        # fill vertical gap between consecutive points
        if col > 0 and abs(cur_row - prev_row) > 1:
            r0, r1 = (prev_row, cur_row) if prev_row < cur_row else (cur_row, prev_row)
            for r in range(r0 + 1, r1):
                rows[r][col] = "│"
        prev_row = cur_row

    return "\n".join("".join(r) for r in rows)


def _render_macd_mini(closes: list[float], *, height: int = 6, ind: object) -> str:
    """Render MACD histogram as a simple bar chart."""
    # We only have the final indicator value; render a histogram sparkline
    # using the closes as a proxy for relative MACD movement.
    if len(closes) < 2:
        return "[dim]—[/dim]"

    # Approximate histogram: diff of EMA-like smoothed closes
    fast = _ema_series(closes, 12)
    slow = _ema_series(closes, 26)
    hist = [f - s for f, s in zip(fast, slow)]

    if not hist:
        return "[dim]—[/dim]"

    hi = max(abs(v) for v in hist) or 1.0
    blocks_pos = "▁▂▃▄▅▆▇█"
    blocks_neg = "▁▂▃▄▅▆▇█"
    bar_chars: list[str] = []
    for v in hist:
        idx = int((abs(v) / hi) * (len(blocks_pos) - 1))
        ch = blocks_pos[idx]
        bar_chars.append(f"[green]{ch}[/green]" if v >= 0 else f"[red]{ch}[/red]")

    return "".join(bar_chars)


def _ema_series(values: list[float], span: int) -> list[float]:
    """Simple EMA without pandas."""
    if not values:
        return []
    k = 2.0 / (span + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result
