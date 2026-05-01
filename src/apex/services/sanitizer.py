"""Input sanitization helpers for Apex API and agent layer."""

from __future__ import annotations

import re

# Patterns that indicate prompt injection or SQL injection attempts
_HTML_TAG = re.compile(r"<[^>]+>")
_SQL_INJECTION = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE|CAST|CONVERT|DECLARE)\b|--|;)",
    re.IGNORECASE,
)
_PROMPT_INJECTION = re.compile(
    r"(ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|context)|"
    r"you\s+are\s+now|act\s+as\s+a|forget\s+(everything|all)|"
    r"system\s*:\s*|<\s*system\s*>)",
    re.IGNORECASE,
)
_TICKER_VALID = re.compile(r"[^A-Z0-9.\-]")


def sanitize_text(text: str, max_length: int = 4096) -> str:
    """Strip HTML tags, SQL injection patterns, and prompt injection attempts.

    Returns a cleaned string safe for use in LLM prompts and DB queries.
    """
    cleaned = _HTML_TAG.sub("", text)
    cleaned = _SQL_INJECTION.sub("", cleaned)
    cleaned = _PROMPT_INJECTION.sub("", cleaned)
    cleaned = cleaned.strip()
    return cleaned[:max_length]


def canonicalize_ticker(ticker: str) -> str:
    """Normalize a ticker symbol to uppercase with no whitespace or invalid chars."""
    upper = ticker.strip().upper()
    return _TICKER_VALID.sub("", upper)
