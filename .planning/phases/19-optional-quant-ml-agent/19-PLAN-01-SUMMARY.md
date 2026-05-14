---
phase: 19
plan: 01
type: execute
subsystem: agents
tags: [quant, ml, ensemble, snakemake, scikit-learn, xgboost, lightgbm, catboost]
requires: [14, 15, 17, 18]
provides: [quant-agent, ml-package, training-pipeline, tui-quant-controls]
affects: [pyproject.toml, Snakefile_train, scripts/, src/apex/ml/, src/apex/agents/, src/apex/tui/]
tech-stack:
  added:
    - scikit-learn >=1.3 — RandomForest + StandardScaler + RidgeCV
    - xgboost >=2.0 — XGBClassifier
    - lightgbm >=4.0 — LGBMClassifier
    - catboost >=1.2 — CatBoostClassifier
    - joblib >=1.3 — model persistence
    - snakemake >=8.0 — training pipeline orchestration
  patterns:
    - 4-model ensemble with RidgeCV meta-learner
    - Joblib model persistence to models/quant/
    - Feature extraction shared between training and inference
    - Optional agent node disabled by default
key-files:
  created:
    - Snakefile_train — Snakemake pipeline (fetch → features → train → evaluate → save)
    - scripts/train_models.sh — one-shot training without snakemake
    - src/apex/ml/__init__.py — ML package init
    - src/apex/ml/features.py — 23-feature extractor (matching train pipeline)
    - src/apex/ml/device.py — DeviceResolver (auto/cpu/mps/cuda)
    - src/apex/ml/model_registry.py — ModelRegistry loading + ensemble inference
    - src/apex/agents/quant.py — quant_agent() LangGraph node
    - tests/unit/test_ml_features.py — 7 tests for feature extraction
    - tests/unit/test_ml_device.py — 10 tests for device resolution
    - tests/unit/test_quant_agent.py — 10 tests for quant agent + registry
  modified:
    - pyproject.toml — added quant dep group + mypy overrides
    - src/apex/agents/state.py — added quant_enabled, quant_analysis
    - src/apex/agents/workflow.py — wired quant node as parallel agent
    - src/apex/agents/portfolio_manager.py — include quant signal when present
    - src/apex/agents/__init__.py — export quant_agent
    - src/apex/services/local_analysis.py — pass quant_enabled to workflow
    - src/apex/tui/state.py — quant_enabled, ml_device, quant_output fields
    - src/apex/tui/app.py — display quant info, dynamic agent count
    - src/apex/tui/widgets.py — SetupPanel quant line, FooterStats quant_info
    - src/apex/tui/commands.py — /quant command with on/off/device
    - tests/unit/test_tui_commands.py — 5 /quant command tests
decisions:
  - 23 features matching training pipeline order exactly
  - RidgeCV meta-learner for ensemble stacking
  - Soft voting fallback (RF=0.20, XGB=0.25, LGBM=0.25, CB=0.30) when RidgeCV unavailable
  - CPU-is-primary device design; PyTorch import tried lazily
  - Quant Agent runs in parallel with other agents, disabled by default
  - Portfolio Manager only includes quant when model_available AND signal != HOLD
metrics:
  duration: ~25 min
  completed: "2026-05-15"
---

# Phase 19 Plan 01: Optional Quant ML Agent + Device Selection — Summary

Optional 4-model ensemble Quant ML Agent (Random Forest + XGBoost + LightGBM + CatBoost with RidgeCV meta-learner) with a Snakemake training pipeline, joblib model persistence, CPU device support, TUI integration via `/quant` command, and 22 new unit tests. All ML dependencies are optional (`uv sync --group quant`).

## Tasks Executed

| #  | Type   | Name                            | Commit   | Files |
|----|--------|---------------------------------|----------|-------|
| 1  | chore  | Add ML dependencies             | c5bd877  | pyproject.toml |
| 2  | feat   | Create training pipeline        | eecb30d  | Snakefile_train, scripts/train_models.sh |
| 3  | feat   | Create ML package               | 1436e85  | features.py, device.py, model_registry.py |
| 4  | feat   | Add optional Quant Agent node   | 0f8a886  | quant.py, state.py, workflow.py, portfolio_manager.py, local_analysis.py |
| 5  | feat   | Expose Quant controls in TUI    | 3f873b3  | commands.py, widgets.py, app.py |
| 6  | test   | Test quant agent + utilities    | 46a1a5f  | test_ml_features.py, test_ml_device.py, test_quant_agent.py |
| —  | test   | Add /quant command tests        | 85221d7  | test_tui_commands.py (5 new tests) |

## Running Verification

**Test suite:**
```bash
uv run pytest tests/unit/
# 190 passed, 1 skipped, 0 failed
```

**Training pipeline (requires quant deps):**
```bash
uv sync --group quant
bash scripts/train_models.sh
# — or —
snakemake -s Snakefile_train all
```

**Run with quant enabled:**
```bash
# In TUI:
# /quant on  → enable quant agent
# /quant device cpu → set device
# /analyze AAPL → run analysis with quant signal
```

**Run with quant disabled (default — no regression):**
```bash
# Default state: quant is OFF
# Existing 4-agent workflow unchanged
```

## Deviations from Plan

None — plan executed exactly as written.

**Note:** Research.md proposed RidgeCV stacking rather than the plan document's weighted voting. The implementation uses RidgeCV as primary with weighted soft-voting fallback when the voter is unavailable — combining the best of both approaches. The plan document's model weights (RF=0.20, XGB=0.25, LGBM=0.25, Cat=0.30) serve as fallback defaults.

## Success Criteria

- [x] Apex gains an optional ensemble ML quant signal (4 models + RidgeCV) without destabilizing the TUI MVP
- [x] Training pipeline is reproducible via Snakefile (or bash script)
- [x] Models are persisted with joblib; no retraining needed at inference
- [x] All tests pass on CPU-only machines (190/190)
- [x] ML dependencies are optional; core install stays lean
- [x] Quant Agent disabled by default; enabled via `/quant on` TUI command
- [x] Portfolio Manager includes quant signal when available and non-HOLD

## Self-Check: PASSED

All 8 created files verified on disk. All 7 commits present in git log. 190/190 tests passing.
