"""Unit tests for report generation (markdown + writer)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apex.reports.markdown import generate_report_markdown, generate_section_markdown
from apex.reports.writer import ReportWriter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _sample_result(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "ticker": "AAPL",
        "signal": "BUY",
        "confidence": 0.85,
        "errors": [],
        "analysis_date": "2026-01-15",
        "mode": "full",
        "request_hash": "abc123",
        "cached": False,
        "usage": {
            "tokens_in": 1500,
            "tokens_out": 800,
            "cost_usd": 0.015,
            "turns": [
                {"agent_name": "technical_agent", "tokens_in": 500,
                 "tokens_out": 200, "cost_usd": 0.005},
                {"agent_name": "portfolio_manager", "tokens_in": 300,
                 "tokens_out": 400, "cost_usd": 0.004},
            ],
        },
        "agent_outputs": {
            "technical": {
                "signal": "BUY", "confidence": 0.8,
                "indicators": {"RSI": 45.2, "MACD": "bullish"},
                "reasoning": "RSI neutral, MACD bullish crossover.",
            },
            "fundamental": {
                "signal": "HOLD", "confidence": 0.6,
                "reasoning": "PE ratio elevated but earnings growth solid.",
            },
            "risk": {
                "signal": "BUY", "confidence": 0.7,
                "risk_score": 0.25,
                "reasoning": "Low volatility environment.",
            },
            "portfolio": {
                "signal": "BUY", "confidence": 0.85,
                "reasoning": "Technical and risk align; fundamental caution noted.",
                "source": "llm",
            },
        },
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# generate_report_markdown
# ---------------------------------------------------------------------------


def test_report_markdown_includes_signal_and_confidence() -> None:
    md = generate_report_markdown(_sample_result())
    assert "BUY" in md
    assert "85.00%" in md or "0.85%" in md


def test_report_markdown_includes_ticker_and_date() -> None:
    md = generate_report_markdown(_sample_result())
    assert "AAPL" in md
    assert "2026-01-15" in md


def test_report_markdown_includes_cost_and_tokens() -> None:
    md = generate_report_markdown(_sample_result())
    assert "$0.015" in md
    assert "1,500" in md
    assert "800" in md


def test_report_markdown_includes_disclaimer() -> None:
    md = generate_report_markdown(_sample_result())
    assert "financial advice" in md.lower()


def test_report_markdown_all_sections_present() -> None:
    md = generate_report_markdown(_sample_result())
    assert "Technical Analysis" in md
    assert "Fundamental Analysis" in md
    assert "Risk Assessment" in md
    assert "Portfolio Decision" in md
    assert "Disagreements" in md
    assert "Cost & Token Usage" in md


def test_report_markdown_no_errors_shows_clean() -> None:
    md = generate_report_markdown(_sample_result())
    assert "Errors" not in md or "⚠" not in md


def test_report_markdown_shows_errors_when_present() -> None:
    md = generate_report_markdown(_sample_result(errors=["Agent timeout", "Low confidence"]))
    assert "Agent timeout" in md


def test_report_markdown_disagreement_detected() -> None:
    result = _sample_result()
    result["agent_outputs"]["technical"] = {"signal": "SELL", "confidence": 0.7, "reasoning": "Bearish."}
    result["agent_outputs"]["fundamental"] = {"signal": "BUY", "confidence": 0.8, "reasoning": "Bullish."}
    md = generate_report_markdown(result)
    assert "disagreement" in md.lower()


def test_report_markdown_empty_agent_outputs() -> None:
    md = generate_report_markdown(_sample_result(agent_outputs={}))
    assert "No output produced" in md


# ---------------------------------------------------------------------------
# generate_section_markdown
# ---------------------------------------------------------------------------


def test_section_markdown_known_agent() -> None:
    md = generate_section_markdown("technical_agent", {"signal": "BUY", "confidence": 0.8})
    assert "Technical Analysis" in md
    assert "BUY" in md


def test_section_markdown_none_output() -> None:
    md = generate_section_markdown("technical_agent", None)
    assert "No output produced" in md


# ---------------------------------------------------------------------------
# ReportWriter
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_reports(tmp_path: Path) -> Path:
    base = tmp_path / "reports"
    base.mkdir()
    return base


def test_writer_creates_report_directory(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result())
    assert report_dir.exists()
    assert report_dir.name.count("_") == 1  # timestamp format YYYYMMDD_HHMMSS


def test_writer_creates_complete_report(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result())
    assert (report_dir / "complete_report.md").exists()
    content = (report_dir / "complete_report.md").read_text(encoding="utf-8")
    assert "AAPL" in content
    assert "BUY" in content


def test_writer_creates_section_folders(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result())
    assert (report_dir / "1_technical" / "technical.md").exists()
    assert (report_dir / "2_fundamental" / "fundamental.md").exists()
    assert (report_dir / "3_risk" / "risk.md").exists()
    assert (report_dir / "4_portfolio" / "decision.md").exists()


def test_writer_creates_state_json(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    state = {"key": "value", "nested": {"a": 1}}
    report_dir = writer.save(_sample_result(), state=state)
    state_file = report_dir / "state.json"
    assert state_file.exists()
    loaded = json.loads(state_file.read_text(encoding="utf-8"))
    assert loaded["key"] == "value"


def test_writer_creates_metadata_json(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result())
    meta_file = report_dir / "metadata.json"
    assert meta_file.exists()
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    assert meta["ticker"] == "AAPL"
    assert meta["signal"] == "BUY"
    assert meta["request_hash"] == "abc123"


def test_writer_load_report(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result(), state={"test": True})
    loaded = ReportWriter.load_report(report_dir)
    assert "report_md" in loaded
    assert "state" in loaded
    assert "metadata" in loaded
    assert loaded["state"]["test"] is True


def test_writer_missing_report_load_graceful(tmp_reports: Path) -> None:
    loaded = ReportWriter.load_report(tmp_reports / "nonexistent")
    assert loaded == {}


def test_writer_none_state_skips_state_json(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result(), state=None)
    assert not (report_dir / "state.json").exists()


def test_writer_nested_ticker_directory(tmp_reports: Path) -> None:
    writer = ReportWriter(base_dir=tmp_reports)
    report_dir = writer.save(_sample_result(ticker="TSLA"))
    assert "TSLA" in str(report_dir)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_report_with_disagreements_caveats_section() -> None:
    result = _sample_result()
    result["agent_outputs"]["technical"] = {"signal": "SELL", "confidence": 0.9, "reasoning": "Bearish divergence."}
    result["agent_outputs"]["risk"] = {"signal": "SELL", "confidence": 0.8, "reasoning": "High risk."}
    md = generate_report_markdown(result)
    assert "disagreement" in md.lower() or "SELL" in md
