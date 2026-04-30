---
phase: 07-workflow-assembly-resilience
plan: 01
subsystem: agent-workflow
tags: [langgraph, checkpointing, compaction, langsmith, persistence]
requires:
  - phase: 06-langgraph-agents-individual
    provides: standalone agent nodes, hooks, AgentState, and usage metadata
provides:
  - Compiled LangGraph workflow assembly
  - PostgreSQL checkpoint saver setup
  - Context compaction seam
  - Parallel state reducers
  - Workflow result persistence helper
affects: [phase-08-streamlit-frontend, phase-09-monitoring, langsmith-tracing]
tech-stack:
  added: [langgraph-checkpoint-postgres, psycopg, psycopg-pool, psycopg-binary]
  patterns: [StateGraph assembly, reducer-backed parallel state merge, LangGraph-managed checkpoint schema]
key-files:
  created:
    - src/apex/agents/workflow.py
    - src/apex/agents/checkpoint.py
    - src/apex/agents/compaction.py
  modified:
    - src/apex/agents/state.py
    - src/apex/agents/__init__.py
    - pyproject.toml
    - uv.lock
key-decisions:
  - "Post-hook runs after portfolio_manager because the current hook validates portfolio_decision."
  - "Checkpoint tables are owned by AsyncPostgresSaver.setup(), not Alembic."
  - "Parallel branch merge uses Annotated AgentState reducers."
patterns-established:
  - "create_workflow() is the main workflow factory; create_workflow_with_checkpointer() adds durable execution."
  - "workflow_run_config() carries project=apex metadata for end-to-end LangSmith traces."
requirements-completed: [AGENT-06, AGENT-07, AGENT-09, LSMI-02]
duration: 45 min
completed: 2026-05-01
---

# Phase 7 Plan 01: Workflow Assembly Summary

**Full LangGraph workflow foundation with parallel specialist execution, checkpoint setup, compaction, and persistence seams**

## Performance

- **Duration:** 45 min
- **Started:** 2026-05-01
- **Completed:** 2026-05-01
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added `create_workflow()` with `StateGraph(AgentState)`.
- Wired `pre_hook` → parallel `technical`, `fundamental`, `risk` branches → `compact_context` → `portfolio_manager` → `post_hook` → `END`.
- Added `create_workflow_with_checkpointer()` for durable LangGraph execution.
- Added PostgreSQL checkpoint helper using `AsyncPostgresSaver.setup()`.
- Added context compaction with `compaction_applied=True` when rough token budget exceeds 80%.
- Added state reducers for parallel `errors`, `usage`, and `compaction_applied` merges.
- Added `persist_workflow_results()` to write analysis run and per-agent decisions.

## Task Commits

1. **Task 1: StateGraph workflow assembly** — `d46a709`
2. **Task 2: Checkpoint saver and compaction** — `d46a709`
3. **Resilience guard follow-up** — `6eea858`

## Files Created/Modified

- `src/apex/agents/workflow.py` — workflow factory, LangSmith config, persistence helper.
- `src/apex/agents/checkpoint.py` — PostgreSQL checkpointer setup/cleanup helpers.
- `src/apex/agents/compaction.py` — deterministic context compaction helper.
- `src/apex/agents/state.py` — reducer-backed parallel merge semantics.
- `src/apex/agents/__init__.py` — workflow exports.
- `pyproject.toml`, `uv.lock` — checkpoint persistence dependencies.

## Decisions Made

- Post-hook runs after Portfolio Manager because the current post-hook requires `portfolio_decision`.
- Checkpoint schema remains outside app Alembic migrations; LangGraph owns it.
- Context compaction is deterministic string truncation for MVP safety rather than another LLM call.

## Deviations from Plan

### Intentional order adjustment

- **Plan text:** `pre_hook → [agents] → post_hook → portfolio_manager`.
- **Implementation:** `pre_hook → [agents] → compact_context → portfolio_manager → post_hook`.
- **Reason:** Existing `post_analysis_hook()` validates `portfolio_decision`; running it before Portfolio Manager would fail every valid workflow.
- **Impact:** Preserves security intent by validating final output immediately before returning/persisting it.

## Issues Encountered

- `langgraph-checkpoint-postgres` and `psycopg-pool` were required but not previously installed; added with `uv add`.
- The GSD SDK plan index did not detect Phase 7 plan files because this project uses `07-PLAN-01.md` naming; execution was completed inline using the plan files directly.

## User Setup Required

- Durable checkpoint execution needs a reachable PostgreSQL database URL.
- LangSmith trace visibility still requires configured LangChain/LangSmith environment variables.

## Next Phase Readiness

Phase 8 can call the real analysis endpoint and display workflow-backed output, agent details, status, and usage summary.

---
*Phase: 07-workflow-assembly-resilience*
*Completed: 2026-05-01*
