---
phase: 05-domain-models-core-services
plan: 02
subsystem: services
tags: [llm-client, redis, sqlalchemy, repository, budget-guard]
requires:
  - phase: 04-database-schema-data-pipeline-completion
    provides: SQLAlchemy ORM models and database schema
  - phase: 05-domain-models-core-services
    provides: ApexError hierarchy and constants
provides:
  - LLMClient ABC with OpenAI and Fake implementations
  - BudgetLimiter with Redis/in-memory daily usage tracking
  - Async SQLAlchemy session factory
  - Redis client factory and cache service
  - Stock and Analysis repositories
affects: [phase-06-agents, phase-07-workflow, api]
tech-stack:
  added: []
  patterns: [ABC provider abstraction, repository pattern, async dependency factories, Redis key prefixing]
key-files:
  created:
    - src/apex/services/llm_client.py
    - src/apex/services/cost_guard.py
    - src/apex/infrastructure_layer/database.py
    - src/apex/infrastructure_layer/redis_client.py
    - src/apex/services/cache_service.py
    - src/apex/services/stock_repository.py
    - src/apex/services/analysis_repository.py
  modified: []
key-decisions:
  - "Use FakeLLMClient as the deterministic test seam for later workflow tests."
  - "BudgetLimiter falls back to in-memory tracking when Redis is not injected."
  - "Repositories accept AsyncSession in constructors."
patterns-established:
  - "Services depend on Settings and ORM models, while API/agents depend on service abstractions."
  - "Redis-backed helpers accept injected clients for tests."
requirements-completed: [CORE-04, CORE-05, DB-04, DB-05, CACHE-01]
duration: 28 min
completed: 2026-04-29
---

# Phase 05 Plan 02: Core Services Summary

**Async service foundations for LLM generation, budget enforcement, database sessions, Redis caching, and repository access**

## Performance

- **Duration:** 28 min
- **Started:** 2026-04-29T08:34:00Z
- **Completed:** 2026-04-29T09:05:00Z
- **Tasks:** 3/3 complete
- **Files modified:** 7

## Accomplishments

- Added `LLMClient` abstraction, `OpenAIClient`, `FakeLLMClient`, and normalized `LLMResponse`.
- Added `BudgetLimiter` with daily budget checks and Redis/in-memory storage.
- Added async SQLAlchemy engine/session factory and Redis client dependency helpers.
- Added `CacheService`, `StockRepository`, and `AnalysisRepository`.

## Task Commits

1. **Task 1: Create LLM client and cost guard** — `1ac3eaf`
2. **Task 2: Create database and Redis infrastructure** — `1ac3eaf`
3. **Task 3: Create repositories** — `1ac3eaf`
4. **Quality gate fixes** — `2200e5c`

## Files Created/Modified

- `src/apex/services/llm_client.py` — LLM abstraction and OpenAI/Fake clients.
- `src/apex/services/cost_guard.py` — daily budget limiter.
- `src/apex/infrastructure_layer/database.py` — async engine/sessionmaker and FastAPI dependency.
- `src/apex/infrastructure_layer/redis_client.py` — Redis client singleton/dependency.
- `src/apex/services/cache_service.py` — Redis cache wrapper with `apex:` key prefix.
- `src/apex/services/stock_repository.py` — stock CRUD repository.
- `src/apex/services/analysis_repository.py` — analysis run CRUD repository.

## Decisions Made

- Instantiated `ChatOpenAI` inside `OpenAIClient.generate()` so per-call temperature and max-token overrides stay simple.
- Used Redis injection for `BudgetLimiter` and `CacheService` to keep tests deterministic.
- Repositories use ORM models from `apex.infrastructure_layer.models`, not domain DTOs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Adjusted ChatOpenAI typing and message list typing**
- **Found during:** `uv run mypy src`.
- **Issue:** mypy reported constructor keyword and message list type issues.
- **Fix:** Used installed `ChatOpenAI` signature-compatible fields, typed messages as `list[BaseMessage]`, and added a scoped `type: ignore[call-arg]` for third-party constructor stubs.
- **Files modified:** `src/apex/services/llm_client.py`.
- **Verification:** `uv run mypy src` passed.
- **Committed in:** `2200e5c`

---

**Total deviations:** 1 auto-fixed type-check issue.  
**Impact on plan:** No scope expansion; service contracts remain as planned.

## Issues Encountered

- Live OpenAI, PostgreSQL, and Redis calls were not exercised in this phase; imports and deterministic fake client behavior were verified.

## User Setup Required

None - no new external configuration required beyond existing `.env` settings.

## Next Phase Readiness

Phase 6 can use `FakeLLMClient` for deterministic agent tests and `BudgetLimiter` for budget pre-hooks. Phase 7 can compose repositories/cache into the workflow.

---
*Phase: 05-domain-models-core-services*
*Completed: 2026-04-29*
