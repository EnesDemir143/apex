"""Shared constants for Apex domain and service layers."""

from __future__ import annotations

TICKERS_WHITELIST: tuple[str, ...] = ("AAPL", "MSFT", "NVDA", "TSLA", "SPY")

MAX_CONFIDENCE = 1.0
MIN_CONFIDENCE = 0.0
DEFAULT_TIMEOUT = 120
FALLBACK_CONFIDENCE = 0.3

BUY_CONFIDENCE_THRESHOLD = 0.7
SELL_CONFIDENCE_THRESHOLD = 0.7
HOLD_CONFIDENCE_THRESHOLD = 0.5
