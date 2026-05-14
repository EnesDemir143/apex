"""JSONL-backed local history store for Apex analysis runs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _compute_request_hash(
    ticker: str,
    analysis_date: str,
    mode: str,
    extra_instructions: str | None = None,
    agent_instructions: dict[str, str] | None = None,
    enabled_agents: list[str] | None = None,
    schema_version: str = "1",
) -> str:
    """Deterministic hash of a normalized analysis request.

    Excludes volatile fields: timestamps, token counts, generated text, report paths.
    """
    normalized = {
        "ticker": ticker.upper().strip(),
        "analysis_date": analysis_date.strip() if analysis_date else "",
        "mode": mode.strip() if mode else "full",
        "extra_instructions": (extra_instructions or "").strip(),
        "agent_instructions": {k: v.strip() for k, v in (agent_instructions or {}).items()},
        "enabled_agents": sorted(enabled_agents or []),
        "schema_version": schema_version,
    }
    raw = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class HistoryStore:
    """Append-only JSONL history of local analysis runs.

    Each line is a JSON object with metadata about one completed analysis.
    """

    def __init__(self, path: str | Path = "reports/history.jsonl") -> None:
        self.path = Path(path)

    def append(self, result: dict[str, Any], report_dir: str | Path | None = None) -> dict[str, Any]:
        """Append one history entry and return it."""
        now = datetime.now(UTC).isoformat()
        usage = result.get("usage") or {}
        entry = {
            "request_hash": result.get("request_hash"),
            "ticker": result.get("ticker"),
            "analysis_date": result.get("analysis_date"),
            "mode": result.get("mode", "full"),
            "signal": result.get("signal"),
            "confidence": result.get("confidence"),
            "report_dir": str(report_dir) if report_dir else None,
            "created_at": now,
            "tokens_in": usage.get("tokens_in", 0),
            "tokens_out": usage.get("tokens_out", 0),
            "cost_usd": usage.get("cost_usd"),
            "error_count": len(result.get("errors") or []),
            "agent_count": len(result.get("agent_outputs") or {}),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        return entry

    def list(
        self,
        limit: int = 20,
        ticker: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent history entries, newest first."""
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
        entries.reverse()
        if ticker:
            entries = [e for e in entries if e.get("ticker", "").upper() == ticker.upper()]
        return entries[:limit]

    def latest(self, ticker: str | None = None) -> dict[str, Any] | None:
        """Return the most recent entry, optionally filtered by ticker."""
        entries = self.list(limit=1, ticker=ticker)
        return entries[0] if entries else None

    def find_by_hash(self, request_hash: str) -> dict[str, Any] | None:
        """Look up the latest entry by its request hash."""
        if not self.path.exists():
            return None
        found: dict[str, Any] | None = None
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("request_hash") == request_hash:
                    found = entry
        return found

    def list_by_hash(self, request_hash: str) -> list[dict[str, Any]]:  # type: ignore[valid-type]
        """Return all entries matching a given request hash."""
        if not self.path.exists():
            return []
        matches: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("request_hash") == request_hash:
                    matches.append(entry)
        return matches
