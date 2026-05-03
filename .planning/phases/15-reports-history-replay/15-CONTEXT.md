# Phase 15: Reports, History, Replay — Context

**Gathered:** 2026-05-03
**Status:** Ready for planning after Phase 13/14

<domain>
## Phase Boundary

Make local analyses useful after the terminal session ends: save markdown reports, metadata, history, and replay previously saved runs.
</domain>

<decisions>
## Implementation Decisions

- Start with local filesystem + JSONL history; SQLite may be added later if JSONL becomes limiting.
- Store under project `reports/` by default for repo demo, with future option for `~/.apex` user data.
- Report content must be readable and CV-friendly: executive summary, agent sections, final decision, caveats, cost/tokens.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/domain/value_objects.py` — Signal and domain objects
- `src/apex/agents/workflow.py` — state/result shape
- `README.md` — report examples should be documented
</canonical_refs>

---
*Phase: 15-reports-history-replay*
