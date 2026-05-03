---
phase: 05-domain-models-core-services
plan: 01
subsystem: domain
tags: [pydantic, domain-models, value-objects, exceptions]
requires:
  - phase: 03-fastapi-data-ingestion-core
    provides: OHLCV domain model pattern and package layout
provides:
  - Pydantic domain models for stocks, trades, analyses, watchlists, and prediction bands
  - Signal and Indicator value objects
  - Core constants and Apex exception hierarchy
affects: [phase-06-agents, phase-07-workflow, api, services]
tech-stack:
  added: []
  patterns: [Pydantic domain model exports, StrEnum value objects, ApexError hierarchy]
key-files:
  created:
    - src/apex/domain/models/stock.py
    - src/apex/domain/models/trade.py
    - src/apex/domain/models/analysis.py
    - src/apex/domain/models/watchlist.py
    - src/apex/domain/models/prediction_band.py
    - src/apex/domain/value_objects.py
    - src/apex/core/constants.py
    - src/apex/core/exceptions.py
  modified:
    - src/apex/domain/__init__.py
    - src/apex/domain/models/__init__.py
key-decisions:
  - "Use Pydantic BaseModel for domain DTOs and keep SQLAlchemy ORM models separate."
  - "Use StrEnum for Signal to satisfy Python 3.13/Ruff guidance while preserving string values."
patterns-established:
  - "Domain package exports stable public models via apex.domain."
  - "Application-specific errors inherit from ApexError."
requirements-completed: [CORE-01, CORE-02, CORE-03]
duration: 20 min
completed: 2026-04-29
---

# Phase 05 Plan 01: Domain Models and Core Primitives Summary

**Pydantic trading domain primitives with Signal value objects, confidence validation, shared constants, and ApexError hierarchy**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-29T08:10:19Z
- **Completed:** 2026-04-29T08:34:00Z
- **Tasks:** 2/2 complete
- **Files modified:** 10

## Accomplishments

- Added Pydantic domain models for stock, trade, analysis result, watchlist, watchlist item, and prediction band.
- Added `Signal` and `Indicator` value objects.
- Added trading constants and custom exception classes for downstream services.
- Exported the new domain API from `apex.domain` and `apex.domain.models`.

## Task Commits

1. **Task 1: Create domain models and value objects** — `838b4b7`
2. **Task 2: Create constants and exceptions** — `838b4b7`
3. **Quality gate fixes** — `2200e5c`

## Files Created/Modified

- `src/apex/domain/models/stock.py` — `Stock` Pydantic model.
- `src/apex/domain/models/trade.py` — `Trade` Pydantic model.
- `src/apex/domain/models/analysis.py` — `AnalysisResult` model with signal, confidence, summary, usage, and status fields.
- `src/apex/domain/models/watchlist.py` — `WatchlistItem` and `Watchlist` models.
- `src/apex/domain/models/prediction_band.py` — Prediction band model with confidence validation.
- `src/apex/domain/value_objects.py` — `Signal` and `Indicator`.
- `src/apex/core/constants.py` — ticker whitelist, confidence bounds, timeouts, fallback confidence.
- `src/apex/core/exceptions.py` — `ApexError`, `LLMBudgetExceededError`, `DataFetchError`, `AgentError`, `ConfigError`.
- `src/apex/domain/__init__.py` — public domain exports.
- `src/apex/domain/models/__init__.py` — model exports.

## Decisions Made

- Kept domain Pydantic models separate from SQLAlchemy ORM models to avoid persistence concerns leaking into API/agent DTOs.
- Used `StrEnum` for `Signal` after Ruff flagged `str, Enum` inheritance.
- Used `Field(default_factory=list)` for watchlist items to avoid mutable defaults.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Adjusted quality issues found during verification**
- **Found during:** post-plan quality gate.
- **Issue:** Ruff flagged `Signal(str, Enum)` and mutable/formatting issues.
- **Fix:** Switched to `StrEnum`, applied field validation/default factory and formatting fixes.
- **Files modified:** `src/apex/domain/value_objects.py`, `src/apex/domain/models/watchlist.py`, `src/apex/domain/models/prediction_band.py`.
- **Verification:** Ruff, mypy, touched-file format check, unit suite, and API smoke all pass.
- **Committed in:** `2200e5c`

---

**Total deviations:** 1 auto-fixed blocking quality issue.  
**Impact on plan:** No scope expansion; changes keep the planned domain surface inside project quality gates.

## Issues Encountered

- `uv` needed cache access outside the sandbox; verification commands were rerun with escalation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 6 agents can import `Signal`, `Indicator`, `AnalysisResult`, constants, and custom exceptions from stable package paths.

---
*Phase: 05-domain-models-core-services*
*Completed: 2026-04-29*
