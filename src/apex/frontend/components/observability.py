"""System Observability panel — 6 live metrics with sparklines."""

from __future__ import annotations

import streamlit as st

from apex.frontend.components.metric_card import _svg_sparkline


def observability_panel(obs: dict, sparklines: dict) -> None:
    """6-column observability metrics matching the mockup."""
    metrics = [
        ("API Latency",      f'{obs["api_latency_ms"]} ms',       "#3B82F6", sparklines.get("latency", [])),
        ("Cache Hit Rate",   f'{obs["cache_hit_rate"]:.0%}',       "#00D4AA", sparklines.get("cache", [])),
        ("LLM Cost Today",   f'${obs["llm_cost_today"]:.2f}',      "#7C3AED", sparklines.get("cost", [])),
        ("Agent Runs Today", str(obs["agent_runs_today"]),          "#F59E0B", sparklines.get("runs", [])),
        ("Failed Runs",      str(obs["failed_runs"]),               "#FF4B4B", sparklines.get("failed", [])),
        ("Data Provider",    obs["data_provider"],                  "#00D4AA", sparklines.get("provider", [])),
    ]

    cols = st.columns(6)
    for col, (title, value, color, spark) in zip(cols, metrics):
        spark_html = (
            f'<div style="margin-top:4px;">{_svg_sparkline(spark, color=color, width=80, height=24)}</div>'
            if spark else ""
        )
        col.markdown(
            f"""
            <div style="background:#161B27;border:1px solid #2A2F3E;border-radius:8px;padding:12px 10px;">
                <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:1px;white-space:nowrap;">{title}</div>
                <div style="font-size:18px;font-weight:700;color:{color};margin-top:4px;">{value}</div>
                {spark_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
