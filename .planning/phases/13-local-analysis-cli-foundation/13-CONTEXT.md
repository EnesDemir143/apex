# Phase 13: Local Analysis + CLI Foundation — Context

**Gathered:** 2026-05-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the existing LangGraph workflow callable from the future interactive Apex app without requiring FastAPI, Streamlit, PostgreSQL, Redis, or K8s to be running.
Build the initial `apex` entrypoint and local runtime seams, but keep the visual full-screen TUI for Phase 14.
</domain>

<decisions>
## Implementation Decisions

### Entrypoint direction
- The primary UX should be `apex` opening the app/cockpit, not requiring users to run `apex analyze AAPL` as the main path.
- Keep a lightweight classic command path only as a fallback/dev/scripting helper.
- Do not adopt Textual in Phase 13; Phase 13 prepares the runtime model that Textual uses in Phase 14.

### Core boundary
- Add a local service seam such as `src/apex/services/local_analysis.py`.
- This service owns creating `AgentState`, fetching/falling back market data, invoking `analyze_with_workflow`, and returning a stable result object/dict.
- It must accept analysis/as-of date plus optional per-run and per-agent extra instructions so the future TUI can pass user prompts like “Risk Agent: also check volatility regime”.
- TUI and API must share workflow logic but not depend on each other.

### Future TUI data model
- TUI will keep a selected ticker in app state.
- TUI will keep a selected analysis/as-of date in app state; default current/latest available date, future dates invalid.
- TUI will pass optional analysis notes/extra instructions to the local analysis service.
- TUI will eventually show charts/market panels for the selected ticker above the analysis controls.

### Dependency rule
- Server dependencies may remain installed, but local CLI must not require a running server or DB.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/agents/workflow.py` — compiled workflow and `analyze_with_workflow`
- `src/apex/agents/state.py` — AgentState contract; graphify god node, change carefully
- `src/apex/ingestion/market_data_fetcher.py` — existing market data seam
- `src/apex/api/app.py` and routes — API should become another caller, not required by CLI
- `pyproject.toml` — project scripts and dependencies
</canonical_refs>

<deferred>
## Deferred

- Full-screen TUI widgets/layout: Phase 14
- Markdown report/history: Phase 15
- Streamlit freeze docs: Phase 16
</deferred>

---
*Phase: 13-local-analysis-cli-foundation*
