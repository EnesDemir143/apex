"""Replay Mode — step through historical agent decisions."""


from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.frontend.mock_data import get_replay_events

st.set_page_config(page_title="Replay Mode — Apex", page_icon="▶️", layout="wide")

st.title("▶️ Replay Mode")
st.caption("Step through past agent decisions like a simulation.")

sym = st.selectbox("Symbol", ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"], index=0)
events = get_replay_events(sym)

if "replay_idx" not in st.session_state:
    st.session_state.replay_idx = 0

idx = st.session_state.replay_idx
event = events[idx]

_SIG_COLOR = {"BUY": "#00D4AA", "SELL": "#FF4B4B", "HOLD": "#FFD700"}
_RISK_COLOR = {"Low": "#00D4AA", "Medium": "#FFD700", "High": "#FF4B4B"}

col_nav, col_card = st.columns([1, 2])

with col_nav:
    st.markdown(f"**Event {idx + 1} / {len(events)}**")
    c1, c2, c3 = st.columns(3)
    if c1.button("⏮ First"):
        st.session_state.replay_idx = 0; st.rerun()
    if c2.button("◀ Prev") and idx > 0:
        st.session_state.replay_idx -= 1; st.rerun()
    if c3.button("Next ▶") and idx < len(events) - 1:
        st.session_state.replay_idx += 1; st.rerun()

    st.slider("Jump to event", 0, len(events) - 1, idx, key="replay_slider",
              on_change=lambda: setattr(st.session_state, "replay_idx", st.session_state.replay_slider))

with col_card:
    sc = _SIG_COLOR.get(event["signal"], "#888")
    rc = _RISK_COLOR.get(event["risk"], "#888")
    st.markdown(
        f"""
        <div style="background:#161B27;border:1px solid #2A2F3E;border-radius:10px;padding:20px;">
            <div style="font-size:12px;color:#555;margin-bottom:4px;">{event['date']} · {sym}</div>
            <div style="font-size:32px;font-weight:700;color:{sc};">{event['signal']}</div>
            <div style="display:flex;gap:16px;margin-top:8px;">
                <span style="font-size:13px;color:#AAA;">Confidence: <b style="color:#F0F0F0;">{event['confidence']:.0%}</b></span>
                <span style="font-size:13px;color:#AAA;">Risk: <b style="color:{rc};">{event['risk']}</b></span>
            </div>
            <div style="margin-top:12px;font-size:13px;color:#888;border-top:1px solid #2A2F3E;padding-top:10px;">
                {event['explanation']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
