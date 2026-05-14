"""Alpaca News fetcher with local cache for Fundamental Agent.

First call fetches news from Alpaca News API and caches to
``~/.apex/knowledge/{TICKER}/alpaca_news.md``. Subsequent calls
read from cache (offline-friendly). Use ``refresh=True`` to force
re-fetch.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from alpaca.data import NewsClient, NewsRequest

from apex.core.config import get_settings


def _news_cache_path(ticker: str) -> Path:
    return Path.home() / ".apex" / "knowledge" / ticker.upper() / "alpaca_news.md"


def _format_news_md(articles: list[dict[str, Any]]) -> str:
    lines: list[str] = [f"# Alpaca News — {len(articles)} articles", ""]
    for i, a in enumerate(articles, 1):
        lines.append(f"## {i}. {a.get('headline', 'No headline')}")
        lines.append(f"**Source:** {a.get('source', '?')}  ")
        lines.append(f"**Date:** {a.get('created_at', '?')}  ")
        if a.get("url"):
            lines.append(f"**URL:** {a['url']}  ")
        lines.append(f"**Summary:** {a.get('summary', '')}")
        if a.get("content"):
            lines.append("")
            lines.append(a["content"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def ensure_market_news(
    ticker: str,
    days: int = 365,
    refresh: bool = False,
) -> str | None:
    """Return cached news path for *ticker*, fetching from Alpaca if needed.

    Args:
        ticker: Stock ticker symbol.
        days: How many days of news to fetch on first call.
        refresh: Force re-fetch even if cache exists.

    Returns:
        Path to cached markdown file, or None if Alpaca news unavailable.
    """
    cache_path = _news_cache_path(ticker)
    if cache_path.exists() and not refresh:
        return str(cache_path)

    settings = get_settings()
    api_key = settings.alpaca_api_key.get_secret_value()
    secret_key = settings.alpaca_secret_key.get_secret_value()
    if not api_key or not secret_key:
        return None

    try:
        client = NewsClient(api_key=api_key, secret_key=secret_key)
        now = datetime.now(UTC)
        request = NewsRequest(
            symbols=ticker,
            start=now - timedelta(days=days),
            end=now,
            limit=50,
            include_content=True,
            exclude_contentless=True,
        )
        result = client.get_news(request)
    except Exception:
        return None

    articles_data: list[dict[str, Any]] = []
    for entry in getattr(result, "data", {}).get("news", []):
        articles_data.append(
            {
                "headline": getattr(entry, "headline", ""),
                "source": getattr(entry, "source", ""),
                "summary": getattr(entry, "summary", ""),
                "content": getattr(entry, "content", ""),
                "url": getattr(entry, "url", ""),
                "created_at": str(getattr(entry, "created_at", "")),
            }
        )

    if not articles_data:
        return None

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(_format_news_md(articles_data), encoding="utf-8")
    return str(cache_path)
