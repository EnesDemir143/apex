"""Market Regime Detection — donut chart + percentage list."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


def market_regime_panel(regime: dict) -> None:
    """Donut chart + legend list matching the mockup."""
    breakdown = regime["breakdown"]
    labels  = [r["label"] for r in breakdown]
    values  = [r["pct"]   for r in breakdown]
    colors  = [r["color"] for r in breakdown]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker={"colors": colors, "line": {"color": "#0E1117", "width": 2}},
        textinfo="none",
        hovertemplate="%{label}: %{value}%<extra></extra>",
    ))

    # Centre annotation
    fig.add_annotation(
        text=f"<b>Current</b><br>{regime['current']}",
        x=0.5, y=0.5, showarrow=False,
        font={"size": 12, "color": "#F0F0F0"},
        align="center",
    )

    fig.update_layout(
        showlegend=False,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=180,
    )

    col_chart, col_legend = st.columns([1, 1])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_legend:
        st.markdown('<div style="padding-top:20px;">', unsafe_allow_html=True)
        for r in breakdown:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:4px 0;border-bottom:1px solid #1E2535;">'
                f'<span style="display:flex;align-items:center;gap:6px;">'
                f'<span style="width:10px;height:10px;border-radius:50%;background:{r["color"]};display:inline-block;"></span>'
                f'<span style="font-size:12px;color:#AAA;">{r["label"]}</span></span>'
                f'<span style="font-size:12px;font-weight:600;color:#F0F0F0;">{r["pct"]}%</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="font-size:11px;color:#555;margin-top:8px;">Since {regime["since"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
