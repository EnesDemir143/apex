---
phase: 07-workflow-assembly-resilience
plan: 02
subsystem: resilience
tags: [redis, circuit-breaker, retry, fallback, llm-cache]
requires:
  - phase: 05-domain-models-core-services
    provides: Redis cache service and LLM client abstraction
  - phase: 06-langgraph-agents-individual
    provides: AgentState and technical indicator payload shape
provides:
  - Redis-backed circuit breaker
  - Async exponential retry decorator
  - RSI-only rule-based fallback
  - Redis-backed LLM response cache
affects: [agent-workflow, degraded-mode, cost-control]
tech-stack:
  added: []
  patterns: [Redis state persistence, deterministic degraded fallback, TTL response caching]
key-files:
  created:
    - src/apex/agents/circuit_breaker.py
    - src/apex/agents/retry.py
    - src/apex/agents/fallback.py
    - src/apex/services/llm_cache.py
  modified:
    - src/apex/agents/workflow.py
    - tests/unit/test_workflow.py
key-decisions:
  - "Fallback output is analysis-only and low confidence; it never executes trades."
  - "Circuit state is persisted in Redis keys so failures survive process restarts."
patterns-established:
  - "Circuit opens after 3 failures and recovers through half-open state."
  - "LLM cache key hashes ticker + date + agent + prompt_version with a 24h TTL."
requirements-completed: [CACHE-02, RES-01, RES-02, RES-03, RES-04]
duration: 35 min
completed: 2026-05-01
---

# Phase 7 Plan 02: Resilience Summary

**Redis-backed circuit breaking, exponential retry, deterministic fallback, workflow guards, and LLM response caching**

## Performance

- **Duration:** 35 min
- **Started:** 2026-05-01
- **Completed:** 2026-05-01
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added `CircuitBreaker` with `CLOSED`, `OPEN`, and `HALF_OPEN` states.
- Added `CircuitOpenError` for explicit fallback routing.
- Persisted circuit state, failure count, and open timestamp in Redis.
- Added async retry decorator with exponential backoff (`base_delay=1s`, `max_delay=30s`, `max_retries=3`).
- Added `rule_based_fallback()` with RSI-only BUY/SELL/HOLD behavior and confidence `0.3`.
- Added `LLMCacheService` with SHA-256 cache key and 24h TTL.
- Added explicit workflow guards: `MAX_AGENT_ITERATIONS = 5` and `WORKFLOW_TIMEOUT_SECONDS = 120`.

## Task Commits

1. **Task 1: Circuit breaker and retry** — `d79c0cd`
2. **Task 2: Fallback and LLM cache** — `d79c0cd`
3. **RES-01 guard follow-up** — `6eea858`

## Files Created/Modified

- `src/apex/agents/circuit_breaker.py` — Redis-backed circuit breaker.
- `src/apex/agents/retry.py` — async retry decorator.
- `src/apex/agents/fallback.py` — RSI-only fallback output.
- `src/apex/services/llm_cache.py` — Redis-backed LLM response cache.
- `src/apex/agents/workflow.py` — timeout and max-iteration guard constants/config.
- `tests/unit/test_workflow.py` — workflow guard regression coverage.

## Decisions Made

- Fallback confidence is intentionally low (`0.3`) to make degraded decisions visibly weaker.
- LLM cache stores response content, not provider objects, to keep the cache simple and serializable.
- Workflow timeout uses `asyncio.timeout()` around the full invocation path.

## Deviations from Plan

None - plan executed within the intended Phase 7 boundary.

## Issues Encountered

- `RES-01` was not explicit in the first implementation pass; added `6eea858` before updating planning artifacts so tracking matches code.

## User Setup Required

- Redis must be reachable for live circuit-breaker and cache behavior.

## Next Phase Readiness

Frontend and monitoring phases can surface degraded/fallback states and cache/cost behavior as product telemetry.

---
*Phase: 07-workflow-assembly-resilience*
*Completed: 2026-05-01*
