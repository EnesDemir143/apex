# Phase 12: TUI Pivot Product Cleanup — Context

**Gathered:** 2026-05-03
**Status:** Ready for planning
**Source:** Bet 5 TUI pivot conversation + `plans/BET5_POSTPROD_PLAN.md`

<domain>
## Phase Boundary

Reposition Apex from a server-first web/dashboard trading app to a **local-first TUI multi-agent market research cockpit**.
This phase is docs/planning/product cleanup only. It must not implement the TUI yet.
</domain>

<decisions>
## Implementation Decisions

### Locked direction
- Primary product experience becomes CLI/TUI: `apex analyze`, `apex tui`, `apex report`, `apex history`, `apex backtest`.
- Web/server stack is preserved but no longer the main Bet 5 path.
- Streamlit remains in the repo as an optional/legacy dashboard; do not delete it.
- FastAPI, PostgreSQL, Redis, K8s, and observability remain as optional production extension evidence for CV.
- Remove web production frontend rewrite language from active roadmap/README.

### CV framing
- README should honestly explain the pivot: the project started as a production-style web dashboard, then shifted to local-first TUI to avoid hosting cost and improve demo/CV impact.
- Keep the story professional: this is a deliberate product strategy decision, not a failure.
</decisions>

<canonical_refs>
## Canonical References

- `plans/BET5_POSTPROD_PLAN.md` — source of Bet 5 pivot scope and priorities
- `README.md` — primary public product story to update
- `.planning/ROADMAP.md` — phase list and status table
- `.planning/PROJECT.md` — project definition and constraints
- `.planning/REQUIREMENTS.md` — requirements IDs for TUI pivot
- `GEMINI.md` — GSD project guide and manual verification expectations
</canonical_refs>

<deferred>
## Deferred

- TUI implementation starts in Phase 13/14.
- Streamlit freeze implementation starts in Phase 16.
- Local RAG/provider/backtest polish starts after TUI MVP works.
</deferred>

---
*Phase: 12-tui-pivot-product-cleanup*
*Context gathered: 2026-05-03*
