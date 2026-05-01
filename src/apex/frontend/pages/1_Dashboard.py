"""Dashboard — Apex AI market intelligence cockpit."""


from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.frontend.components.agent_consensus import agent_consensus_panel
from apex.frontend.components.backtest_cards import backtest_performance_panel
from apex.frontend.components.latest_analysis import latest_analysis_card
from apex.frontend.components.metric_card import hero_metric_card
from apex.frontend.components.observability import observability_panel
from apex.frontend.components.regime_chart import market_regime_panel
from apex.frontend.components.signal_table import signal_leaderboard
from apex.frontend.components.tradingview_widget import tradingview_chart
from apex.frontend.mock_data import (
    BACKTEST_SPARKLINES,
    BACKTEST_SUMMARY,
    HERO_METRICS,
    HERO_SPARKLINES,
    MARKET_REGIME,
    OBS_SPARKLINES,
    OBSERVABILITY,
    TOP_SIGNALS,
    get_consensus,
    get_latest_analysis,
)

st.set_page_config(
    page_title="Dashboard — Apex",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "AAPL"

# ── Top header ─────────────────────────────────────────────────────────────
hdr_left, hdr_mid, hdr_right = st.columns([2, 3, 2])

with hdr_left:
    st.markdown(
        """
        <div style="padding-top:4px;">
            <div style="font-size:22px;font-weight:700;color:#F0F0F0;">Good afternoon! 👋</div>
            <div style="font-size:12px;color:#555;">AI-powered market intelligence and multi-agent analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hdr_mid:
    search = st.text_input(
        "search", placeholder="Search symbols (e.g. AAPL)",
        label_visibility="collapsed", key="dashboard_search",
    )
    if search:
        st.session_state.selected_symbol = search.strip().upper()
        st.rerun()

with hdr_right:
    st.markdown(
        """
        <div style="display:flex;justify-content:flex-end;align-items:center;gap:16px;padding-top:8px;">
            <span style="font-size:12px;color:#AAA;">⚡ Market: <b style="color:#FFD700;">Volatile</b></span>
            <span style="font-size:12px;color:#AAA;">System Status <b style="color:#00D4AA;">● Healthy</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div style="margin-bottom:12px;"></div>', unsafe_allow_html=True)

# ── Hero KPI cards ─────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    hero_metric_card(
        "Market Regime", HERO_METRICS["market_regime"]["value"],
        sparkline=HERO_SPARKLINES["market_regime"], spark_color="#7C3AED",
    )
with k2:
    hero_metric_card(
        "Analyzed Symbols", str(HERO_METRICS["analyzed_symbols"]["value"]),
        delta=HERO_METRICS["analyzed_symbols"]["delta"],
    )
with k3:
    hero_metric_card(
        "Strongest Signal", HERO_METRICS["strongest_signal"]["value"],
        signal_badge=HERO_METRICS["strongest_signal"]["signal"],
    )
with k4:
    hero_metric_card(
        "Avg Confidence",
        f'{HERO_METRICS["avg_confidence"]["value"]:.0%}',
        delta=HERO_METRICS["avg_confidence"]["delta"],
        sparkline=HERO_SPARKLINES["avg_confidence"], spark_color="#00D4AA",
    )
with k5:
    hero_metric_card(
        "System Health", HERO_METRICS["system_health"]["value"],
        sparkline=HERO_SPARKLINES["system_health"], spark_color="#00D4AA",
    )

st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

# ── Main grid: left (signals) | right (chart) ─────────────────────────────
left_col, right_col = st.columns([1.1, 1.4])

with left_col:
    with st.container(border=True):
        top_hdr, top_link = st.columns([3, 1])
        top_hdr.markdown('<div style="font-size:15px;font-weight:600;color:#F0F0F0;">Top Signals</div>', unsafe_allow_html=True)
        top_link.page_link("pages/2_Signals.py", label="View all →")
        signal_leaderboard(TOP_SIGNALS[:5])

        # Agent legend
        st.markdown(
            """
            <div style="display:flex;gap:16px;padding-top:8px;flex-wrap:wrap;">
                <span style="font-size:11px;color:#888;">● Technical Agent</span>
                <span style="font-size:11px;color:#888;">● Fundamental Agent</span>
                <span style="font-size:11px;color:#888;">● Risk Agent</span>
                <span style="font-size:11px;color:#888;">● Portfolio Manager</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

with right_col:
    sym = st.session_state.selected_symbol
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:15px;font-weight:600;color:#F0F0F0;margin-bottom:8px;">'
            f'{sym} — TradingView Chart</div>',
            unsafe_allow_html=True,
        )
        tradingview_chart(symbol=sym, interval="D", height=400)

st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

# ── Bottom grid: consensus | backtest | regime ─────────────────────────────
b1, b2, b3 = st.columns([1, 1.2, 1])

with b1:
    with st.container(border=True):
        hdr_c, hdr_l = st.columns([2, 1])
        hdr_c.markdown(f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;">Agent Consensus ({sym})</div>', unsafe_allow_html=True)
        hdr_l.page_link("pages/2_Signals.py", label="View details →")
        agent_consensus_panel(get_consensus(sym))

with b2:
    with st.container(border=True):
        hdr_c, hdr_l = st.columns([2, 1])
        hdr_c.markdown('<div style="font-size:14px;font-weight:600;color:#F0F0F0;">Backtest Performance</div>', unsafe_allow_html=True)
        hdr_l.page_link("pages/3_Backtest.py", label="View full report →")
        backtest_performance_panel(BACKTEST_SUMMARY, BACKTEST_SPARKLINES)

with b3:
    with st.container(border=True):
        hdr_c, hdr_l = st.columns([2, 1])
        hdr_c.markdown('<div style="font-size:14px;font-weight:600;color:#F0F0F0;">Market Regime Detection</div>', unsafe_allow_html=True)
        hdr_l.markdown('<div style="text-align:right;font-size:12px;color:#3B82F6;">View all</div>', unsafe_allow_html=True)
        market_regime_panel(MARKET_REGIME)

st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

# ── Observability + Latest Analysis ───────────────────────────────────────
obs_col, lat_col = st.columns([1.6, 1])

with obs_col:
    with st.container(border=True):
        st.markdown('<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:10px;">System Observability <span style="font-size:11px;color:#00D4AA;">(Live)</span></div>', unsafe_allow_html=True)
        observability_panel(OBSERVABILITY, OBS_SPARKLINES)

with lat_col:
    with st.container(border=True):
        hdr_c, hdr_l = st.columns([2, 1])
        hdr_c.markdown(f'<div style="font-size:14px;font-weight:600;color:#F0F0F0;">Latest Analysis ({sym})</div>', unsafe_allow_html=True)
        hdr_l.page_link("pages/6_Observability.py", label="View all →")
        latest_analysis_card(sym, get_latest_analysis(sym))

# ── Footer disclaimer ──────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<div style="text-align:center;font-size:11px;color:#333;">'
    'Disclaimer: Apex is an educational project. Not financial advice. Past performance does not predict future results.'
    '&nbsp;&nbsp;|&nbsp;&nbsp;Built with ❤️ using Python, LangGraph, FastAPI, Streamlit'
    '</div>',
    unsafe_allow_html=True,
)
