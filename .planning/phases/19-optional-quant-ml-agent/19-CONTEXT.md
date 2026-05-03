# Phase 19: Optional Quant ML Agent + Device Selection — Context

**Gathered:** 2026-05-03
**Status:** Deferred final/advanced Bet 5+ enhancement

<domain>
## Phase Boundary

Add an optional ML-based Quant Agent after the local-first TUI, reports, provider settings, and localization are stable. This phase is intentionally late because it adds training/inference complexity and hardware/device choices.
</domain>

<decisions>
## Implementation Decisions

- Quant Agent is optional, not required for the first Apex cockpit MVP.
- It should produce a structured signal compatible with existing agent outputs.
- It should not call an LLM; it uses engineered OHLCV features and a local ML model.
- Device selection must be explicit and safe:
  - CPU always supported
  - Apple Silicon MPS if available
  - CUDA if available
  - Auto mode may select best available, but must show what was selected
- TUI setup may show Quant Agent/device options only when this phase is implemented.
- Portfolio Manager should treat Quant Agent as an additional input, not a replacement for existing Technical/Fundamental/Risk agents.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/agents/workflow.py` — workflow node wiring
- `src/apex/agents/state.py` — AgentState extension point
- `src/apex/agents/technical.py` and `src/apex/agents/indicators.py` — feature reuse
- `src/apex/ingestion/market_data_fetcher.py` — OHLCV input source
- `src/apex/tui/` — setup panel/device selection after implementation
</canonical_refs>

<deferred>
## Deferred Ideas

- MLflow/model registry
- Deep learning models
- GPU benchmarking UI
- Training notebook polish
</deferred>

---
*Phase: 19-optional-quant-ml-agent*
