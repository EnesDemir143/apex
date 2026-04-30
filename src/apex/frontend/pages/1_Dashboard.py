"""Dashboard page — hero card, metrics, ticker search."""

from __future__ import annotations

import streamlit as st

from apex.frontend.api_client import fetch_analysis, fetch_health
from apex.frontend.components.cards import signal_hero_card

st.set_page_config(page_title="Dashboard — Apex", page_icon="📊", layout="wide")

st.title("📊 Dashboard")

# --- Backend health indicator ---
health = fetch_health()
status_color = "🟢" if health.get("status") == "ok" else "🔴"
st.caption(f"{status_color} Backend: {health.get('status', 'unknown')}")

st.divider()

# --- Ticker search ---
col_search, col_btn = st.columns([3, 1])
with col_search:
    ticker_input = st.text_input(
        "Ticker symbol",
        value=st.session_state.get("selected_ticker", "AAPL"),
        placeholder="e.g. AAPL, TSLA, MSFT",
        label_visibility="collapsed",
    )
with col_btn:
    run_analysis = st.button("Analyse", type="primary", use_container_width=True)

if run_analysis and ticker_input:
    st.session_state.selected_ticker = ticker_input.upper()
    st.session_state.last_analysis = None  # force refresh

ticker = st.session_state.get("selected_ticker", "AAPL")

# --- Fetch / display analysis ---
with st.spinner(f"Running analysis for {ticker}…"):
    result = fetch_analysis(ticker)

if result is None:
    st.warning("Backend unavailable or ticker not whitelisted. Showing placeholder data.")
    result = {
        "ticker": ticker, "signal": "HOLD", "confidence": 0.5,
        "status": "offline", "total_tokens": 0, "cost_usd": 0.0,
    }

st.session_state.last_analysis = result

# --- Hero card ---
signal_hero_card(
    ticker=result.get("ticker", ticker),
    signal=result.get("signal", "HOLD"),
    confidence=float(result.get("confidence", 0.5)),
    status=result.get("status", "completed"),
)

# --- Key metrics ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Signal", result.get("signal", "—"))
m2.metric("Confidence", f"{float(result.get('confidence', 0)):.0%}")
m3.metric("Total Tokens", f"{result.get('total_tokens', 0):,}")
m4.metric("Cost (USD)", f"${float(result.get('cost_usd', 0)):.4f}")

# --- Recent analyses table (session-based) ---
st.divider()
st.subheader("Recent Analyses")
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

# Append current result if not duplicate
history: list[dict] = st.session_state.analysis_history
if not history or history[-1].get("ticker") != result.get("ticker"):
    history.append({
        "Ticker": result.get("ticker"),
        "Signal": result.get("signal"),
        "Confidence": f"{float(result.get('confidence', 0)):.0%}",
        "Status": result.get("status"),
    })
    st.session_state.analysis_history = history[-20:]  # keep last 20

if history:
    st.dataframe(history, use_container_width=True, hide_index=True)
else:
    st.info("No analyses yet. Run one above.")
