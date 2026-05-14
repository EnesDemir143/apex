# Phase 19: Optional Quant ML Agent + Device Selection — Context

**Gathered:** 2026-05-15
**Status:** Planned — final Bet 5+ enhancement

<domain>
## Phase Boundary

Add an optional 4-model ensemble Quant ML Agent (Random Forest + XGBoost + LightGBM + CatBoost) with Snakemake training pipeline, joblib model persistence, and TUI integration. This is the final phase of the v1.0 milestone.
</domain>

<decisions>
## Implementation Decisions

- Quant Agent is optional (opt-in via TUI toggle), not required for Apex cockpit MVP.
- 4-model soft voting ensemble: RF=0.20, XGB=0.25, LGBM=0.25, Cat=0.30.
- Training pipeline via Snakefile_train (or bash script without snakemake).
- Models persisted with joblib to models/quant/ — no retraining at inference.
- Features must match exactly between training and inference.
- ML dependencies are optional (`uv sync --group quant`), core stays lean.
- CPU is the primary device; device selection API kept for future deep learning use.
- Portfolio Manager treats Quant as additional input, not replacement.
- TUI setup shows Quant controls only after this phase.
</decisions>

<canonical_refs>
## Canonical References

- `Snakefile_train` — training pipeline
- `scripts/train_models.sh` — one-shot training script
- `src/apex/ml/features.py` — feature extraction (shared train/inference)
- `src/apex/ml/device.py` — device resolution
- `src/apex/ml/model_registry.py` — load models + ensemble predict
- `src/apex/agents/quant.py` — LangGraph agent node
- `src/apex/agents/workflow.py` — workflow node wiring
- `src/apex/agents/state.py` — AgentState extension
- `src/apex/tui/` — setup panel, /quant command, footer metadata
</canonical_refs>

<deferred>
## Deferred Ideas

- Deep learning models (LSTM/CNN with PyTorch)
- GPU benchmarking UI
- MLflow/model registry
- Online learning / model drift detection
- Walk-forward optimization
- Feature store
</deferred>

<dependencies>
## ML Dependencies (optional group)

```toml
[project.optional-dependencies]
quant = [
    "scikit-learn>=1.3",
    "xgboost>=2.0",
    "lightgbm>=4.0",
    "catboost>=1.2",
    "snakemake>=8.0",
]
```
</dependencies>

---
*Phase: 19-optional-quant-ml-agent*
