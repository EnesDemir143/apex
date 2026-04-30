"""Reusable card components for signal and metric display."""

from __future__ import annotations

import streamlit as st

_SIGNAL_COLORS = {"BUY": "#00D4AA", "SELL": "#FF4B4B", "HOLD": "#FFD700"}
_SIGNAL_ICONS = {"BUY": "▲", "SELL": "▼", "HOLD": "◆"}


def signal_hero_card(ticker: str, signal: str, confidence: float, status: str = "completed") -> None:
    """Large hero card showing the latest signal for a ticker."""
    color = _SIGNAL_COLORS.get(signal, "#FAFAFA")
    icon = _SIGNAL_ICONS.get(signal, "?")
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1A1F2E 0%, #0E1117 100%);
            border: 1px solid {color}44;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 24px 28px;
            margin-bottom: 16px;
        ">
            <div style="font-size:13px; color:#888; text-transform:uppercase; letter-spacing:2px;">{ticker}</div>
            <div style="font-size:48px; font-weight:700; color:{color}; margin:8px 0;">{icon} {signal}</div>
            <div style="font-size:16px; color:#FAFAFA;">Confidence: <b>{confidence:.0%}</b></div>
            <div style="font-size:12px; color:#666; margin-top:8px;">Status: {status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def agent_decision_card(agent_name: str, signal: str | None, confidence: float | None, summary: str = "") -> None:
    """Card for an individual agent's decision."""
    color = _SIGNAL_COLORS.get(signal or "HOLD", "#888")
    label = signal or "N/A"
    conf_str = f"{confidence:.0%}" if confidence is not None else "—"
    st.markdown(
        f"""
        <div style="
            background:#1A1F2E; border:1px solid #2A2F3E;
            border-top: 3px solid {color};
            border-radius:6px; padding:16px; margin-bottom:8px;
        ">
            <div style="font-size:11px; color:#888; text-transform:uppercase; letter-spacing:1px;">{agent_name}</div>
            <div style="font-size:22px; font-weight:600; color:{color};">{label}</div>
            <div style="font-size:13px; color:#AAA;">Confidence: {conf_str}</div>
            {f'<div style="font-size:12px; color:#666; margin-top:6px;">{summary[:120]}</div>' if summary else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
