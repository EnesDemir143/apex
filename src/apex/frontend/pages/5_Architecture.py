"""Architecture — Apex system design overview."""


from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

st.set_page_config(page_title="Architecture — Apex", page_icon="🏗️", layout="wide")

st.title("🏗️ Architecture")
st.caption("How Apex works — 4-agent LangGraph workflow.")

# System diagram as styled HTML
st.markdown(
    """
    <div style="background:#161B27;border:1px solid #2A2F3E;border-radius:10px;padding:24px;font-family:monospace;font-size:13px;color:#AAA;line-height:2;">
        <div style="color:#F0F0F0;font-size:15px;font-weight:600;margin-bottom:16px;">Apex — System Architecture</div>
        <pre style="background:transparent;color:#AAA;margin:0;">
Market Data (Alpaca)
        │
        ▼
  FastAPI Backend
  ┌─────────────────────────────────────────┐
  │  POST /api/v1/analyze/{symbol}          │
  │                                         │
  │  LangGraph Workflow                     │
  │  ┌──────────┐  ┌──────────────────┐    │
  │  │Technical │  │  Fundamental     │    │
  │  │  Agent   │  │    Agent         │    │
  │  └────┬─────┘  └────────┬─────────┘    │
  │       │                 │              │
  │  ┌────┴─────┐  ┌────────┴─────────┐    │
  │  │  Risk    │  │ Portfolio Manager│    │
  │  │  Agent   │  │  (Supervisor)    │    │
  │  └──────────┘  └──────────────────┘    │
  │                                         │
  │  PostgreSQL · Redis · LangSmith         │
  └─────────────────────────────────────────┘
        │
        ▼
  Streamlit Frontend (this dashboard)
        </pre>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**Data Layer**")
    for item in ["Alpaca Markets API (primary)", "yfinance (fallback)", "PostgreSQL + pgvector", "Redis cache"]:
        st.markdown(f"- {item}")

with c2:
    st.markdown("**Agent Layer**")
    for item in ["Technical Agent (RSI, MACD, Bollinger)", "Fundamental Agent (RAG)", "Risk Agent (volatility)", "Portfolio Manager (supervisor)"]:
        st.markdown(f"- {item}")

with c3:
    st.markdown("**Infrastructure**")
    for item in ["FastAPI 0.136", "LangGraph 1.1 (stable)", "OpenTelemetry + Grafana LGTM", "Docker + K3s", "LangSmith tracing"]:
        st.markdown(f"- {item}")

st.divider()
st.markdown(
    '<div style="text-align:center;font-size:12px;color:#555;">'
    'Built with Python 3.13 · LangGraph · FastAPI · PostgreSQL · Redis · Streamlit'
    '</div>',
    unsafe_allow_html=True,
)
