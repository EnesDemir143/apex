"""Observability — system health, API metrics, LLM cost."""


from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.core.constants import TICKERS_WHITELIST
from apex.frontend.api_client import fetch_all_signals, fetch_observability
from apex.frontend.components.observability import observability_panel
from apex.frontend.mock_data import (
    OBS_SPARKLINES as _MOCK_OBS_SPARKLINES,
    OBSERVABILITY as _MOCK_OBS,
)

st.set_page_config(page_title="Observability — Apex", page_icon="🔭", layout="wide")

st.title("🔭 Observability")
st.caption("Live system metrics — API latency, cache, LLM cost, agent runs.")

# ── Fetch live data ────────────────────────────────────────────────────────
with st.spinner("Fetching system status…"):
    obs_data = fetch_observability()
    live_signals = fetch_all_signals(TICKERS_WHITELIST)

api_available = obs_data.get("data_provider") not in (None, "Unreachable")

# Merge live health into mock shape (mock provides sparklines + numeric fields)
observability = _MOCK_OBS.copy()
if api_available:
    observability["data_provider"] = obs_data.get("data_provider", "Healthy")

if not api_available:
    st.warning("⚠️ API unavailable — showing cached demo data.", icon="⚠️")

with st.container(border=True):
    st.markdown('<div style="font-size:14px;font-weight:600;color:#F0F0F0;margin-bottom:12px;">System Observability <span style="font-size:11px;color:#00D4AA;">(Live)</span></div>', unsafe_allow_html=True)
    observability_panel(observability, _MOCK_OBS_SPARKLINES)

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Agent Run History")
    st.info("Full Grafana dashboard available in production (LGTM stack: Loki + Tempo + Prometheus).")

with c2:
    st.subheader("LLM Cost Breakdown")

    # Derive per-ticker cost from live signals if available
    if live_signals:
        total_cost = sum(s.get("cost_usd", 0.0) or 0.0 for s in live_signals)
        # Distribute evenly across 4 agents as approximation
        per_agent = total_cost / 4 if total_cost else None
        cost_data = {
            "Technical Agent":   f"${per_agent:.4f}" if per_agent is not None else "—",
            "Fundamental Agent": f"${per_agent:.4f}" if per_agent is not None else "—",
            "Risk Agent":        f"${per_agent:.4f}" if per_agent is not None else "—",
            "Portfolio Manager": f"${per_agent:.4f}" if per_agent is not None else "—",
        }
        total_label = f"${total_cost:.4f}" if total_cost else "—"
    else:
        cost_data = {
            "Technical Agent":   "$0.12",
            "Fundamental Agent": "$0.09",
            "Risk Agent":        "$0.08",
            "Portfolio Manager": "$0.13",
        }
        total_label = f"${observability['llm_cost_today']:.2f}"

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
        f'<span style="color:#00D4AA;font-weight:700;">{total_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
