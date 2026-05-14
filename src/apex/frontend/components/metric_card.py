"""KPI metric cards with inline sparkline (pure HTML/SVG — no Plotly overhead)."""

from __future__ import annotations

import streamlit as st

_SIGNAL_COLOR = {"BUY": "#00D4AA", "SELL": "#FF4B4B", "HOLD": "#FFD700"}


def _svg_sparkline(values: list[float], color: str = "#00D4AA", width: int = 80, height: int = 32) -> str:
    """Render a minimal SVG polyline sparkline."""
    if not values or len(values) < 2:
        return ""
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    pad = 2
    w, h = width - pad * 2, height - pad * 2
    pts = " ".join(
        f"{pad + i * w / (len(values) - 1):.1f},{pad + h - (v - mn) / rng * h:.1f}" for i, v in enumerate(values)
    )
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f"</svg>"
    )


def hero_metric_card(
    title: str,
    value: str,
    delta: str | None = None,
    sparkline: list[float] | None = None,
    spark_color: str = "#00D4AA",
    signal_badge: str | None = None,
) -> None:
    """Single KPI card matching the mockup style."""
    badge_html = ""
    if signal_badge:
        c = _SIGNAL_COLOR.get(signal_badge, "#888")
        badge_html = (
            f'<span style="background:{c}22;color:{c};border:1px solid {c}55;'
            f"border-radius:4px;padding:2px 8px;font-size:12px;font-weight:700;"
            f'margin-left:8px;">{signal_badge}</span>'
        )

    delta_html = ""
    if delta:
        delta_html = f'<div style="font-size:11px;color:#888;margin-top:4px;">{delta}</div>'

    spark_html = ""
    if sparkline:
        spark_html = (
            f'<div style="position:absolute;bottom:12px;right:12px;opacity:0.7;">'
            f"{_svg_sparkline(sparkline, color=spark_color)}</div>"
        )

    st.markdown(
        f"""
        <div style="
            position:relative;
            background:#161B27;
            border:1px solid #2A2F3E;
            border-radius:10px;
            padding:18px 16px 14px;
            min-height:90px;
            overflow:hidden;
        ">
            <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">{title}</div>
            <div style="font-size:24px;font-weight:700;color:#F0F0F0;line-height:1.1;">
                {value}{badge_html}
            </div>
            {delta_html}
            {spark_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
