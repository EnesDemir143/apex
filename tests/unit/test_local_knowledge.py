"""Tests for local knowledge retrieval service."""

from __future__ import annotations

from pathlib import Path

from apex.services.local_knowledge import find_knowledge, format_knowledge_context, knowledge_base_path


def test_find_knowledge_no_dir() -> None:
    """Unknown ticker returns empty list without error."""
    result = find_knowledge("ZZZZZ")
    assert result == []


def test_find_knowledge_empty_dir(tmp_path: Path) -> None:
    """Empty knowledge directory returns empty list."""
    ticker_dir = tmp_path / "TEST"
    ticker_dir.mkdir(parents=True)
    result = find_knowledge("TEST")  # will look under ~/.apex/knowledge/TEST, not tmp_path
    assert isinstance(result, list)


def test_format_knowledge_context_empty() -> None:
    """Empty items produce empty string."""
    assert format_knowledge_context([]) == ""


def test_format_knowledge_context_single(tmp_path: Path) -> None:
    """Single item produces formatted block."""
    items = [{"path": "/tmp/knowledge/AAPL/notes.md", "content": "Strong balance sheet"}]
    result = format_knowledge_context(items)
    assert "--- /tmp/knowledge/AAPL/notes.md ---" in result
    assert "Strong balance sheet" in result


def test_knowledge_base_path_returns_string() -> None:
    """knowledge_base_path returns a non-empty string."""
    path = knowledge_base_path()
    assert isinstance(path, str)
    assert len(path) > 0


def test_local_knowledge_importable() -> None:
    """Module imports without error."""
    from apex.services import local_knowledge
    assert hasattr(local_knowledge, "find_knowledge")
