"""Local-first knowledge retrieval for Apex Fundamental Agent.

Discovers markdown knowledge files from ``~/.apex/knowledge/{TICKER}/``
and returns snippets with source paths.  No server or vector DB required.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _knowledge_base_path() -> Path:
    return Path.home() / ".apex" / "knowledge"


def find_knowledge(ticker: str) -> list[dict[str, Any]]:
    """Return list of {path, content} entries for *ticker* knowledge files.

    Returns empty list when no knowledge directory exists for the ticker.
    """
    ticker_dir = _knowledge_base_path() / ticker.upper()
    if not ticker_dir.is_dir():
        return []

    results: list[dict[str, Any]] = []
    for md_file in sorted(ticker_dir.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8").strip()
            if content:
                results.append({"path": str(md_file), "content": content})
        except OSError:
            continue
    return results


def format_knowledge_context(items: list[dict[str, Any]]) -> str:
    """Format knowledge items into a prompt-ready context string."""
    if not items:
        return ""

    parts: list[str] = []
    for item in items:
        parts.append(f"--- {item['path']} ---")
        parts.append(item["content"][:2000])
        parts.append("")
    return "\n".join(parts)


def knowledge_base_path() -> str:
    """Return the knowledge base directory path for display."""
    return str(_knowledge_base_path())
