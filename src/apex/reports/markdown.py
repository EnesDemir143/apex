"""Markdown report rendering for Apex analysis results."""

from __future__ import annotations

from datetime import datetime
from typing import Any

_TR_SECTION_TITLES: dict[str, str] = {
    "technical_agent": "1. Teknik Analiz",
    "fundamental_agent": "2. Temel Analiz",
    "risk_agent": "3. Risk Değerlendirmesi",
    "portfolio_manager": "4. Portföy Kararı",
}

_TR_KEY_LABELS: dict[str, str] = {
    "Signal": "Sinyal",
    "Confidence": "Güven",
    "Source": "Kaynak",
    "Key Indicators": "Temel Göstergeler",
    "Reasoning": "Gerekçe",
}


def _signal_emoji(signal: str) -> str:
    return {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")


def _agent_output_markdown(
    agent_name: str,
    output: dict[str, Any] | None,
    section_title: str,
    *,
    language: str = "English",
) -> str:
    if not output:
        no_output = "Hiçbir çıktı üretilmedi." if language == "Turkish" else "No output produced."
        return f"## {section_title}\n\n*{no_output}*\n\n"
    signal = output.get("signal", "N/A")
    confidence = output.get("confidence")
    reason = output.get("reasoning") or output.get("analysis") or ""
    lbl_signal = _tr_label("Signal", language)
    lbl_confidence = _tr_label("Confidence", language)
    lbl_source = _tr_label("Source", language)
    lbl_indicators = _tr_label("Key Indicators", language)
    lbl_reasoning = _tr_label("Reasoning", language)
    lines = [
        f"## {section_title}",
        "",
        f"**{lbl_signal}:** {signal}",
    ]
    if confidence is not None:
        lines.append(f"**{lbl_confidence}:** {confidence:.2%}")
    source = output.get("source")
    if source:
        lines.append(f"**{lbl_source}:** {source}")
    indicators = output.get("indicators")
    if indicators and isinstance(indicators, dict):
        lines.append("")
        lines.append(f"### {lbl_indicators}")
        for k, v in indicators.items():
            lines.append(f"- **{k}:** {v}")
    if isinstance(reason, str) and reason.strip():
        lines.append("")
        lines.append(f"### {lbl_reasoning}")
        lines.append(reason)
    elif isinstance(reason, dict):
        lines.append("")
        lines.append(f"### {lbl_reasoning}")
        for k, v in reason.items():
            lines.append(f"- **{k}:** {v}")
    lines.append("")
    return "\n".join(lines)


def _tr_label(key: str, language: str) -> str:
    if language == "Turkish":
        return _TR_KEY_LABELS.get(key, key)
    return key


def generate_report_markdown(result: dict[str, Any], *, language: str = "English") -> str:
    """Render the full analysis result as a formatted markdown string."""
    signal = result.get("signal", "HOLD")
    confidence = result.get("confidence", 0.0)
    ticker = result.get("ticker", "UNKNOWN")
    analysis_date = result.get("analysis_date", "unknown")
    mode = result.get("mode", "full")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    is_tr = language == "Turkish"

    title_prefix = "Apex Analiz Raporu" if is_tr else "Apex Analysis Report"
    lbl_date = "Tarih" if is_tr else "Date"
    lbl_generated = "Oluşturulma" if is_tr else "Generated"
    lbl_exec_summary = "Yönetici Özeti" if is_tr else "Executive Summary"
    lbl_final_signal = "Nihai Sinyal" if is_tr else "Final Signal"
    lbl_confidence = "Güven" if is_tr else "Confidence"
    lbl_cost = "Maliyet" if is_tr else "Cost"
    lbl_errors = "Hatalar" if is_tr else "Errors"
    lbl_disagreements = "Anlaşmazlıklar ve Uyarılar" if is_tr else "Disagreements & Caveats"
    no_dis = "Önemli bir anlaşmazlık tespit edilmedi."
    lbl_no_disagreements = no_dis if is_tr else "No significant disagreements detected."
    lbl_cost_token = "Maliyet ve Token Kullanımı" if is_tr else "Cost & Token Usage"
    lbl_total_cost = "Toplam Maliyet" if is_tr else "Total Cost"
    lbl_tokens_in = "Giren Token" if is_tr else "Tokens In"
    lbl_tokens_out = "Çıkan Token" if is_tr else "Tokens Out"
    lbl_per_agent = "Ajan Başına Kullanım" if is_tr else "Per-Agent Usage"
    lbl_disclaimer = "Feragatname" if is_tr else "Disclaimer"
    disclaimer_text = (
        "*Bu analiz yalnızca bilgilendirme ve eğitim amaçlıdır. "
        "Yatırım tavsiyesi niteliği taşımaz. Geçmiş performans gelecek sonuçların "
        "göstergesi değildir. Yatırım kararlarınızı vermeden önce mutlaka kendi "
        "araştırmanızı yapın.*"
        if is_tr else
        "*This analysis is for informational and educational purposes only. "
        "It does not constitute financial advice. Past performance is not indicative "
        "of future results. Always do your own research before making investment decisions.*"
    )

    lines = [
        f"# {title_prefix} — {ticker}",
        "",
        f"**{lbl_date}:** {analysis_date} | **{lbl_generated}:** {now} | **Mode:** {mode}",
        "",
        "---",
        "",
        f"## {lbl_exec_summary}",
        "",
        f"{_signal_emoji(signal)} **{lbl_final_signal}: {signal}**",
        "",
        f"**{lbl_confidence}:** {confidence:.2%}",
        "",
    ]

    usage = result.get("usage") or {}
    if usage.get("cost_usd"):
        lines.append(f"**{lbl_cost}:** ${usage['cost_usd']:.4f}")
    if usage.get("tokens_in") or usage.get("tokens_out"):
        t_in = usage.get("tokens_in", 0)
        t_out = usage.get("tokens_out", 0)
        lines.append(f"**Tokens:** {t_in:,} in / {t_out:,} out")
    lines.append("")

    errors = result.get("errors") or []
    if errors:
        lines.append(f"### {lbl_errors}")
        for err in errors:
            lines.append(f"- ⚠️ {err}")
        lines.append("")

    lines.append("---")
    lines.append("")

    agent_outputs = result.get("agent_outputs") or {}

    tr_titles = _TR_SECTION_TITLES
    en_titles = {
        "technical_agent": "1. Technical Analysis",
        "fundamental_agent": "2. Fundamental Analysis",
        "risk_agent": "3. Risk Assessment",
        "portfolio_manager": "4. Portfolio Decision",
    }
    titles = tr_titles if is_tr else en_titles

    aout = agent_outputs
    ta_title = titles["technical_agent"]
    lines.append(_agent_output_markdown("technical_agent", aout.get("technical"), ta_title, language=language))
    lines.append("---\n")
    lines.append(
        _agent_output_markdown("fundamental_agent", aout.get("fundamental"),
                                titles["fundamental_agent"], language=language)
    )
    lines.append("---\n")
    ri_title = titles["risk_agent"]
    lines.append(_agent_output_markdown("risk_agent", aout.get("risk"), ri_title, language=language))
    lines.append("---\n")
    po_title = titles["portfolio_manager"]
    lines.append(_agent_output_markdown("portfolio_manager", aout.get("portfolio"), po_title, language=language))
    lines.append("---\n")

    lines.append(f"## 5. {lbl_disagreements}")
    lines.append("")
    disagreements = _detect_disagreements(agent_outputs)
    if disagreements:
        for d in disagreements:
            lines.append(f"- {d}")
    else:
        lines.append(f"*{lbl_no_disagreements}*")
    lines.append("")

    lines.append(f"## 6. {lbl_cost_token}")
    lines.append("")
    if usage.get("cost_usd"):
        lines.append(f"- **{lbl_total_cost}:** ${usage['cost_usd']:.4f}")
    if usage.get("tokens_in") or usage.get("tokens_out"):
        lines.append(f"- **{lbl_tokens_in}:** {usage.get('tokens_in', 0):,}")
        lines.append(f"- **{lbl_tokens_out}:** {usage.get('tokens_out', 0):,}")
    turns = usage.get("turns") or []
    if turns:
        lines.append("")
        lines.append(f"### {lbl_per_agent}")
        for turn in turns:
            name = turn.get("agent_name", "unknown")
            t_in = turn.get("tokens_in", 0)
            t_out = turn.get("tokens_out", 0)
            cost = turn.get("cost_usd")
            cost_str = f" ${cost:.4f}" if cost else ""
            lines.append(f"- **{name}:** {t_in:,} in / {t_out:,} out{cost_str}")
    lines.append("")

    lines.append(f"## 7. {lbl_disclaimer}")
    lines.append("")
    lines.append(disclaimer_text)
    lines.append("")

    return "\n".join(lines)


def generate_section_markdown(agent_name: str, output: dict[str, Any] | None, *, language: str = "English") -> str:
    """Render a single agent's output as a standalone markdown section file."""
    en_titles = {
        "technical_agent": "Technical Analysis",
        "fundamental_agent": "Fundamental Analysis",
        "risk_agent": "Risk Assessment",
        "portfolio_manager": "Portfolio Decision",
    }
    if language == "Turkish":
        title = _TR_SECTION_TITLES.get(agent_name, agent_name.replace("_", " ").title())
    else:
        title = en_titles.get(agent_name, agent_name.replace("_", " ").title())
    return _agent_output_markdown(agent_name, output, title, language=language)


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
