"""Plotly chart factory functions — all use plotly_dark template."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

_TEMPLATE = "plotly_dark"
_BG = "rgba(0,0,0,0)"


def candlestick_chart(
    dates: list[Any],
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    ticker: str = "",
    volumes: list[float] | None = None,
    prediction_high: list[float] | None = None,
    prediction_low: list[float] | None = None,
) -> go.Figure:
    """Mountain (area) price chart + volume histogram — Yahoo Finance style.

    Upper panel: filled area line with OHLCV hover tooltip.
    Lower panel: volume bars (green=up day, red=down day).
    """
    vol_colors = [
        "#26a69a" if c >= o else "#ef5350"
        for o, c in zip(opens, closes)
    ]
    vols = volumes or [0] * len(closes)

    fig = go.Figure()

    # Upper panel: mountain area
    fig.add_trace(go.Scatter(
        x=dates, y=closes,
        mode="lines",
        name=ticker,
        line={"color": "#2962ff", "width": 1.5},
        fill="tozeroy",
        fillcolor="rgba(41,98,255,0.15)",
        customdata=list(zip(opens, highs, lows, closes, vols)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "O: %{customdata[0]:.2f}  H: %{customdata[1]:.2f}<br>"
            "L: %{customdata[2]:.2f}  C: %{customdata[3]:.2f}<br>"
            "V: %{customdata[4]:,.0f}<extra></extra>"
        ),
        yaxis="y",
    ))

    # Lower panel: volume bars
    fig.add_trace(go.Bar(
        x=dates, y=vols,
        name="Volume",
        marker_color=vol_colors,
        opacity=0.8,
        yaxis="y2",
        hovertemplate="%{y:,.0f}<extra>Volume</extra>",
    ))

    fig.update_layout(
        template=_TEMPLATE,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        margin={"l": 10, "r": 60, "t": 40, "b": 10},
        title={"text": f"{ticker} Price", "font": {"size": 14}} if ticker else None,
        hovermode="x unified",
        showlegend=False,
        xaxis={
            "rangeslider": {"visible": False},
            "showgrid": True,
            "gridcolor": "#1e2130",
            "zeroline": False,
        },
        yaxis={
            "domain": [0.28, 1.0],
            "showgrid": True,
            "gridcolor": "#1e2130",
            "zeroline": False,
            "side": "right",
        },
        yaxis2={
            "domain": [0.0, 0.25],
            "showgrid": False,
            "zeroline": False,
            "side": "right",
        },
        bargap=0.1,
    )
    return fig


def price_band_chart(
    dates: list[Any],
    closes: list[float],
    ticker: str = "",
) -> go.Figure:
    """Simple line chart for price history."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=closes, mode="lines", name=ticker,
        line={"color": "#00D4AA", "width": 2},
        fill="tozeroy", fillcolor="rgba(0,212,170,0.08)",
    ))
    fig.update_layout(
        template=_TEMPLATE, paper_bgcolor=_BG, plot_bgcolor=_BG,
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        title=f"{ticker} Close Price" if ticker else None,
    )
    return fig


def backtest_equity_chart(dates: list[Any], equity: list[float]) -> go.Figure:
    """Equity curve for backtest results."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=equity, mode="lines", name="Portfolio Value",
        line={"color": "#00D4AA", "width": 2},
        fill="tozeroy", fillcolor="rgba(0,212,170,0.08)",
    ))
    fig.update_layout(
        template=_TEMPLATE, paper_bgcolor=_BG, plot_bgcolor=_BG,
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        title="Equity Curve",
    )
    return fig
