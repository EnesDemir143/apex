"""HTTP client for Apex FastAPI backend."""

from __future__ import annotations

from typing import Any

import httpx
import streamlit as st

BASE_URL = "http://localhost:8000"
_TIMEOUT = 30.0


@st.cache_data(ttl=60)
def fetch_analysis(ticker: str) -> dict[str, Any] | None:
    """POST /api/v1/analyze/{ticker} and return the JSON result."""
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(f"{BASE_URL}/api/v1/analyze/{ticker.upper()}")
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]
    except httpx.HTTPError:
        return None


@st.cache_data(ttl=30)
def fetch_health() -> dict[str, Any]:
    """GET /health and return status dict."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{BASE_URL}/health")
            return resp.json()  # type: ignore[no-any-return]
    except httpx.HTTPError:
        return {"status": "unreachable"}


def clear_analysis_cache(ticker: str) -> None:
    """Invalidate cached analysis for a ticker."""
    fetch_analysis.clear()  # type: ignore[attr-defined]


@st.cache_data(ttl=300)
def fetch_ohlcv(ticker: str, days: int = 60) -> list[dict[str, Any]]:
    """GET /api/v1/ohlcv/{ticker} and return list of bar dicts."""
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(f"{BASE_URL}/api/v1/ohlcv/{ticker.upper()}", params={"days": days})
            resp.raise_for_status()
            data = resp.json()
            return data.get("bars", [])  # type: ignore[no-any-return]
    except httpx.HTTPError:
        return []
