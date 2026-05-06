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


@dataclass
class SetupState:
    """User-configurable setup panel values."""

    ticker: str = "AAPL"
    analysis_date: date = field(default_factory=date.today)
    depth: str = "Standard"  # Quick | Standard | Deep
    global_instructions: str = ""
    agent_instructions: dict[str, str] = field(default_factory=dict)
    enabled_agents: set[str] = field(
        default_factory=lambda: {"technical", "fundamental", "risk", "portfolio"}
    )


@dataclass
class TuiState:
    """Root TUI state shared across widgets."""

    setup: SetupState = field(default_factory=SetupState)
    analysis: AnalysisState = field(default_factory=AnalysisState)
    events: list[str] = field(default_factory=list)
    current_report: str = ""

    def add_event(self, msg: str) -> None:
        from datetime import datetime

        ts = datetime.now().strftime("%H:%M:%S")
        self.events.append(f"[{ts}] {msg}")
        # Keep last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
