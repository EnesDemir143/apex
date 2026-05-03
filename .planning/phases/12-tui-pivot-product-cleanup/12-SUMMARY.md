# Phase 12 Summary: TUI Pivot Product Cleanup

**Completed:** 2026-05-03
**Branch:** feat/tui-pivot-product-cleanup → main
**Requirements:** TUI-01, DOC-01

## What Was Done

1. **README** — confirmed TUI-first product story: local-first cockpit as primary path, web/API/Streamlit/K8s as optional/legacy extension, pivot note, web revival guide link.

2. **REQUIREMENTS.md** — added traceability rows for TUI-01–11, DOC-01–02, ML-01–03, FE-02 with phase assignments (Phases 12–19, Planned).

3. **Consistency verified** — BET5_POSTPROD_PLAN.md and ROADMAP.md agree: all web-rewrite/monetization items are explicitly out-of-scope; no active web-rewrite work remains.

4. **make check** — ruff ✅, mypy ✅ (95 files), 29 unit tests ✅. E2E errors are pre-existing Docker-not-running failures unrelated to this phase.

## Files Modified

- `README.md`
- `.planning/REQUIREMENTS.md`

## Success Criteria Check

| Criterion | Status |
|-----------|--------|
| README first screen = local-first TUI cockpit | ✅ |
| Old web production frontend rewrite not an active roadmap item | ✅ |
| Streamlit/FastAPI/Postgres/K8s documented as optional/legacy | ✅ |
| .planning and BET5_POSTPROD_PLAN.md agree on TUI pivot | ✅ |
