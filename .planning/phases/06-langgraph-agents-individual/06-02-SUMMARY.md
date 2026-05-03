---
phase: 06-langgraph-agents-individual
plan: 02
subsystem: agents-security
tags: [security, pydantic, hooks, validation]
requires:
  - phase: 06-langgraph-agents-individual
    provides: AgentState and portfolio_decision payload shape
provides:
  - Pre-analysis whitelist, prompt injection, and budget snapshot hook
  - Post-analysis output schema and confidence validation hook
  - Pydantic trade decision tool schema
affects: [phase-07-workflow-assembly, security-hooks, tool-isolation]
tech-stack:
  added: []
  patterns: [synchronous hook guards, Pydantic tool boundary validation]
key-files:
  created:
    - src/apex/agents/hooks.py
    - src/apex/agents/tool_schemas.py
  modified:
    - src/apex/agents/__init__.py
    - tests/unit/test_agents_phase6.py
key-decisions:
  - "Keep hooks synchronous for easy Phase 7 graph wiring."
  - "Use the existing HOLD confidence threshold instead of a zero lower bound."
patterns-established:
  - "Pre-hook blocks unsafe input before analysis work starts."
  - "Post-hook normalizes final decisions through TradeDecisionInput before downstream use."
requirements-completed: [AGENT-08, SEC-01, SEC-02, SEC-03]
duration: 25 min
completed: 2026-04-29
---

# Phase 6 Plan 02: Agent Security Hooks Summary

**Three-layer agent safety guardrails with whitelist/prompt-injection prechecks and Pydantic post-decision validation**

## Performance

- **Duration:** 25 min
- **Started:** 2026-04-29T09:22:09Z
- **Completed:** 2026-04-29T09:22:09Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `pre_analysis_hook()` for ticker whitelist, prompt-injection scan, and budget snapshot checks.
- Added `post_analysis_hook()` for final decision schema validation, confidence threshold checks, and instruction hierarchy screening.
- Added `TradeDecisionInput` with bounded confidence and risk score fields.
- Exported hooks/schema through `apex.agents`.
- Added unit tests for blocked tickers, prompt injection, invalid confidence, low confidence, and valid output normalization.

## Task Commits

1. **Task 1: Create pre and post analysis hooks** — `f26432d`
2. **Task 2: Create tool isolation schemas** — `3cabf0d`
3. **Review fix: meaningful confidence gate** — `b64883b`

## Files Created/Modified

- `src/apex/agents/hooks.py` — pre/post analysis hook guards.
- `src/apex/agents/tool_schemas.py` — Pydantic trade decision schema.
- `src/apex/agents/__init__.py` — exports hooks and schema.
- `tests/unit/test_agents_phase6.py` — hook/schema regression tests.

## Decisions Made

- Hook functions remain synchronous because the phase plan specified synchronous pre/post hooks and Phase 7 can call them directly.
- Budget checking uses a snapshot of accumulated cost rather than awaiting Redis; full runtime budget enforcement remains in service/workflow layers.
- Confidence validation uses `HOLD_CONFIDENCE_THRESHOLD` to avoid a no-op `MIN_CONFIDENCE=0.0` gate.

## Deviations from Plan

### Auto-fixed Issues

**1. Confidence threshold was initially too weak**
- **Found during:** Code review gate
- **Issue:** `MIN_CONFIDENCE=0.0` would allow every schema-valid confidence.
- **Fix:** Switched post-hook to `HOLD_CONFIDENCE_THRESHOLD` and added a low-confidence rejection test.
- **Files modified:** `src/apex/agents/hooks.py`, `tests/unit/test_agents_phase6.py`
- **Verification:** Ruff, targeted mypy, and full pytest all passed.
- **Committed in:** `b64883b`

---

**Total deviations:** 1 auto-fixed review issue.
**Impact on plan:** Improved correctness without expanding Phase 6 scope.

## Issues Encountered

None beyond the review fix above.

## User Setup Required

None.

## Next Phase Readiness

Phase 7 can place `pre_analysis_hook` before agent execution and `post_analysis_hook` before returning/persisting final analysis decisions.

---
*Phase: 06-langgraph-agents-individual*
*Completed: 2026-04-29*
