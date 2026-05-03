"""Unit tests for the Apex CLI."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from typer.testing import CliRunner

from apex.cli.main import app

runner = CliRunner()


def _fake_result(ticker: str = "AAPL", signal: str = "BUY", confidence: float = 0.8) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "signal": signal,
        "confidence": confidence,
        "errors": [],
        "usage": {"cost_usd": 0.001},
        "agent_outputs": {},
        "analysis_date": "2026-01-15",
        "mode": "full",
    }


# ---------------------------------------------------------------------------
# --help
# ---------------------------------------------------------------------------

def test_help_exits_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "apex" in result.output.lower()


def test_analyze_help_exits_zero() -> None:
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "ticker" in result.output.lower()


# ---------------------------------------------------------------------------
# default command (no subcommand)
# ---------------------------------------------------------------------------

def test_default_command_prints_placeholder() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Phase 14" in result.output or "cockpit" in result.output.lower()


# ---------------------------------------------------------------------------
# analyze command
# ---------------------------------------------------------------------------

def test_analyze_calls_local_analysis_and_prints_signal() -> None:
    with patch("apex.cli.main.run_local_analysis_sync", return_value=_fake_result()) as mock_fn:
        result = runner.invoke(app, ["analyze", "AAPL"])

    mock_fn.assert_called_once()
    call_kwargs = mock_fn.call_args
    assert call_kwargs.args[0] == "AAPL"
    assert result.exit_code == 0
    assert "BUY" in result.output


def test_analyze_passes_date_option() -> None:
    with patch("apex.cli.main.run_local_analysis_sync", return_value=_fake_result()) as mock_fn:
        runner.invoke(app, ["analyze", "MSFT", "--date", "2026-01-10"])

    _, kwargs = mock_fn.call_args
    assert kwargs.get("analysis_date") == "2026-01-10"


def test_analyze_passes_instructions_option() -> None:
    with patch("apex.cli.main.run_local_analysis_sync", return_value=_fake_result()) as mock_fn:
        runner.invoke(app, ["analyze", "NVDA", "--instructions", "focus on momentum"])

    _, kwargs = mock_fn.call_args
    assert kwargs.get("extra_instructions") == "focus on momentum"


def test_analyze_exits_1_on_value_error() -> None:
    with patch("apex.cli.main.run_local_analysis_sync", side_effect=ValueError("not whitelisted")):
        result = runner.invoke(app, ["analyze", "FAKE"])

    assert result.exit_code == 1
    assert "Error" in result.output


def test_analyze_exits_2_when_errors_present() -> None:
    result_with_errors = {**_fake_result(), "errors": ["agent failed"]}
    with patch("apex.cli.main.run_local_analysis_sync", return_value=result_with_errors):
        result = runner.invoke(app, ["analyze", "AAPL"])

    assert result.exit_code == 2


def test_analyze_sell_signal_renders() -> None:
    with patch("apex.cli.main.run_local_analysis_sync", return_value=_fake_result(signal="SELL", confidence=0.75)):
        result = runner.invoke(app, ["analyze", "TSLA"])

    assert "SELL" in result.output
    assert result.exit_code == 0
