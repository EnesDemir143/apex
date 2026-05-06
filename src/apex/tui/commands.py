"""Slash command parser and dispatch for the Apex TUI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apex.tui.state import TuiState

# Commands that are deferred to a later phase
_PLANNED: dict[str, str] = {
    "history": "Phase 15",
    "report": "Phase 15",
    "replay": "Phase 15",
    "provider": "Phase 17 (read-only display available via /model)",
    "model": "Phase 17 (read-only display available)",
}

COMMAND_HELP: dict[str, str] = {
    "chat": "/chat — return to main screen",
    "setup": "/setup — open setup configuration",
    "team": "/team — show agent team progress",
    "select": "/select TICKER — change selected ticker",
    "analyze": "/analyze [TICKER] — run analysis for selected or given ticker",
    "langsmith": "/langsmith — show LangSmith tracing status",
    "usage": "/usage — show token/cost summary from latest run",
    "tokens": "/tokens — alias for /usage",
    "cost": "/cost — alias for /usage",
    "agents": "/agents — show enabled agents",
    "events": "/events — show event log",
    "help": "/help — list all commands",
    "history": "/history — list previous runs (Phase 15)",
    "report": "/report — view latest report (Phase 15)",
    "provider": "/provider — show/switch LLM provider (Phase 17)",
    "model": "/model — show current LLM model",
}


@dataclass
class CommandResult:
    """Result of a parsed and dispatched slash command."""

    action: str  # select | analyze | info | error | help | screen
    message: str = ""
    ticker: str = ""
    planned_phase: str = ""
    title: str = ""


def parse_command(raw: str) -> tuple[str, list[str]]:
    """Parse '/cmd arg1 arg2' → (cmd, [arg1, arg2])."""
    text = raw.strip()
    if text.startswith("/"):
        text = text[1:]
    parts = text.split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def dispatch(raw: str, state: TuiState) -> CommandResult:
    """Parse and dispatch a slash command, returning a CommandResult."""
    cmd, args = parse_command(raw)

    if not cmd:
        return CommandResult(action="help", title="Help", message=_help_text())

    if cmd == "help":
        return CommandResult(action="help", title="Help", message=_help_text())

    # Screen switching
    if cmd == "chat":
        return CommandResult(action="screen", message="chat")

    if cmd == "setup":
        return CommandResult(action="screen", message="setup")

    if cmd in ("team", "agents"):
        return CommandResult(action="screen", message="team")

    if cmd == "select":
        if not args:
            return CommandResult(action="error", title="Command Error", message="Usage: /select TICKER")
        ticker = args[0].upper()
        from apex.core.constants import TICKERS_WHITELIST

        if ticker not in TICKERS_WHITELIST:
            return CommandResult(
                action="error",
                title="Command Error",
                message=f"{ticker!r} not in whitelist: {list(TICKERS_WHITELIST)}",
            )
        return CommandResult(action="select", ticker=ticker, message=f"Selected {ticker}")

    if cmd == "analyze":
        ticker = args[0].upper() if args else state.setup.ticker
        from apex.core.constants import TICKERS_WHITELIST

        if ticker not in TICKERS_WHITELIST:
            return CommandResult(
                action="error",
                title="Command Error",
                message=f"{ticker!r} not in whitelist: {list(TICKERS_WHITELIST)}",
            )
        return CommandResult(action="analyze", ticker=ticker, message=f"Analyzing {ticker}…")

    if cmd in ("usage", "tokens", "cost"):
        usage = state.analysis.usage
        if not usage:
            return CommandResult(
                action="info",
                title="Usage",
                message="Usage metrics will appear after the first analysis run.",
            )
        tokens = usage.get("total_tokens", usage.get("_extra_instructions", "—"))
        cost = usage.get("cost_usd", 0.0)
        return CommandResult(
            action="info",
            title="Usage",
            message=f"Tokens: {tokens} | Cost: ${cost:.4f}",
        )

    if cmd == "langsmith":
        from apex.core.config import get_settings

        s = get_settings()
        key_present = bool(s.langchain_api_key.get_secret_value())
        tracing = s.langchain_tracing
        project = s.langchain_project
        status = "enabled" if (key_present and tracing) else "disabled"
        key_display = "***set***" if key_present else "not set"
        return CommandResult(
            action="info",
            title="LangSmith",
            message=f"LangSmith: {status} | project={project} | key={key_display}",
        )

    if cmd == "model":
        from apex.core.config import get_settings

        s = get_settings()
        return CommandResult(action="info", title="Model", message=f"Model: {s.llm_model}")

    if cmd == "events":
        return CommandResult(action="screen", message="team")

    if cmd in _PLANNED:
        phase = _PLANNED[cmd]
        return CommandResult(
            action="info",
            title=f"/{cmd}",
            planned_phase=phase,
            message=f"/{cmd} is planned for {phase}.",
        )

    return CommandResult(action="error", title="Command Error", message=f"Unknown command: /{cmd}. Type /help.")


def _help_text() -> str:
    lines = ["Available commands:"] + [f"  {v}" for v in COMMAND_HELP.values()]
    return "\n".join(lines)
