# Phase 12: TUI Pivot Product Cleanup — Research

## Research Summary

This phase uses project-local research and product-positioning analysis rather than external framework research.

### Existing project evidence

- `README.md` currently presents Apex as FastAPI + Streamlit + PostgreSQL/Redis + K3s production app.
- `plans/BET5_POSTPROD_PLAN.md` now defines Bet 5 as local-first TUI pivot.
- `.planning/ROADMAP.md` currently ends at Phase 11 and still contains old web-evolution assumptions.
- `GEMINI.md` says GSD is the source of truth for phase execution, so `.planning` must be updated, not only `plans/BET5_POSTPROD_PLAN.md`.

### Graphify evidence

`graphify-out/GRAPH_REPORT.md` shows key nodes that must not be casually broken:

- `AgentState` — 42 edges; central workflow state
- `Signal` — 41 edges; final output contract
- `MarketDataFetcher` / `MarketDataClient` — data entrypoint for local analysis
- `Infrastructure` — 34 edges; should be decoupled from local TUI path, not deleted

### Planning implication

The pivot should be phased so docs and public story change first, then core execution becomes local-first, then UI layers are added. This avoids mixing product messaging cleanup with implementation and respects Karpathy-style surgical changes.
