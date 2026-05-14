"""Top Signals leaderboard — clickable rows update selected_symbol."""

from __future__ import annotations

import streamlit as st

_SIG_COLOR = {"BUY": "#00D4AA", "SELL": "#FF4B4B", "HOLD": "#FFD700"}
_RISK_COLOR = {"Low": "#00D4AA", "Medium": "#FFD700", "High": "#FF4B4B"}


def _badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;">{text}</span>'
    )


def _conf_bar(pct: float, color: str) -> str:
    """Mini progress bar for confidence."""
    w = int(pct * 60)
    return (
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<span style="color:{color};font-weight:600;font-size:13px;">{pct:.0%}</span>'
        f'<div style="background:#2A2F3E;border-radius:3px;height:5px;width:60px;">'
        f'<div style="background:{color};border-radius:3px;height:5px;width:{w}px;"></div>'
        f"</div></div>"
    )


def signal_leaderboard(signals: list[dict]) -> None:
    """Render the Top Signals table with clickable symbol buttons."""
    # Header row
    h1, h2, h3, h4, h5, h6 = st.columns([1.2, 1, 1.4, 1, 1, 1])
    for col, label in zip(
        [h1, h2, h3, h4, h5, h6], ["Symbol", "Signal", "Confidence", "Risk", "Agreement", "Last Analysis"]
    ):
        col.markdown(
            f'<div style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:1px;padding-bottom:4px;">{label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border-color:#2A2F3E;margin:0 0 4px;">', unsafe_allow_html=True)

    for row in signals:
        sym = row["symbol"]
        sig = row["signal"]
        conf = row["confidence"]
        risk = row["risk"]
        agree = row["agreement"]
        last = row["last_analysis"]

        sc = _SIG_COLOR.get(sig, "#888")
        rc = _RISK_COLOR.get(risk, "#888")

        c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1, 1.4, 1, 1, 1])

        with c1:
            if st.button(sym, key=f"sig_btn_{sym}", use_container_width=False):
                st.session_state.selected_symbol = sym
                st.rerun()

        c2.markdown(_badge(sig, sc), unsafe_allow_html=True)
        c3.markdown(_conf_bar(conf, sc), unsafe_allow_html=True)
        c4.markdown(_badge(risk, rc), unsafe_allow_html=True)
        c5.markdown(f'<span style="color:#AAA;font-size:13px;">{agree}</span>', unsafe_allow_html=True)
        c6.markdown(f'<span style="color:#666;font-size:12px;">{last}</span>', unsafe_allow_html=True)

        st.markdown('<div style="border-bottom:1px solid #1E2535;margin:2px 0;"></div>', unsafe_allow_html=True)
