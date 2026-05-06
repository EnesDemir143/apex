"""Unit tests for TUI slash command parser and dispatch."""

from __future__ import annotations

import pytest

from apex.tui.commands import dispatch, parse_command
from apex.tui.state import TuiState

# ── parse_command ─────────────────────────────────────────────────────────────


def test_parse_command_with_slash() -> None:
    cmd, args = parse_command("/select AAPL")
    assert cmd == "select"
    assert args == ["AAPL"]


def test_parse_command_without_slash() -> None:
    cmd, args = parse_command("analyze MSFT")
    assert cmd == "analyze"
    assert args == ["MSFT"]


def test_parse_command_empty() -> None:
    cmd, args = parse_command("")
    assert cmd == ""
    assert args == []


def test_parse_command_no_args() -> None:
    cmd, args = parse_command("/help")
    assert cmd == "help"
    assert args == []


# ── dispatch helpers ──────────────────────────────────────────────────────────


@pytest.fixture()
def state() -> TuiState:
    return TuiState()


# /help


def test_help_command(state: TuiState) -> None:
    result = dispatch("/help", state)
    assert result.action == "help"
    assert "/select" in result.message
    assert "/analyze" in result.message


def test_empty_input_returns_help(state: TuiState) -> None:
    result = dispatch("/", state)
    assert result.action == "help"


# /select


def test_select_valid_ticker(state: TuiState) -> None:
    result = dispatch("/select AAPL", state)
    assert result.action == "select"
    assert result.ticker == "AAPL"


def test_select_missing_arg(state: TuiState) -> None:
    result = dispatch("/select", state)
    assert result.action == "error"
    assert "Usage" in result.message


def test_select_non_whitelisted(state: TuiState) -> None:
    result = dispatch("/select FAKE", state)
    assert result.action == "error"
    assert "whitelist" in result.message.lower()


# /analyze


def test_analyze_with_ticker(state: TuiState) -> None:
    result = dispatch("/analyze AAPL", state)
    assert result.action == "analyze"
    assert result.ticker == "AAPL"


def test_analyze_uses_state_ticker(state: TuiState) -> None:
    state.setup.ticker = "MSFT"
    result = dispatch("/analyze", state)
    assert result.action == "analyze"
    assert result.ticker == "MSFT"


def test_analyze_non_whitelisted(state: TuiState) -> None:
    result = dispatch("/analyze FAKE", state)
    assert result.action == "error"


# /langsmith


def test_langsmith_shows_status(state: TuiState) -> None:
    result = dispatch("/langsmith", state)
    assert result.action == "info"
    assert result.title == "LangSmith"
    assert "LangSmith" in result.message
    # Key must never be printed in full — only present/missing
    assert "sk-" not in result.message


# /usage, /tokens, /cost


def test_usage_no_run(state: TuiState) -> None:
    result = dispatch("/usage", state)
    assert result.action == "info"
    assert result.title == "Usage"
    assert "Usage metrics" in result.message
    assert "No analysis" not in result.message


def test_tokens_alias(state: TuiState) -> None:
    result = dispatch("/tokens", state)
    assert result.action == "info"


def test_cost_alias(state: TuiState) -> None:
    result = dispatch("/cost", state)
    assert result.action == "info"


def test_usage_with_data(state: TuiState) -> None:
    state.analysis.usage = {"total_tokens": 500, "cost_usd": 0.0025}
    result = dispatch("/usage", state)
    assert result.action == "info"
    assert result.title == "Usage"
    assert "500" in result.message
    assert "0.0025" in result.message


# /model


def test_model_shows_model(state: TuiState) -> None:
    result = dispatch("/model", state)
    assert result.action == "info"
    assert result.title == "Model"
    assert "Model:" in result.message


# /agents


def test_agents_switches_to_team_screen(state: TuiState) -> None:
    result = dispatch("/agents", state)
    assert result.action == "screen"
    assert result.message == "team"


# /settings


def test_settings_shows_ticker(state: TuiState) -> None:
    state.setup.ticker = "NVDA"
    result = dispatch("/settings", state)
    assert result.action == "info"
    assert result.title == "Settings"
    assert "NVDA" in result.message


# /events


def test_events_switches_to_team_screen(state: TuiState) -> None:
    result = dispatch("/events", state)
    assert result.action == "screen"
    assert result.message == "team"


# Planned commands return info, not error


@pytest.mark.parametrize("cmd", ["/history", "/report"])
def test_planned_commands_return_info(cmd: str, state: TuiState) -> None:
    result = dispatch(cmd, state)
    assert result.action == "info"
    assert "Phase" in result.message


# Unknown command


def test_unknown_command(state: TuiState) -> None:
    result = dispatch("/xyzzy", state)
    assert result.action == "error"
    assert "Unknown" in result.message
