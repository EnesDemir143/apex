"""Latest Analysis card — signal, confidence, risk, explanation."""

from __future__ import annotations

import streamlit as st

_SIG_COLOR = {"BUY": "#00D4AA", "SELL": "#FF4B4B", "HOLD": "#FFD700"}
_RISK_COLOR = {"Low": "#00D4AA", "Medium": "#FFD700", "High": "#FF4B4B"}


def latest_analysis_card(symbol: str, analysis: dict) -> None:
    """Render the Latest Analysis card matching the mockup."""
    sig = analysis.get("signal", "HOLD")
    conf = analysis.get("confidence", 0.0)
    risk = analysis.get("risk", "Medium")
    last = analysis.get("last_analysis", "—")
    expl = analysis.get("explanation", "")

    sc = _SIG_COLOR.get(sig, "#888")
    rc = _RISK_COLOR.get(risk, "#888")

    def _badge(text: str, color: str) -> str:
        return f'<span style="color:{color};font-weight:700;font-size:16px;">{text}</span>'

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f'<div style="font-size:10px;color:#555;text-transform:uppercase;">Signal</div>{_badge(sig, sc)}',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div style="font-size:10px;color:#555;text-transform:uppercase;">Confidence</div>{_badge(f"{conf:.0%}", "#F0F0F0")}',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div style="font-size:10px;color:#555;text-transform:uppercase;">Risk</div>{_badge(risk, rc)}',
        unsafe_allow_html=True,
    )
    c4.markdown(
        f'<div style="font-size:10px;color:#555;text-transform:uppercase;">Last Analysis</div><span style="color:#888;font-size:13px;">{last}</span>',
        unsafe_allow_html=True,
    )

    if expl:
        st.markdown(
            f'<div style="margin-top:12px;font-size:13px;color:#AAA;line-height:1.6;'
            f'border-top:1px solid #2A2F3E;padding-top:10px;">{expl}</div>',
            unsafe_allow_html=True,
        )
