"""Unit tests for HistoryStore (JSONL-backed local analysis history)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apex.services.history_store import HistoryStore, _compute_request_hash


# ---------------------------------------------------------------------------
# _compute_request_hash
# ---------------------------------------------------------------------------


def test_request_hash_deterministic() -> None:
    h1 = _compute_request_hash("AAPL", "2026-01-15", "full")
    h2 = _compute_request_hash("AAPL", "2026-01-15", "full")
    assert h1 == h2


def test_request_hash_changes_with_ticker() -> None:
    h1 = _compute_request_hash("AAPL", "2026-01-15", "full")
    h2 = _compute_request_hash("MSFT", "2026-01-15", "full")
    assert h1 != h2


def test_request_hash_changes_with_date() -> None:
    h1 = _compute_request_hash("AAPL", "2026-01-15", "full")
    h2 = _compute_request_hash("AAPL", "2026-01-16", "full")
    assert h1 != h2


def test_request_hash_changes_with_mode() -> None:
    h1 = _compute_request_hash("AAPL", "2026-01-15", "full")
    h2 = _compute_request_hash("AAPL", "2026-01-15", "quick")
    assert h1 != h2


def test_request_hash_normalizes_ticker_case() -> None:
    h1 = _compute_request_hash("aapl", "2026-01-15", "full")
    h2 = _compute_request_hash("AAPL", "2026-01-15", "full")
    assert h1 == h2


def test_request_hash_includes_instructions() -> None:
    h1 = _compute_request_hash("AAPL", "2026-01-15", "full", extra_instructions="focus on risk")
    h2 = _compute_request_hash("AAPL", "2026-01-15", "full", extra_instructions="focus on growth")
    assert h1 != h2


def test_request_hash_excludes_volatile_fields() -> None:
    """Hash depends only on normalized request fields, not on output."""
    h = _compute_request_hash("AAPL", "2026-01-15", "full")
    assert isinstance(h, str)
    assert len(h) == 64  # SHA-256 hex
    assert h == _compute_request_hash("AAPL", "2026-01-15", "full")  # deterministic


# ---------------------------------------------------------------------------
# HistoryStore
# ---------------------------------------------------------------------------


@pytest.fixture
def store(tmp_path: Path) -> HistoryStore:
    return HistoryStore(path=str(tmp_path / "history.jsonl"))


def _sample_result(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "ticker": "AAPL",
        "signal": "BUY",
        "confidence": 0.85,
        "errors": [],
        "analysis_date": "2026-01-15",
        "mode": "full",
        "request_hash": "abc123",
        "usage": {"tokens_in": 100, "tokens_out": 200, "cost_usd": 0.001},
        "agent_outputs": {"technical": {"signal": "BUY"}},
    }
    data.update(overrides)
    return data


def test_store_append_creates_file(store: HistoryStore) -> None:
    store.append(_sample_result())
    assert store.path.exists()


def test_store_append_adds_line(store: HistoryStore) -> None:
    store.append(_sample_result())
    lines = store.path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1


def test_store_append_returns_entry(store: HistoryStore) -> None:
    entry = store.append(_sample_result())
    assert entry["ticker"] == "AAPL"
    assert entry["signal"] == "BUY"
    assert "created_at" in entry


def test_store_list_returns_newest_first(store: HistoryStore) -> None:
    store.append(_sample_result(ticker="AAPL"))
    store.append(_sample_result(ticker="MSFT"))
    entries = store.list()
    assert len(entries) == 2
    assert entries[0]["ticker"] == "MSFT"


def test_store_list_limit(store: HistoryStore) -> None:
    for i in range(5):
        store.append(_sample_result(ticker=f"TK{i}"))
    entries = store.list(limit=3)
    assert len(entries) == 3


def test_store_list_filter_by_ticker(store: HistoryStore) -> None:
    store.append(_sample_result(ticker="AAPL"))
    store.append(_sample_result(ticker="MSFT"))
    entries = store.list(ticker="AAPL")
    assert len(entries) == 1
    assert entries[0]["ticker"] == "AAPL"


def test_store_list_empty_when_no_file(tmp_path: Path) -> None:
    store = HistoryStore(path=str(tmp_path / "nonexistent.jsonl"))
    assert store.list() == []


def test_store_latest_returns_most_recent(store: HistoryStore) -> None:
    store.append(_sample_result(ticker="AAPL"))
    store.append(_sample_result(ticker="MSFT"))
    latest = store.latest()
    assert latest is not None
    assert latest["ticker"] == "MSFT"


def test_store_latest_filter_by_ticker(store: HistoryStore) -> None:
    store.append(_sample_result(ticker="AAPL", request_hash="h1"))
    store.append(_sample_result(ticker="MSFT", request_hash="h2"))
    store.append(_sample_result(ticker="AAPL", request_hash="h3"))
    latest = store.latest(ticker="AAPL")
    assert latest is not None
    assert latest["request_hash"] == "h3"


def test_store_latest_empty(store: HistoryStore) -> None:
    assert store.latest() is None


def test_store_find_by_hash_found(store: HistoryStore) -> None:
    store.append(_sample_result(request_hash="abc"))
    store.append(_sample_result(request_hash="def"))
    entry = store.find_by_hash("abc")
    assert entry is not None
    assert entry["request_hash"] == "abc"


def test_store_find_by_hash_not_found(store: HistoryStore) -> None:
    store.append(_sample_result(request_hash="abc"))
    assert store.find_by_hash("xyz") is None


def test_store_list_by_hash(store: HistoryStore) -> None:
    store.append(_sample_result(request_hash="abc", ticker="AAPL"))
    store.append(_sample_result(request_hash="abc", ticker="MSFT"))
    store.append(_sample_result(request_hash="xyz", ticker="GOOGL"))
    matches = store.list_by_hash("abc")
    assert len(matches) == 2


def test_store_append_with_report_dir(store: HistoryStore) -> None:
    entry = store.append(_sample_result(), report_dir="reports/AAPL/20260115_120000")
    assert entry["report_dir"] == "reports/AAPL/20260115_120000"


def test_store_can_parse_multiple_entries(store: HistoryStore) -> None:
    data = [
        _sample_result(ticker="AAPL", request_hash="h1"),
        _sample_result(ticker="MSFT", request_hash="h2"),
        _sample_result(ticker="GOOGL", request_hash="h3"),
    ]
    for d in data:
        store.append(d)

    entries = store.list()
    assert len(entries) == 3
    assert entries[0]["request_hash"] == "h3"
    assert entries[2]["request_hash"] == "h1"
