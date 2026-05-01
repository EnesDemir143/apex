"""Observability — system health, API metrics, LLM cost."""


from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.frontend.components.observability import observability_panel
from apex.frontend.mock_data import OBS_SPARKLINES, OBSERVABILITY

st.set_page_config(page_title="Observability — Apex", page_icon="🔭", layout="wide")

st.title("🔭 Observability")
st.caption("Live system metrics — API latency, cache, LLM cost, agent runs.")

with st.container(border=True):
    st.markdown('<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:12px;">System Observability <span style="font-size:11px;color:#00D4AA;">(Live)</span></div>', unsafe_allow_html=True)
    observability_panel(OBSERVABILITY, OBS_SPARKLINES)

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Agent Run History")
    st.info("Full Grafana dashboard available in production (LGTM stack: Loki + Tempo + Prometheus).")

with c2:
    st.subheader("LLM Cost Breakdown")
    cost_data = {
        "Technical Agent":   "$0.12",
        "Fundamental Agent": "$0.09",
        "Risk Agent":        "$0.08",
        "Portfolio Manager": "$0.13",
    }
    for agent, cost in cost_data.items():
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2535;">'
            f'<span style="color:#AAA;font-size:13px;">{agent}</span>'
            f'<span style="color:#F0F0F0;font-weight:600;font-size:13px;">{cost}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;padding:8px 0;">'
        f'<span style="color:#F0F0F0;font-weight:600;">Total Today</span>'
        f'<span style="color:#00D4AA;font-weight:700;">${OBSERVABILITY["llm_cost_today"]:.2f}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
