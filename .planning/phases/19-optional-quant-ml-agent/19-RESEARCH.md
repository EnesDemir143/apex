# Phase 19: Optional Quant ML Agent + Device Selection — Research

## Why This Is Late

ML integration is CV-useful but can easily dominate scope. The local-first TUI must first prove the product experience. Quant Agent comes after that as an advanced optional signal.

## Recommended MVP

Start with a simple, explainable model:

- feature engineering from OHLCV:
  - RSI
  - MACD
  - Bollinger position
  - short/medium returns
  - volatility
  - volume ratio
- model:
  - lightweight sklearn/XGBoost-style classifier if dependency accepted later
  - or a simple rule/logistic baseline first
- output:
  - signal
  - confidence/probability
  - top features / explanation
  - model version
  - device used

## Device Selection

Expose:

```text
ML device: auto / cpu / mps / cuda
```

Rules:
- CPU must always work.
- MPS only if PyTorch with Apple MPS support is installed and available.
- CUDA only if CUDA runtime and compatible package are available.
- If requested accelerator is unavailable, fail clearly or fall back only with explicit warning.

## TUI Integration

Add to setup panel:

- Quant Agent: enabled/disabled
- ML model: baseline / latest
- Device: auto/cpu/mps/cuda

Add to footer/report metadata:

- model version
- device used
- inference latency
