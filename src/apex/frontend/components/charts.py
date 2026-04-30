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
    prediction_high: list[float] | None = None,
    prediction_low: list[float] | None = None,
) -> go.Figure:
    """Candlestick chart with optional prediction band overlay."""
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=dates, open=opens, high=highs, low=lows, close=closes,
        name=ticker, increasing_line_color="#00D4AA", decreasing_line_color="#FF4B4B",
    ))
    if prediction_high and prediction_low:
        fig.add_trace(go.Scatter(
            x=dates + list(reversed(dates)),
            y=prediction_high + list(reversed(prediction_low)),
            fill="toself", fillcolor="rgba(0,212,170,0.15)",
            line={"color": "rgba(0,0,0,0)"}, name="Prediction Band",
        ))
    fig.update_layout(
        template=_TEMPLATE, paper_bgcolor=_BG, plot_bgcolor=_BG,
        xaxis_rangeslider_visible=False, margin={"l": 0, "r": 0, "t": 30, "b": 0},
        title=f"{ticker} Price" if ticker else None,
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
