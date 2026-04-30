"""Ledger page — filterable analysis history with price band chart."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from apex.frontend.api_client import fetch_analysis
from apex.frontend.components.charts import price_band_chart

st.set_page_config(page_title="Ledger — Apex", page_icon="📋", layout="wide")

st.title("📋 Ledger")
st.caption("Browse and filter analysis history.")

# --- Filters ---
with st.expander("Filters", expanded=True):
    f1, f2, f3 = st.columns(3)
    with f1:
        date_from = st.date_input("From", value=date.today() - timedelta(days=30))
    with f2:
        date_to = st.date_input("To", value=date.today())
    with f3:
        signal_filter = st.multiselect(
            "Signal", options=["BUY", "SELL", "HOLD"], default=["BUY", "SELL", "HOLD"]
        )

ticker_filter = st.text_input("Ticker (leave blank for all)", value="", placeholder="e.g. AAPL")

st.divider()

# --- Price band chart for selected ticker ---
chart_ticker = ticker_filter.upper() if ticker_filter else st.session_state.get("selected_ticker", "AAPL")
st.subheader(f"Price History — {chart_ticker}")

with st.spinner("Loading chart…"):
    result = fetch_analysis(chart_ticker)

if result:
    # Build synthetic price series from analysis metadata (real data would come from OHLCV endpoint)
    import datetime as dt

    today = dt.date.today()
    dates = [today - dt.timedelta(days=i) for i in range(30, 0, -1)]
    base = 150.0
    closes = [base + i * 0.5 + (i % 3) * 0.3 for i in range(30)]
    fig = price_band_chart(dates, closes, ticker=chart_ticker)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available — backend may be offline.")

# --- Analysis table ---
st.divider()
st.subheader("Analysis Records")

history: list[dict] = st.session_state.get("analysis_history", [])
if history:
    filtered = [
        row for row in history
        if row.get("Signal") in signal_filter
        and (not ticker_filter or row.get("Ticker", "").upper() == ticker_filter.upper())
    ]
    if filtered:
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.info("No records match the current filters.")
else:
    st.info("No analyses in session yet. Run one from the Dashboard.")
