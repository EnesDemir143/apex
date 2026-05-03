# Phase 18: Turkish Output / Localization — Context

**Gathered:** 2026-05-03
**Status:** Deferred final Bet 5 enhancement

<domain>
## Phase Boundary

Add optional Turkish output/localization after the English-first TUI, reports, history, local knowledge, and provider surfaces are stable.
</domain>

<decisions>
## Implementation Decisions

- MVP output language remains English for GitHub/CV readability and stable tests.
- Turkish support is a later optional mode, not part of the first TUI MVP.
- Do not mix languages inside one report unless explicitly selected.
- UI labels may remain English initially; first useful scope is report/agent output language.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/tui/` — setup panel and output language control once implemented
- `src/apex/reports/markdown.py` — report generation
- `src/apex/agents/*.py` — agent prompt language instructions
- `src/apex/services/local_analysis.py` — analysis config/state entrypoint
</canonical_refs>

<deferred>
## Deferred Ideas

- Full UI label translation
- Multiple output languages beyond Turkish
- Per-section language mixing
</deferred>

---
*Phase: 18-turkish-localization*
