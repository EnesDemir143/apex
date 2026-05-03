---
phase: 06-langgraph-agents-individual
plan: 01
subsystem: agents
tags: [langgraph, langsmith, pandas, pydantic, llm]
requires:
  - phase: 05-domain-models-core-services
    provides: LLM client abstraction, Signal enum, constants, and service seams
provides:
  - AgentState TypedDict for LangGraph nodes
  - Technical indicator calculations
  - Four standalone async agent nodes
  - Per-agent usage tracking
affects: [phase-07-workflow-assembly, agent-workflow, langsmith-tracing]
tech-stack:
  added: []
  patterns: [async LangGraph node functions, shared LLM trace config, partial state updates]
key-files:
  created:
    - src/apex/agents/state.py
    - src/apex/agents/indicators.py
    - src/apex/agents/_common.py
    - src/apex/agents/technical.py
    - src/apex/agents/fundamental.py
    - src/apex/agents/risk.py
    - src/apex/agents/portfolio_manager.py
    - src/apex/agents/usage_tracker.py
    - tests/unit/test_agents_phase6.py
  modified:
    - src/apex/agents/__init__.py
    - src/apex/services/llm_client.py
key-decisions:
  - "Keep agent nodes standalone; workflow wiring remains Phase 7."
  - "Preserve the Phase 5 LLMClient seam and pass LangSmith config through it."
  - "Keep fundamental RAG as an explicit stub until the planned full RAG phase."
patterns-established:
  - "Agent nodes return partial AgentState updates and append errors instead of raising."
  - "Each LLM call receives run_name plus ticker/agent metadata for LangSmith filtering."
requirements-completed: [AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05, CORE-06, LSMI-01]
duration: 45 min
completed: 2026-04-29
---

# Phase 6 Plan 01: Individual Agent Nodes Summary

**Standalone LangGraph-ready agent nodes with deterministic indicators, traceable LLM calls, and per-agent usage accounting**

## Performance

- **Duration:** 45 min
- **Started:** 2026-04-29T08:55:31Z
- **Completed:** 2026-04-29T09:22:09Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Created `AgentState` with `errors`, `compaction_applied`, agent output fields, and `usage`.
- Added RSI, MACD, Bollinger Bands, SMA, and EMA calculation helpers.
- Built `technical_agent`, `fundamental_agent`, `risk_agent`, and `portfolio_manager`.
- Added LangSmith trace config propagation through the existing LLM client abstraction.
- Added `AnalysisTurnSummary` and `UsageTracker`.
- Added Phase 6 unit coverage for indicators, agent outputs, trace metadata, and usage totals.

## Task Commits

1. **Task 1: Create AgentState and indicators module** — `b1edb06`
2. **Task 2: Create 4 agent nodes** — `315fef6`
3. **Task 3: Create usage tracker** — `a80006f`
4. **Quality gate fixes** — `b0a7204`

## Files Created/Modified

- `src/apex/agents/state.py` — shared LangGraph state contract.
- `src/apex/agents/indicators.py` — pure technical indicator calculations.
- `src/apex/agents/_common.py` — shared node helpers for errors, parsing, trace config, and usage.
- `src/apex/agents/technical.py` — technical indicator + LLM interpretation node.
- `src/apex/agents/fundamental.py` — RAG-stub + LLM fundamental analysis node.
- `src/apex/agents/risk.py` — volatility/drawdown risk node.
- `src/apex/agents/portfolio_manager.py` — final BUY/SELL/HOLD synthesis node.
- `src/apex/agents/usage_tracker.py` — Pydantic usage summary and accumulator.
- `src/apex/services/llm_client.py` — accepts LangChain `RunnableConfig` for trace metadata.
- `tests/unit/test_agents_phase6.py` — Phase 6 unit coverage.

## Decisions Made

- Reused `LLMClient` instead of direct `ChatOpenAI` calls inside agent nodes.
- Kept node outputs as dictionaries for Phase 7 workflow/persistence flexibility.
- Used conservative free-text parsing for signal/confidence because structured tool output enforcement is handled separately in Plan 02.

## Deviations from Plan

None - plan executed within the intended Phase 6 boundary.

## Issues Encountered

- Initial `uv` verification needed cache access outside the workspace; reran with approved escalated execution.
- Ruff/mypy surfaced small formatting and typing issues; fixed in `b0a7204`.

## User Setup Required

None - no external service configuration required. Live LangSmith traces still require normal LangChain/LangSmith environment variables from prior configuration.

## Next Phase Readiness

Phase 7 can import the individual nodes and wire them into a `StateGraph` with parallel specialist execution followed by final decision synthesis.

---
*Phase: 06-langgraph-agents-individual*
*Completed: 2026-04-29*
