"""Agent Consensus panel — 4 agents, stance + one-line explanation."""

from __future__ import annotations

import streamlit as st

_AGENT_ICONS = {
    "technical":   "⚙️",
    "fundamental": "📊",
    "risk":        "🛡️",
    "portfolio":   "🎯",
}
_AGENT_LABELS = {
    "technical":   "Technical Agent",
    "fundamental": "Fundamental Agent",
    "risk":        "Risk Agent",
    "portfolio":   "Portfolio Manager",
}


def agent_consensus_panel(consensus: dict) -> None:
    """Render 4-agent consensus rows matching the mockup."""
    for key in ["technical", "fundamental", "risk", "portfolio"]:
        data   = consensus.get(key, {})
        icon   = _AGENT_ICONS[key]
        label  = _AGENT_LABELS[key]
        stance = data.get("stance", "—")
        color  = data.get("color", "#888")
        summary = data.get("summary", "")

        st.markdown(
            f"""
            <div style="
                display:flex;align-items:center;gap:12px;
                padding:10px 12px;
                border-bottom:1px solid #1E2535;
            ">
                <div style="
                    width:36px;height:36px;border-radius:50%;
                    background:{color}22;border:1px solid {color}55;
                    display:flex;align-items:center;justify-content:center;
                    font-size:16px;flex-shrink:0;
                ">{icon}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:12px;color:#888;">{label}</div>
                    <div style="font-size:13px;color:#F0F0F0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        <span style="color:{color};font-weight:600;">{stance}</span>
                        &nbsp;·&nbsp;
                        <span style="color:#AAA;">{summary}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
