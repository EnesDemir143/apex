"""Backtest page — input form, result metrics, equity curve, trade table."""

from __future__ import annotations

import datetime as dt
import random

import streamlit as st

from apex.frontend.components.charts import backtest_equity_chart

st.set_page_config(page_title="Backtest — Apex", page_icon="⚗️", layout="wide")

st.title("⚗️ Backtest")
st.caption("Simulate strategy performance over historical data.")

# --- Input form ---
with st.form("backtest_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        bt_ticker = st.text_input("Ticker", value="AAPL")
    with c2:
        bt_from = st.date_input("From", value=dt.date.today() - dt.timedelta(days=365))
    with c3:
        bt_to = st.date_input("To", value=dt.date.today())

    c4, c5 = st.columns(2)
    with c4:
        initial_capital = st.number_input("Initial Capital ($)", value=10_000, min_value=100, step=500)
    with c5:
        confidence_threshold = st.slider("Min Confidence Threshold", 0.0, 1.0, 0.6, 0.05)

    submitted = st.form_submit_button("Run Backtest", type="primary", use_container_width=True)

if submitted or st.session_state.get("backtest_result"):
    if submitted:
        # Deterministic stub backtest result
        rng = random.Random(bt_ticker + str(bt_from))
        n_days = (bt_to - bt_from).days or 1
        equity = [initial_capital]
        for _ in range(min(n_days, 252)):
            equity.append(equity[-1] * (1 + rng.uniform(-0.015, 0.02)))

        trades = [
            {"Date": str(bt_from + dt.timedelta(days=i * 10)), "Signal": rng.choice(["BUY", "SELL"]),
             "Price": round(150 + rng.uniform(-10, 10), 2), "P&L": round(rng.uniform(-200, 400), 2)}
            for i in range(min(n_days // 10, 20))
        ]
        total_return = (equity[-1] - initial_capital) / initial_capital
        wins = sum(1 for t in trades if t["P&L"] > 0)
        win_rate = wins / len(trades) if trades else 0.0
        max_dd = min(0.0, min((equity[i] - max(equity[:i+1])) / max(equity[:i+1]) for i in range(1, len(equity))))
        sharpe = total_return / (0.15 + 1e-9) * (252 / n_days) ** 0.5

        st.session_state.backtest_result = {
            "equity": equity, "trades": trades,
            "total_return": total_return, "win_rate": win_rate,
            "max_drawdown": max_dd, "sharpe": sharpe,
            "ticker": bt_ticker.upper(), "dates": [
                bt_from + dt.timedelta(days=i) for i in range(len(equity))
            ],
        }

    res = st.session_state.backtest_result
    st.divider()

    # --- Result metrics ---
    st.subheader("Results")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Return", f"{res['total_return']:.1%}")
    m2.metric("Sharpe Ratio", f"{res['sharpe']:.2f}")
    m3.metric("Max Drawdown", f"{res['max_drawdown']:.1%}")
    m4.metric("Win Rate", f"{res['win_rate']:.0%}")

    # --- Equity curve ---
    st.subheader("Equity Curve")
    fig = backtest_equity_chart(res["dates"], res["equity"])
    st.plotly_chart(fig, use_container_width=True)

    # --- Trade table ---
    st.subheader("Trades")
    if res["trades"]:
        st.dataframe(res["trades"], use_container_width=True, hide_index=True)
    else:
        st.info("No trades generated.")
else:
    st.info("Configure parameters above and click **Run Backtest**.")
