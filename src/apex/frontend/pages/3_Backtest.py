"""Backtest — strategy performance analysis."""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_src = _Path(__file__).resolve().parents[3]
if str(_src) not in _sys.path:
    _sys.path.insert(0, str(_src))

import streamlit as st

from apex.frontend.components.backtest_cards import backtest_performance_panel
from apex.frontend.mock_data import BACKTEST_SPARKLINES, BACKTEST_SUMMARY

st.set_page_config(page_title="Backtest — Apex", page_icon="⚗️", layout="wide")

st.title("⚗️ Backtest")
st.caption("Historical strategy performance — Agent Consensus v1.")

with st.container(border=True):
    backtest_performance_panel(BACKTEST_SUMMARY, BACKTEST_SPARKLINES)

st.divider()
st.info("Full interactive backtest with custom date ranges and symbol selection coming soon.")
