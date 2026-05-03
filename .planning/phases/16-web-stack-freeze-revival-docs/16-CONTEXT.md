# Phase 16: Web Stack Freeze + Revival Docs — Context

**Gathered:** 2026-05-03
**Status:** Ready after TUI path is usable

<domain>
## Phase Boundary

Preserve existing Streamlit/FastAPI/Postgres work without keeping it as the primary product path. Document how to revive it later.
</domain>

<decisions>
## Implementation Decisions

- Do not delete Streamlit files.
- Do not remove FastAPI app.
- Make README and docs clear: primary = TUI, optional = Streamlit/API production stack.
- Create `docs/WEB_STACK_REVIVAL_GUIDE.md`.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/frontend/` — Streamlit optional dashboard
- `src/apex/api/` — FastAPI optional API mode
- `docker-compose.*.yml`, `k8s/` — optional production stack
- `plans/BET5_POSTPROD_PLAN.md` — freeze decision source
</canonical_refs>

---
*Phase: 16-web-stack-freeze-revival-docs*
