"""Signals — full agent signal leaderboard."""


from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.frontend.components.agent_consensus import agent_consensus_panel
from apex.frontend.components.latest_analysis import latest_analysis_card
from apex.frontend.components.signal_table import signal_leaderboard
from apex.frontend.components.tradingview_widget import tradingview_chart
from apex.frontend.mock_data import ALL_SIGNALS, get_consensus, get_latest_analysis

st.set_page_config(page_title="Signals — Apex", page_icon="⚡", layout="wide")

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "AAPL"

st.title("⚡ Signals")
st.caption("All agent signals — click a symbol to inspect.")

# Filters
f1, f2, f3 = st.columns([1, 1, 2])
sig_filter  = f1.multiselect("Signal", ["BUY", "SELL", "HOLD"], default=["BUY", "SELL", "HOLD"])
risk_filter = f2.multiselect("Risk",   ["Low", "Medium", "High"], default=["Low", "Medium", "High"])

filtered = [
    s for s in ALL_SIGNALS
    if s["signal"] in sig_filter and s["risk"] in risk_filter
]

left, right = st.columns([1.2, 1])

with left:
    with st.container(border=True):
        st.markdown(f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:8px;">All Signals ({len(filtered)})</div>', unsafe_allow_html=True)
        signal_leaderboard(filtered)

with right:
    sym = st.session_state.selected_symbol
    with st.container(border=True):
        st.markdown(f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:8px;">{sym} — Chart</div>', unsafe_allow_html=True)
        tradingview_chart(symbol=sym, height=320)

    with st.container(border=True):
        st.markdown(f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:4px;">Agent Consensus ({sym})</div>', unsafe_allow_html=True)
        agent_consensus_panel(get_consensus(sym))

    with st.container(border=True):
        st.markdown(f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:4px;">Latest Analysis ({sym})</div>', unsafe_allow_html=True)
        latest_analysis_card(sym, get_latest_analysis(sym))
