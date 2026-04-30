"""Tests for rule-based fallback decisions."""

from __future__ import annotations

from apex.agents.fallback import rule_based_fallback


def test_rule_based_fallback_produces_valid_output() -> None:
    result = rule_based_fallback({"ticker": "AAPL", "technical_analysis": {"indicators": {"rsi": 25}}})

    decision = result["portfolio_decision"]
    assert decision["signal"] == "BUY"
    assert decision["confidence"] == 0.3
    assert decision["source"] == "rule_based"
