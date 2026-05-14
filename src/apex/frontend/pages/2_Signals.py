"""Signals — full agent signal leaderboard."""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.core.constants import TICKERS_WHITELIST
from apex.frontend.api_client import fetch_all_signals, fetch_analysis
from apex.frontend.components.agent_consensus import agent_consensus_panel
from apex.frontend.components.latest_analysis import latest_analysis_card
from apex.frontend.components.signal_table import signal_leaderboard
from apex.frontend.components.tradingview_widget import tradingview_chart
from apex.frontend.mock_data import (
    ALL_SIGNALS as _MOCK_ALL_SIGNALS,
    get_consensus as _mock_get_consensus,
    get_latest_analysis as _mock_get_latest_analysis,
)

st.set_page_config(page_title="Signals — Apex", page_icon="⚡", layout="wide")

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "AAPL"

st.title("⚡ Signals")
st.caption("All agent signals — click a symbol to inspect.")

# ── Fetch live signals ─────────────────────────────────────────────────────
with st.spinner("Loading signals…"):
    live_signals = fetch_all_signals(TICKERS_WHITELIST)

api_available = bool(live_signals)
all_signals = live_signals if api_available else _MOCK_ALL_SIGNALS

if not api_available:
    st.warning("⚠️ API unavailable — showing cached demo data.", icon="⚠️")


# ── Consensus / latest analysis helpers ───────────────────────────────────
def _get_consensus(symbol: str) -> dict:  # type: ignore[type-arg]
    if not api_available:
        return _mock_get_consensus(symbol)
    result = fetch_analysis(symbol)
    if result is None:
        return _mock_get_consensus(symbol)
    agent_outputs = (result.get("summary") or {}).get("agent_outputs") or {}
    signal = result.get("signal", "HOLD")
    color_map = {"BUY": "#00D4AA", "SELL": "#FF4B4B", "HOLD": "#FFD700"}
    color = color_map.get(signal, "#FFD700")
    consensus: dict = {}  # type: ignore[type-arg]
    for agent_name in ("technical", "fundamental", "risk"):
        agent_data = agent_outputs.get(agent_name) or {}
        summary = agent_data.get("reasoning") or agent_data.get("risk_factors") or "Analysis complete."
        consensus[agent_name] = {
            "stance": agent_data.get("signal", signal),
            "color": color,
            "summary": summary,
        }
    consensus["portfolio"] = {"stance": signal, "color": color, "summary": "Synthesis complete."}
    return consensus


def _get_latest_analysis(symbol: str) -> dict:  # type: ignore[type-arg]
    if not api_available:
        return _mock_get_latest_analysis(symbol)
    result = fetch_analysis(symbol)
    if result is None:
        return _mock_get_latest_analysis(symbol)
    confidence: float = result.get("confidence", 0.0) or 0.0
    risk = "Low" if confidence >= 0.7 else ("Medium" if confidence >= 0.5 else "High")
    agent_outputs = (result.get("summary") or {}).get("agent_outputs") or {}
    pm_data = agent_outputs.get("portfolio_manager") or {}
    explanation = pm_data.get("reasoning") or f"{result.get('signal', 'HOLD')} signal with {confidence:.0%} confidence."
    return {
        "signal": result.get("signal", "HOLD"),
        "confidence": confidence,
        "risk": risk,
        "last_analysis": "just now",
        "explanation": explanation,
    }


# Filters
f1, f2, f3 = st.columns([1, 1, 2])
sig_filter = f1.multiselect("Signal", ["BUY", "SELL", "HOLD"], default=["BUY", "SELL", "HOLD"])
risk_filter = f2.multiselect("Risk", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])

filtered = [s for s in all_signals if s["signal"] in sig_filter and s["risk"] in risk_filter]

left, right = st.columns([1.2, 1])

with left:
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:8px;">All Signals ({len(filtered)})</div>',
            unsafe_allow_html=True,
        )
        signal_leaderboard(filtered)

with right:
    sym = st.session_state.selected_symbol
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:8px;">{sym} — Chart</div>',
            unsafe_allow_html=True,
        )
        tradingview_chart(symbol=sym, height=320)

    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:4px;">Agent Consensus ({sym})</div>',
            unsafe_allow_html=True,
        )
        agent_consensus_panel(_get_consensus(sym))

    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:4px;">Latest Analysis ({sym})</div>',
            unsafe_allow_html=True,
        )
        latest_analysis_card(sym, _get_latest_analysis(sym))
