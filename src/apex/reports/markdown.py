"""Markdown report rendering for Apex analysis results."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _signal_emoji(signal: str) -> str:
    return {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")


def _agent_output_markdown(agent_name: str, output: dict[str, Any] | None, section_title: str) -> str:
    if not output:
        return f"## {section_title}\n\n*No output produced.*\n\n"
    signal = output.get("signal", "N/A")
    confidence = output.get("confidence")
    reason = output.get("reasoning") or output.get("analysis") or ""
    lines = [
        f"## {section_title}",
        "",
        f"**Signal:** {signal}",
    ]
    if confidence is not None:
        lines.append(f"**Confidence:** {confidence:.2%}")
    source = output.get("source")
    if source:
        lines.append(f"**Source:** {source}")
    indicators = output.get("indicators")
    if indicators and isinstance(indicators, dict):
        lines.append("")
        lines.append("### Key Indicators")
        for k, v in indicators.items():
            lines.append(f"- **{k}:** {v}")
    if isinstance(reason, str) and reason.strip():
        lines.append("")
        lines.append("### Reasoning")
        lines.append(reason)
    elif isinstance(reason, dict):
        lines.append("")
        lines.append("### Reasoning")
        for k, v in reason.items():
            lines.append(f"- **{k}:** {v}")
    lines.append("")
    return "\n".join(lines)


def generate_report_markdown(result: dict[str, Any]) -> str:
    """Render the full analysis result as a formatted markdown string."""
    signal = result.get("signal", "HOLD")
    confidence = result.get("confidence", 0.0)
    ticker = result.get("ticker", "UNKNOWN")
    analysis_date = result.get("analysis_date", "unknown")
    mode = result.get("mode", "full")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# Apex Analysis Report — {ticker}",
        "",
        f"**Date:** {analysis_date} | **Generated:** {now} | **Mode:** {mode}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"{_signal_emoji(signal)} **Final Signal: {signal}**",
        "",
        f"**Confidence:** {confidence:.2%}",
        "",
    ]

    usage = result.get("usage") or {}
    if usage.get("cost_usd"):
        lines.append(f"**Cost:** ${usage['cost_usd']:.4f}")
    if usage.get("tokens_in") or usage.get("tokens_out"):
        t_in = usage.get("tokens_in", 0)
        t_out = usage.get("tokens_out", 0)
        lines.append(f"**Tokens:** {t_in:,} in / {t_out:,} out")
    lines.append("")

    errors = result.get("errors") or []
    if errors:
        lines.append("### Errors")
        for err in errors:
            lines.append(f"- ⚠️ {err}")
        lines.append("")

    lines.append("---")
    lines.append("")

    agent_outputs = result.get("agent_outputs") or {}

    aout = agent_outputs
    lines.append(_agent_output_markdown("technical_agent", aout.get("technical"), "1. Technical Analysis"))
    lines.append("---\n")
    lines.append(
        _agent_output_markdown("fundamental_agent", aout.get("fundamental"),
                                "2. Fundamental Analysis")
    )
    lines.append("---\n")
    lines.append(_agent_output_markdown("risk_agent", aout.get("risk"), "3. Risk Assessment"))
    lines.append("---\n")
    lines.append(_agent_output_markdown("portfolio_manager", aout.get("portfolio"), "4. Portfolio Decision"))
    lines.append("---\n")

    lines.append("## 5. Disagreements & Caveats")
    lines.append("")
    disagreements = _detect_disagreements(agent_outputs)
    if disagreements:
        for d in disagreements:
            lines.append(f"- {d}")
    else:
        lines.append("*No significant disagreements detected.*")
    lines.append("")

    lines.append("## 6. Cost & Token Usage")
    lines.append("")
    if usage.get("cost_usd"):
        lines.append(f"- **Total Cost:** ${usage['cost_usd']:.4f}")
    if usage.get("tokens_in") or usage.get("tokens_out"):
        lines.append(f"- **Tokens In:** {usage.get('tokens_in', 0):,}")
        lines.append(f"- **Tokens Out:** {usage.get('tokens_out', 0):,}")
    turns = usage.get("turns") or []
    if turns:
        lines.append("")
        lines.append("### Per-Agent Usage")
        for turn in turns:
            name = turn.get("agent_name", "unknown")
            t_in = turn.get("tokens_in", 0)
            t_out = turn.get("tokens_out", 0)
            cost = turn.get("cost_usd")
            cost_str = f" ${cost:.4f}" if cost else ""
            lines.append(f"- **{name}:** {t_in:,} in / {t_out:,} out{cost_str}")
    lines.append("")

    lines.append("## 7. Disclaimer")
    lines.append("")
    lines.append(
        "*This analysis is for informational and educational purposes only. "
        "It does not constitute financial advice. Past performance is not indicative "
        "of future results. Always do your own research before making investment decisions.*"
    )
    lines.append("")

    return "\n".join(lines)


def generate_section_markdown(agent_name: str, output: dict[str, Any] | None) -> str:
    """Render a single agent's output as a standalone markdown section file."""
    section_titles = {
        "technical_agent": "Technical Analysis",
        "fundamental_agent": "Fundamental Analysis",
        "risk_agent": "Risk Assessment",
        "portfolio_manager": "Portfolio Decision",
    }
    title = section_titles.get(agent_name, agent_name.replace("_", " ").title())
    return _agent_output_markdown(agent_name, output, title)


def _detect_disagreements(agent_outputs: dict[str, Any]) -> list[str]:
    """Identify conflicting signals between agents."""
    disagreements: list[str] = []
    signals: dict[str, str] = {}
    for name, key in (("technical_agent", "technical"), ("fundamental_agent", "fundamental"), ("risk_agent", "risk")):
        out = agent_outputs.get(key)
        if out and out.get("signal"):
            signals[name] = out["signal"]

    unique_signals = set(signals.values())
    if len(unique_signals) > 1:
        parts = [f"{name}: {sig}" for name, sig in signals.items()]
        disagreements.append(f"Agent signal disagreement: {' vs '.join(parts)}")

    portfolio = agent_outputs.get("portfolio") or {}
    if portfolio.get("signal") and unique_signals:
        final = portfolio["signal"]
        agent_agree = sum(1 for s in signals.values() if s == final)
        if agent_agree < len(signals) / 2:
            disagreements.append(f"Portfolio final signal ({final}) disagrees with majority of agents.")

    return disagreements
