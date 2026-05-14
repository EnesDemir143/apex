# Phase 15: Reports, History, Replay — Summary

**Completed:** 2026-05-15
**Plan:** 15-PLAN-01 (1 plan, 4 tasks, Wave 1)

## What Was Built

### Task 1: Markdown Analysis Reports
- `src/apex/reports/markdown.py` — Renders full analysis result as sectioned markdown: Executive Summary, Technical Analysis, Fundamental Analysis, Risk Assessment, Portfolio Decision, Disagreements & Caveats, Cost & Token Usage, Disclaimer
- `src/apex/reports/writer.py` — `ReportWriter` persists to `reports/{TICKER}/{timestamp}/` with `complete_report.md`, `state.json`, `metadata.json`, and section folders (`1_technical/`, `2_fundamental/`, `3_risk/`, `4_portfolio/`)
- Signal emoji indicators, disagreement detection between agents, per-agent usage breakdown

### Task 2: JSONL History Store
- `src/apex/services/history_store.py` — Append-only JSONL-backed `HistoryStore` with `append()`, `list(limit, ticker)`, `latest(ticker)`, `find_by_hash()`, `list_by_hash()`
- Each entry stores: request_hash, ticker, analysis_date, mode, signal, confidence, report_dir, tokens, cost, error_count

### Task 2.5: Cache-First Lookup
- `_compute_request_hash()` — Deterministic SHA-256 hash of normalized request (ticker, date, mode, instructions, agents, schema version)
- `run_local_analysis()` updated with `save_report` and `force` params — checks history cache before running analysis
- Identical repeated analyses reuse saved reports unless `--force` is passed

### Task 3: CLI Commands
- `apex analyze TICKER --save-report` runs analysis + saves report
- `apex analyze TICKER --save-report --force` forces re-run even if cached
- `apex history [--ticker T] [--limit N]` — lists saved runs
- `apex report TICKER [--latest]` — displays saved report markdown
- `apex replay PATH` — renders saved report without rerunning LLM

## Verification
- Ruff clean, mypy clean
- 43 new unit tests (21 reports + 22 history)
- 134 total tests pass

## Files Created/Modified
- `src/apex/reports/__init__.py` (updated exports)
- `src/apex/reports/markdown.py` (new)
- `src/apex/reports/writer.py` (new)
- `src/apex/services/history_store.py` (new)
- `src/apex/services/local_analysis.py` (updated)
- `src/apex/cli/main.py` (updated)
- `tests/unit/test_reports.py` (21 tests, new)
- `tests/unit/test_history_store.py` (22 tests, new)
