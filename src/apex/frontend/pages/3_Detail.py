"""Detail page — candlestick chart, prediction band, agent decision breakdown."""

from __future__ import annotations

import streamlit as st
from plotly.graph_objects import Candlestick  # noqa: F401 — confirms plotly.graph_objects import

from apex.frontend.api_client import fetch_analysis, fetch_ohlcv
from apex.frontend.components.cards import agent_decision_card, signal_hero_card
from apex.frontend.components.charts import candlestick_chart

st.set_page_config(page_title="Detail — Apex", page_icon="🔍", layout="wide")

st.title("🔍 Detail")

# --- Ticker selector ---
col_t, col_btn = st.columns([3, 1])
with col_t:
    ticker = st.text_input(
        "Ticker",
        value=st.session_state.get("selected_ticker", "AAPL"),
        label_visibility="collapsed",
        placeholder="e.g. AAPL",
    )
with col_btn:
    if st.button("Load", type="primary", use_container_width=True):
        st.session_state.selected_ticker = ticker.upper()

ticker = st.session_state.get("selected_ticker", "AAPL")

with st.spinner(f"Loading detail for {ticker}…"):
    result = fetch_analysis(ticker)

if result is None:
    st.warning("Backend unavailable. Showing placeholder data.")
    result = {
        "ticker": ticker, "signal": "HOLD", "confidence": 0.5,
        "status": "offline", "total_tokens": 0, "cost_usd": 0.0, "summary": {},
    }

# --- Hero card ---
signal_hero_card(
    ticker=result.get("ticker", ticker),
    signal=result.get("signal", "HOLD"),
    confidence=float(result.get("confidence", 0.5)),
    status=result.get("status", "completed"),
)

st.divider()

# --- Candlestick chart with real OHLCV ---
st.subheader("Price Chart")
with st.spinner("Loading OHLCV…"):
    bars = fetch_ohlcv(ticker, days=60)

if bars:
    dates  = [b["timestamp"] for b in bars]
    opens  = [float(b["open"])  for b in bars]
    highs  = [float(b["high"])  for b in bars]
    lows   = [float(b["low"])   for b in bars]
    closes = [float(b["close"]) for b in bars]
    volumes = [float(b.get("volume", 0)) for b in bars]
else:
    # Fallback synthetic when backend offline
    import datetime as dt
    today = dt.date.today()
    dates  = [today - dt.timedelta(days=i) for i in range(60, 0, -1)]
    opens  = [150.0 + i * 0.5 for i in range(60)]
    closes = [o + 0.3 * (1 if i % 2 == 0 else -1) for i, o in enumerate(opens)]
    highs  = [max(o, c) + 0.8 for o, c in zip(opens, closes)]
    lows   = [min(o, c) - 0.8 for o, c in zip(opens, closes)]
    volumes = [float(1_000_000 + i * 10_000) for i in range(60)]

fig = candlestick_chart(dates, opens, highs, lows, closes, ticker=ticker, volumes=volumes)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Agent decision breakdown ---
st.subheader("Agent Decisions")
summary = result.get("summary", {})
agent_outputs = summary.get("agent_outputs", {}) if isinstance(summary, dict) else {}

agents = {
    "Technical Agent": agent_outputs.get("technical"),
    "Fundamental Agent": agent_outputs.get("fundamental"),
    "Risk Agent": agent_outputs.get("risk"),
    "Portfolio Manager": agent_outputs.get("portfolio"),
}

cols = st.columns(2)
for idx, (name, output) in enumerate(agents.items()):
    with cols[idx % 2]:
        if isinstance(output, dict):
            agent_decision_card(
                agent_name=name,
                signal=output.get("signal"),
                confidence=output.get("confidence"),
                summary=str(output.get("reasoning", output.get("summary", ""))),
            )
        else:
            agent_decision_card(agent_name=name, signal=None, confidence=None, summary="No data")

# --- Error analysis ---
errors = summary.get("errors", []) if isinstance(summary, dict) else []
if errors:
    st.divider()
    st.subheader("Errors")
    for err in errors:
        st.error(str(err))
