---
phase: 07-workflow-assembly-resilience
plan: 03
subsystem: workflow-api-tests
tags: [fastapi, pytest, fakellm, workflow-tests]
requires:
  - phase: 07-workflow-assembly-resilience
    provides: workflow factory and resilience primitives
provides:
  - Workflow-backed analysis endpoint
  - FakeLLMClient full-pipeline test
  - Circuit breaker transition tests
  - Rule-based fallback tests
affects: [phase-08-streamlit-frontend, api-analysis]
tech-stack:
  added: []
  patterns: [ASGITransport endpoint smoke, monkeypatched workflow/LLM tests]
key-files:
  created:
    - tests/unit/test_workflow.py
    - tests/unit/test_circuit_breaker.py
    - tests/unit/test_fallback.py
  modified:
    - src/apex/api/routes/analysis.py
key-decisions:
  - "Keep the endpoint response model as AnalysisResult and place usage/agent details in summary."
  - "Use deterministic synthetic OHLCV bars for API smoke workflow input."
patterns-established:
  - "Endpoint tests monkeypatch create_workflow to avoid external LLM or market data calls."
requirements-completed: [TEST-03]
duration: 30 min
completed: 2026-05-01
---

# Phase 7 Plan 03: Workflow Tests and Endpoint Summary

**Real workflow-backed `/analyze` route plus deterministic unit coverage for workflow, fallback, and circuit transitions**

## Performance

- **Duration:** 30 min
- **Started:** 2026-05-01
- **Completed:** 2026-05-01
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Updated `POST /api/v1/analyze/{ticker}` to invoke `create_workflow()`.
- Added workflow run config with `project=apex` metadata.
- Preserved `AnalysisResult` as the API response contract.
- Added `usage_summary`, `agent_outputs`, and `errors` under response `summary`.
- Added deterministic synthetic OHLCV bars for endpoint smoke execution.
- Added FakeLLMClient full-pipeline workflow unit test.
- Added API route smoke test verifying `signal`, `confidence`, and `usage_summary`.
- Added circuit breaker and fallback unit tests.

## Task Commits

1. **Task 1: Workflow unit tests** — `f6b792b`
2. **Task 2: Analysis endpoint wiring** — `f6b792b`
3. **Workflow guard test coverage** — `6eea858`

## Files Created/Modified

- `tests/unit/test_workflow.py` — full workflow and endpoint tests.
- `tests/unit/test_circuit_breaker.py` — circuit state transition tests.
- `tests/unit/test_fallback.py` — RSI fallback tests.
- `src/apex/api/routes/analysis.py` — workflow-backed API route.

## Decisions Made

- Endpoint remains analysis-only; rejected tickers return a deterministic rejected `AnalysisResult`.
- Synthetic local OHLCV bars keep endpoint tests independent of Alpaca/yfinance credentials.
- Usage and agent detail fields live inside `summary` instead of changing the response model.

## Deviations from Plan

### API response shape preserved

- **Plan text:** mentions `usage_summary` and agent outputs as top-level response concepts.
- **Implementation:** keeps `AnalysisResult` response model and nests them under `summary`.
- **Reason:** Avoids broad API contract churn while still exposing required information.

## Issues Encountered

- Test monkeypatch initially imported `portfolio_manager` from package exports as a function, not module; fixed by using `importlib.import_module()`.

## User Setup Required

None for unit tests. Live endpoint calls still require normal app runtime configuration.

## Next Phase Readiness

Streamlit can consume `/api/v1/analyze/{ticker}` and display signal, confidence, usage summary, agent outputs, and degraded/rejected states.

---
*Phase: 07-workflow-assembly-resilience*
*Completed: 2026-05-01*
