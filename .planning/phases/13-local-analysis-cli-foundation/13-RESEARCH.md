# Phase 13: Local Analysis + CLI Foundation — Research

## Existing Code Findings

- `src/apex/agents/workflow.py` already exposes `analyze_with_workflow(state: AgentState)` and `workflow_run_config(ticker)`.
- `AgentState` is a central graphify god node; changes must be minimal and backward-compatible.
- Existing API persistence is in `persist_workflow_results(...)`; local CLI should not call this by default.
- Market data clients exist under `src/apex/ingestion/`; local analysis can reuse fetcher logic or deterministic fallback if credentials are unavailable.

## CLI Library Approach

- Typer is appropriate for command routing (`apex analyze AAPL`, `apex tui`, `apex history`).
- Rich is appropriate for first-pass readable terminal output and progress display.
- This keeps Phase 13 simple; Textual can be introduced only once a stable local analysis seam exists.

## Risk

Do not wire CLI through FastAPI HTTP. That would preserve the server dependency and defeat the local-first goal.
