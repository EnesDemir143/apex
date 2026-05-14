"""Unit tests for Turkish output / localization support."""

from __future__ import annotations

from typing import Any

from apex.reports.markdown import (
    generate_report_markdown,
    generate_section_markdown,
)
from apex.tui.commands import dispatch
from apex.tui.state import TuiState

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
        "language": "English",
        "usage": {
            "tokens_in": 1500,
            "tokens_out": 800,
            "cost_usd": 0.015,
        },
        "agent_outputs": {
            "technical": {
                "signal": "BUY",
                "confidence": 0.8,
                "indicators": {"RSI": 45.2, "MACD": "bullish"},
                "reasoning": "RSI neutral, MACD bullish crossover.",
            },
            "fundamental": {
                "signal": "HOLD",
                "confidence": 0.6,
                "reasoning": "PE ratio elevated but earnings growth solid.",
            },
            "risk": {
                "signal": "BUY",
                "confidence": 0.7,
                "risk_score": 0.25,
                "reasoning": "Low volatility environment.",
            },
            "portfolio": {
                "signal": "BUY",
                "confidence": 0.85,
                "reasoning": "Technical and risk align; fundamental caution noted.",
                "source": "llm",
            },
        },
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# English default
# ---------------------------------------------------------------------------


def test_english_default_report_contains_english_sections() -> None:
    md = generate_report_markdown(_sample_result(), language="English")
    assert "Apex Analysis Report" in md
    assert "Executive Summary" in md
    assert "Technical Analysis" in md
    assert "Fundamental Analysis" in md
    assert "Risk Assessment" in md
    assert "Portfolio Decision" in md


def test_english_report_preserves_signal_values() -> None:
    md = generate_report_markdown(_sample_result(), language="English")
    assert "BUY" in md
    assert "HOLD" in md


def test_english_report_uses_english_labels() -> None:
    md = generate_report_markdown(_sample_result(), language="English")
    assert "Signal:" in md
    assert "Confidence:" in md
    assert "Key Indicators" in md
    assert "Reasoning" in md


# ---------------------------------------------------------------------------
# Turkish mode
# ---------------------------------------------------------------------------


def test_turkish_report_contains_turkish_sections() -> None:
    md = generate_report_markdown(_sample_result(), language="Turkish")
    assert "Apex Analiz Raporu" in md
    assert "Yönetici Özeti" in md
    assert "Teknik Analiz" in md
    assert "Temel Analiz" in md
    assert "Risk Değerlendirmesi" in md
    assert "Portföy Kararı" in md


def test_turkish_report_preserves_signal_values() -> None:
    md = generate_report_markdown(_sample_result(), language="Turkish")
    assert "BUY" in md
    assert "HOLD" in md


def test_turkish_report_uses_turkish_labels() -> None:
    md = generate_report_markdown(_sample_result(), language="Turkish")
    assert "Sinyal" in md
    assert "Güven" in md
    assert "Gerekçe" in md


def test_turkish_report_includes_turkish_disclaimer() -> None:
    md = generate_report_markdown(_sample_result(), language="Turkish")
    assert "bilgilendirme ve eğitim amaçlıdır" in md


def test_turkish_report_no_output_message() -> None:
    result = _sample_result(agent_outputs={})
    md = generate_report_markdown(result, language="Turkish")
    assert "Hiçbir çıktı üretilmedi" in md


# ---------------------------------------------------------------------------
# Section markdown language support
# ---------------------------------------------------------------------------


def test_section_markdown_english() -> None:
    md = generate_section_markdown("technical_agent", {"signal": "BUY", "confidence": 0.8}, language="English")
    assert "Technical Analysis" in md
    assert "Signal:" in md


def test_section_markdown_turkish() -> None:
    md = generate_section_markdown("technical_agent", {"signal": "BUY", "confidence": 0.8}, language="Turkish")
    assert "Teknik Analiz" in md
    assert "Sinyal:" in md


# ---------------------------------------------------------------------------
# /lang TUI command
# ---------------------------------------------------------------------------


def test_lang_command_shows_current_language() -> None:
    state = TuiState()
    result = dispatch("/lang", state)
    assert result.action == "info"
    assert "English" in result.message


def test_lang_command_switches_to_turkish() -> None:
    state = TuiState()
    assert state.setup.language == "English"
    result = dispatch("/lang Turkish", state)
    assert result.action == "info"
    assert state.setup.language == "Turkish"
    assert "Turkish" in result.message


def test_lang_command_switches_to_english() -> None:
    state = TuiState()
    state.setup.language = "Turkish"
    result = dispatch("/lang English", state)
    assert result.action == "info"
    assert state.setup.language == "English"


def test_lang_command_rejects_invalid_language() -> None:
    state = TuiState()
    result = dispatch("/lang French", state)
    assert result.action == "error"
    assert state.setup.language == "English"


def test_lang_command_help_no_args() -> None:
    state = TuiState()
    result = dispatch("/lang", state)
    assert result.action == "info"


def test_lang_command_appears_in_help() -> None:
    from apex.tui.commands import COMMAND_HELP
    assert "/lang" in COMMAND_HELP["lang"]


# ---------------------------------------------------------------------------
# Metadata records language
# ---------------------------------------------------------------------------


def test_report_metadata_includes_language() -> None:
    en = _sample_result(language="English")
    tr = _sample_result(language="Turkish")
    assert en["language"] == "English"
    assert tr["language"] == "Turkish"


# ---------------------------------------------------------------------------
# English report unchanged (regression)
# ---------------------------------------------------------------------------


def test_english_report_matches_original_structure() -> None:
    md_en = generate_report_markdown(_sample_result(), language="English")
    assert md_en.startswith("# Apex Analysis Report")
    assert "## Executive Summary" in md_en
    assert "## 5. Disagreements" in md_en or "## 5. Disagreements & Caveats" in md_en
    assert "## 7. Disclaimer" in md_en
