"""Report writer — persists analysis results to disk."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from apex.reports.markdown import generate_report_markdown, generate_section_markdown


class ReportWriter:
    """Write analysis results to a timestamped report directory under reports/.

    Directory layout::

        reports/{TICKER}/{timestamp}/
        ├── complete_report.md
        ├── state.json
        ├── metadata.json
        ├── 1_technical/
        │   └── technical.md
        ├── 2_fundamental/
        │   └── fundamental.md
        ├── 3_risk/
        │   └── risk.md
        └── 4_portfolio/
            └── decision.md
    """

    def __init__(self, base_dir: str | Path = "reports") -> None:
        self.base_dir = Path(base_dir)

    def save(self, result: dict[str, Any], state: dict[str, Any] | None = None, *, language: str = "English") -> Path:
        """Persist an analysis result to disk and return the report directory."""
        ticker = result.get("ticker", "UNKNOWN")
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        report_dir = self.base_dir / ticker / timestamp
        report_dir.mkdir(parents=True, exist_ok=True)

        complete = generate_report_markdown(result, language=language)
        (report_dir / "complete_report.md").write_text(complete, encoding="utf-8")

        if state is not None:
            state_safe = self._json_safe(state)
            if not (report_dir / "state.json").exists():
                (report_dir / "state.json").write_text(
                    json.dumps(state_safe, indent=2, default=str), encoding="utf-8"
                )

        agent_outputs = result.get("agent_outputs") or {}
        section_map = {
            "1_technical": "technical",
            "2_fundamental": "fundamental",
            "3_risk": "risk",
            "4_portfolio": "portfolio",
        }
        agent_name_map = {
            "technical": "technical_agent",
            "fundamental": "fundamental_agent",
            "risk": "risk_agent",
            "portfolio": "portfolio_manager",
        }
        section_filename_map = {
            "technical": "technical.md",
            "fundamental": "fundamental.md",
            "risk": "risk.md",
            "portfolio": "decision.md",
        }
        for section_dir, agent_key in section_map.items():
            section_path = report_dir / section_dir
            section_path.mkdir(exist_ok=True)
            output = agent_outputs.get(agent_key)
            aname = agent_name_map.get(agent_key, agent_key)
            section_md = generate_section_markdown(aname, output, language=language)
            fname = section_filename_map.get(agent_key, f"{agent_key}.md")
            section_path.joinpath(fname).write_text(section_md, encoding="utf-8")

        metadata = self._build_metadata(result, timestamp)
        (report_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, default=str), encoding="utf-8"
        )

        return cast(Path, report_dir)

    def _build_metadata(self, result: dict[str, Any], timestamp: str) -> dict[str, Any]:
        usage = result.get("usage") or {}
        return {
            "ticker": result.get("ticker"),
            "analysis_date": result.get("analysis_date"),
            "mode": result.get("mode", "full"),
            "signal": result.get("signal"),
            "confidence": result.get("confidence"),
            "created_at": timestamp,
            "request_hash": result.get("request_hash"),
            "language": result.get("language", "English"),
            "usage": {
                "tokens_in": usage.get("tokens_in", 0),
                "tokens_out": usage.get("tokens_out", 0),
                "cost_usd": usage.get("cost_usd"),
            },
            "error_count": len(result.get("errors") or []),
            "agent_count": len(result.get("agent_outputs") or {}),
        }

    @staticmethod
    def _json_safe(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: ReportWriter._json_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [ReportWriter._json_safe(v) for v in obj]
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)

    @staticmethod
    def load_report(report_dir: str | Path) -> dict[str, Any]:
        """Load a saved report directory into a dict with report_md, state, and metadata."""
        report_dir = Path(report_dir)
        result: dict[str, Any] = {}
        complete = report_dir / "complete_report.md"
        if complete.exists():
            result["report_md"] = complete.read_text(encoding="utf-8")
        state_file = report_dir / "state.json"
        if state_file.exists():
            result["state"] = json.loads(state_file.read_text(encoding="utf-8"))
        metadata_file = report_dir / "metadata.json"
        if metadata_file.exists():
            result["metadata"] = json.loads(metadata_file.read_text(encoding="utf-8"))
        return result
