"""
Apex — Multi-Agent Market Intelligence · Streamlit entry point.

⚠️  LEGACY / OPTIONAL — the primary Bet 5 UX is the TUI/CLI (``uv run apex``).
    This Streamlit dashboard is preserved for portfolio/CV demonstration.
    See ``docs/WEB_STACK_REVIVAL_GUIDE.md`` for how to run and revive the full
    web stack (FastAPI + PostgreSQL + Redis + Streamlit + K3s).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure 'apex' package is importable regardless of how streamlit is invoked.
# Works with: `streamlit run src/apex/frontend/app.py` from project root,
# or `PYTHONPATH=src streamlit run ...`, or `uv run streamlit run ...`
_src = Path(__file__).resolve().parents[3]  # apex/src/
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import streamlit as st

st.set_page_config(
    page_title="Apex · Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "AAPL"

with st.sidebar:
    st.markdown(
        """
        <div style="padding:8px 0 16px;">
            <div style="font-size:20px;font-weight:800;color:#F0F0F0;letter-spacing:-0.5px;">
                📈 Apex
            </div>
            <div style="font-size:11px;color:#555;margin-top:2px;">Multi-Agent Market Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link("app.py", label="🏠  Home")
    st.page_link("pages/1_Dashboard.py", label="📊  Dashboard")
    st.page_link("pages/2_Signals.py", label="⚡  Signals")
    st.page_link("pages/3_Backtest.py", label="⚗️  Backtest")
    st.page_link("pages/4_Replay_Mode.py", label="▶️  Replay Mode")
    st.page_link("pages/5_Architecture.py", label="🏗️  Architecture")
    st.page_link("pages/6_Observability.py", label="🔭  Observability")

    st.divider()

    st.markdown(
        """
        <div style="background:#161B27;border:1px solid #2A2F3E;border-radius:8px;padding:14px;">
            <div style="font-size:13px;font-weight:600;color:#F0F0F0;margin-bottom:6px;">Explore the system</div>
            <div style="font-size:11px;color:#666;line-height:1.6;">
                See how 4 specialized agents work together to generate high-quality market intelligence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
    st.page_link("pages/5_Architecture.py", label="Learn More →")

    st.divider()
    st.markdown(
        '<div style="font-size:10px;color:#333;text-align:center;">© 2025 Apex · All rights reserved</div>',
        unsafe_allow_html=True,
    )

st.title("📈 Apex — Multi-Agent Market Intelligence")
st.markdown("Use the sidebar to navigate. Start with **Dashboard** for the full cockpit view.")

c1, c2, c3 = st.columns(3)
c1.metric("Agents", "4", "Technical · Fundamental · Risk · Portfolio")
c2.metric("Signals", "BUY / SELL / HOLD", "with confidence + risk scores")
c3.metric("Stack", "LangGraph + FastAPI", "PostgreSQL · Redis · Streamlit")

st.info("👈 Select **Dashboard** from the sidebar to open the AI market intelligence cockpit.")
