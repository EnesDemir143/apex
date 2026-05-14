"""Slash command parser and dispatch for the Apex TUI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apex.tui.state import TuiState

VALID_AGENT_KEYS = {"technical", "fundamental", "risk"}

COMMAND_HELP: dict[str, str] = {
    "chat": "/chat — return to main screen",
    "exit": "/exit — quit Apex",
    "setup": "/setup — open setup configuration",
    "team": "/team — show agent team progress",
    "select": "/select TICKER — change selected ticker",
    "chart": "/chart [TICKER] — open terminal price/volume chart",
    "analyze": "/analyze [TICKER] — run analysis for selected or given ticker",
    "langsmith": "/langsmith — show LangSmith tracing status",
    "usage": "/usage — show token/cost summary from latest run",
    "tokens": "/tokens — alias for /usage",
    "cost": "/cost — alias for /usage",
    "agents": "/agents — show enabled agents",
    "events": "/events — show event log",
    "lang": "/lang — show or switch report language (English / Turkish)",
    "prompt": "/prompt — show or set agent prompts",
    "quant": "/quant — show or toggle Quant ML agent (requires trained models)",
    "help": "/help — list all commands",
    "history": "/history — list previous runs",
    "report": "/report — view latest report",
    "model": "/model — show current LLM model",
}

# Commands only relevant inside ChartScreen
CHART_COMMAND_HELP: dict[str, str] = {
    "inspect": "/inspect — enter bar-inspect mode (Tab to move, Enter to inspect)",
    "refresh": "/refresh — reload chart data",
    "zoom": "/zoom + | - — zoom chart in or out",
    "set-tf": "/set-tf — show timeframe options",
    "set-tf-1m": "/set-tf-1m — set timeframe to 1 minute",
    "set-tf-5m": "/set-tf-5m — set timeframe to 5 minutes",
    "set-tf-1h": "/set-tf-1h — set timeframe to 1 hour",
    "set-tf-4h": "/set-tf-4h — set timeframe to 4 hours",
    "set-tf-1d": "/set-tf-1d — set timeframe to 1 day",
    "set-tf-1w": "/set-tf-1w — set timeframe to 1 week",
}


@dataclass
class CommandResult:
    """Result of a parsed and dispatched slash command."""

    action: str  # select | analyze | chart | info | error | help | screen
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

    if cmd in ("exit", "quit"):
        return CommandResult(action="exit", title="Exit", message="Exiting Apex…")

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

    if cmd == "chart":
        ticker = args[0].upper() if args else state.setup.ticker
        from apex.core.constants import TICKERS_WHITELIST

        if ticker not in TICKERS_WHITELIST:
            return CommandResult(
                action="error",
                title="Command Error",
                message=f"{ticker!r} not in whitelist: {list(TICKERS_WHITELIST)}",
            )
        return CommandResult(action="chart", ticker=ticker, message=f"Opening chart for {ticker}")

    if cmd == "inspect":
        return CommandResult(action="bar_select", message="bar_select")

    # Chart-specific commands — handled by ChartScreen but dispatched here as fallback
    if cmd == "refresh":
        return CommandResult(action="chart_cmd", message="refresh")

    if cmd == "zoom":
        direction = args[0] if args else ""
        return CommandResult(action="chart_cmd", message=f"zoom:{direction}")

    if cmd.startswith("set-tf"):
        return CommandResult(action="chart_cmd", message=f"set-tf:{cmd}")

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

    if cmd == "lang":
        if not args:
            current = state.setup.language
            return CommandResult(
                action="info",
                title="Language",
                message=f"Current report language: {current}\nUsage: /lang English  or  /lang Turkish",
            )
        lang = args[0].capitalize()
        if lang not in ("English", "Turkish"):
            return CommandResult(
                action="error",
                title="Command Error",
                message=f"Unsupported language: {lang}. Choose English or Turkish.",
            )
        state.setup.language = lang
        return CommandResult(
            action="info",
            title="Language",
            message=f"Report language set to {lang}. Next analysis will use {lang}.",
        )

    if cmd == "quant":
        if not args:
            status = "enabled" if state.setup.quant_enabled else "disabled"
            device = state.setup.ml_device
            # Check if models exist
            from pathlib import Path

            models_path = Path("models/quant")
            models_ready = "yes" if models_path.exists() and any(models_path.glob("*.pkl")) else "no"
            return CommandResult(
                action="info",
                title="Quant ML Agent",
                message=(
                    f"Quant ML Agent: {status}\n"
                    f"ML Device: {device}\n"
                    f"Models trained: {models_ready}\n"
                    f"Usage: /quant on | /quant off  to toggle\n"
                    f"       /quant device auto|cpu|mps|cuda  to set device"
                ),
            )

        sub = args[0].lower()
        if sub in ("on", "enable", "1", "true"):
            state.setup.quant_enabled = True
            return CommandResult(
                action="info",
                title="Quant ML Agent",
                message="Quant ML Agent enabled. Next analysis will include quant signal.",
            )
        elif sub in ("off", "disable", "0", "false"):
            state.setup.quant_enabled = False
            return CommandResult(
                action="info", title="Quant ML Agent", message="Quant ML Agent disabled. LLM-only analysis."
            )
        elif sub == "device" and len(args) >= 2:
            device = args[1].lower()
            if device in ("auto", "cpu", "mps", "cuda"):
                state.setup.ml_device = device
                return CommandResult(action="info", title="Quant ML Agent", message=f"ML device set to {device}.")
            return CommandResult(
                action="error",
                title="Command Error",
                message=f"Unsupported device: {device}. Options: auto, cpu, mps, cuda.",
            )
        else:
            return CommandResult(
                action="error", title="Command Error", message=f"Unknown quant option: {sub}. Try: on, off, device."
            )

    if cmd == "prompt":
        if not args:
            global_inst = state.setup.global_instructions or "(none)"
            agent_lines = []
            for name in ("technical", "fundamental", "risk"):
                val = state.setup.agent_instructions.get(name)
                agent_lines.append(f"  {name}: {val or '(none)'}")
            return CommandResult(
                action="info",
                title="Agent Prompts",
                message=(
                    f"Global: {global_inst}\n"
                    f"{chr(10).join(agent_lines)}\n\n"
                    f"Usage:\n"
                    f'  /prompt global "text"\n'
                    f'  /prompt technical "text"\n'
                    f'  /prompt fundamental "text"\n'
                    f'  /prompt risk "text"\n'
                    f"  /prompt clear"
                ),
            )

        sub = args[0].lower()
        rest = " ".join(args[1:]) if len(args) > 1 else ""

        if sub == "clear":
            state.setup.global_instructions = ""
            state.setup.agent_instructions = {}
            return CommandResult(action="info", title="Agent Prompts", message="All agent prompts cleared.")

        if sub == "global":
            state.setup.global_instructions = rest
            return CommandResult(
                action="info",
                title="Agent Prompts",
                message=f"Global instruction set: {rest}" if rest else "Global instruction cleared.",
            )

        if sub in VALID_AGENT_KEYS:
            if rest:
                state.setup.agent_instructions[sub] = rest
            else:
                state.setup.agent_instructions.pop(sub, None)
            return CommandResult(
                action="info",
                title="Agent Prompts",
                message=f"Prompt for {sub}: {rest}" if rest else f"Prompt for {sub} cleared.",
            )

        return CommandResult(
            action="error",
            title="Command Error",
            message=f"Unknown agent: {sub}. Valid: global, technical, fundamental, risk.",
        )

    return CommandResult(action="error", title="Command Error", message=f"Unknown command: /{cmd}. Type /help.")


def _help_text() -> str:
    lines = ["Available commands:"] + [f"  {v}" for v in COMMAND_HELP.values()]
    return "\n".join(lines)
