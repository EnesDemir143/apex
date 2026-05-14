"""TUI application state dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class AnalysisState:
    """Tracks the current analysis run state."""

    status: str = "idle"  # idle | running | completed | error
    ticker: str = ""
    signal: str = ""
    confidence: float = 0.0
    errors: list[str] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    agent_outputs: dict[str, Any] = field(default_factory=dict)
    analysis_date: str = ""
    quant_output: dict[str, Any] = field(default_factory=dict)


@dataclass
class SetupState:
    """User-configurable setup panel values."""

    ticker: str = "AAPL"
    analysis_date: date = field(default_factory=date.today)
    depth: str = "Standard"  # Quick | Standard | Deep
    language: str = "English"
    global_instructions: str = ""
    agent_instructions: dict[str, str] = field(default_factory=dict)
    enabled_agents: set[str] = field(
        default_factory=lambda: {"technical", "fundamental", "risk", "portfolio"}
    )
    quant_enabled: bool = False
    ml_device: str = "auto"  # auto | cpu | mps | cuda


@dataclass
class ChartViewport:
    """Chart pan/zoom/timeframe state."""

    timeframe: str = "1d"          # 1m | 5m | 1h | 1d
    viewport_bars: int = 60        # how many bars to show
    offset: int = 0                # pan offset from the right (0 = latest)


@dataclass
class TuiState:
    """Root TUI state shared across widgets."""

    setup: SetupState = field(default_factory=SetupState)
    analysis: AnalysisState = field(default_factory=AnalysisState)
    chart: ChartViewport = field(default_factory=ChartViewport)
    events: list[str] = field(default_factory=list)
    current_report: str = ""

    def add_event(self, msg: str) -> None:
        from datetime import datetime

        ts = datetime.now().strftime("%H:%M:%S")
        self.events.append(f"[{ts}] {msg}")
        # Keep last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
