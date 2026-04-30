"""Apex Streamlit app entry point."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Apex — Trading Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialise session state defaults once
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "AAPL"
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

st.sidebar.title("📈 Apex")
st.sidebar.caption("Multi-Agent Trading Analysis")
st.sidebar.divider()
st.sidebar.markdown("**Navigation**")
st.sidebar.page_link("app.py", label="🏠 Home")
st.sidebar.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
st.sidebar.page_link("pages/2_Ledger.py", label="📋 Ledger")
st.sidebar.page_link("pages/3_Detail.py", label="🔍 Detail")
st.sidebar.page_link("pages/4_Backtest.py", label="⚗️ Backtest")

st.title("📈 Apex Trading Analysis")
st.markdown(
    "Multi-Agent Based Automated Trading System — 4 AI agents producing **BUY / SELL / HOLD** signals."
)
st.info("Use the sidebar to navigate between pages.")

col1, col2, col3 = st.columns(3)
col1.metric("Agents", "4", "Technical · Fundamental · Risk · Portfolio")
col2.metric("Signals", "BUY / SELL / HOLD", "with confidence scores")
col3.metric("Stack", "LangGraph + FastAPI", "PostgreSQL · Redis · Streamlit")
