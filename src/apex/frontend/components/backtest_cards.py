"""Backtest Performance panel — metric cards with sparklines."""

from __future__ import annotations

import streamlit as st

from apex.frontend.components.metric_card import _svg_sparkline


def backtest_performance_panel(summary: dict, sparklines: dict) -> None:
    """Render 3-column backtest metrics matching the mockup."""
    st.markdown(
        f'<div style="font-size:12px;color:#666;margin-bottom:8px;">'
        f'Strategy: <span style="color:#AAA;">{summary["strategy"]}</span>'
        f'&nbsp;&nbsp;Period: <span style="color:#AAA;">{summary["period"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    metrics = [
        ("Win Rate",                f'{summary["win_rate"]:.1%}',                "#00D4AA", sparklines.get("win_rate", [])),
        ("Max Drawdown",            f'{summary["max_drawdown"]:.1%}',             "#FF4B4B", sparklines.get("drawdown", [])),
        ("Sharpe-like",             f'{summary["sharpe"]:.2f}',                  "#7C3AED", sparklines.get("sharpe", [])),
        ("Signals Tested",          f'{summary["signals_tested"]:,}',            "#3B82F6", []),
        ("Avg Confidence (Winners)",f'{summary["avg_confidence_winners"]:.0%}',  "#FFD700", []),
        ("Profit Factor",           f'{summary["profit_factor"]:.2f}',           "#00D4AA", sparklines.get("profit", [])),
    ]

    cols = st.columns(3)
    for i, (title, value, color, spark) in enumerate(metrics):
        spark_html = (
            f'<div style="margin-top:6px;">{_svg_sparkline(spark, color=color, width=90, height=28)}</div>'
            if spark else ""
        )
        cols[i % 3].markdown(
            f"""
            <div style="background:#161B27;border:1px solid #2A2F3E;border-radius:8px;padding:12px 14px;margin-bottom:8px;">
                <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:1px;">{title}</div>
                <div style="font-size:22px;font-weight:700;color:{color};margin-top:2px;">{value}</div>
                {spark_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
