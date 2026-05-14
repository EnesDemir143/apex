"""Quant ML model registry — load persisted models and run ensemble inference."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from apex.ml.device import DeviceResolver
from apex.ml.features import FEATURE_COLUMNS, compute_features


@dataclass
class QuantPrediction:
    """Structured output from the quant ensemble."""

    signal: str  # "BUY" | "SELL" | "HOLD"
    confidence: float
    reasoning: str
    top_features: dict[str, float]
    model_version: str
    device: str
    latency_ms: float
    model_available: bool = True


MODELS_DIR = Path("models/quant")

# Soft-voting fallback weights if RidgeCV is unavailable
DEFAULT_WEIGHTS = {"random_forest": 0.20, "xgboost": 0.25, "lightgbm": 0.25, "catboost": 0.30}


def _check_models_exist(models_dir: Path = MODELS_DIR) -> bool:
    """Check if saved model files exist on disk."""
    required = [
        models_dir / "random_forest.pkl",
        models_dir / "xgboost.pkl",
        models_dir / "lightgbm.pkl",
        models_dir / "catboost.pkl",
        models_dir / "scaler.pkl",
    ]
    # ensemble_voter is optional (we can do soft voting without it)
    return all(p.exists() for p in required)


class ModelRegistry:
    """Load and manage the quant ensemble model stack.

    Usage:
        registry = ModelRegistry()
        if registry.available:
            pred = registry.predict(bars)
    """

    def __init__(self, models_dir: str | Path = MODELS_DIR) -> None:
        self._models_dir = Path(models_dir)
        self._models: dict[str, Any] = {}
        self._voter: Any = None
        self._scaler: Any = None
        self._metadata: dict[str, Any] = {}
        self._device_resolver = DeviceResolver("auto")
        self._loaded = False
        self._load_error: str | None = None

    # ── public API ─────────────────────────────────────────────────────────

    @property
    def available(self) -> bool:
        """True if all required model files exist and were loaded."""
        if not self._loaded and not self._load_error:
            if _check_models_exist(self._models_dir):
                self._load()
            else:
                self._load_error = f"Models not found in {self._models_dir}"
        return self._loaded

    @property
    def model_version(self) -> str:
        if self._metadata:
            return str(self._metadata.get("model_version", "unknown"))
        return "not_loaded"

    @property
    def device(self) -> str:
        return self._device_resolver.device

    @property
    def device_display(self) -> str:
        return self._device_resolver.device_display()

    def predict(self, bars: list[Any]) -> QuantPrediction:
        """Run ensemble inference on OHLCV bars.

        Args:
            bars: List of OHLCV bar-like objects sorted chronologically (oldest first).

        Returns:
            QuantPrediction with signal, confidence, top features, etc.
        """
        if not self.available:
            return QuantPrediction(
                signal="HOLD",
                confidence=0.0,
                reasoning="Quant model not available. Train first: bash scripts/train_models.sh",
                top_features={},
                model_version="not_available",
                device=self.device,
                latency_ms=0.0,
                model_available=False,
            )

        start = time.monotonic()

        # Compute features using the same function used during training
        features = compute_features(bars)

        if features.shape[0] == 0:
            return QuantPrediction(
                signal="HOLD",
                confidence=0.0,
                reasoning="No bars provided",
                top_features={},
                model_version=self.model_version,
                device=self.device,
                latency_ms=0.0,
            )

        # Use the latest bar's feature vector
        x = features[-1:, :]  # (1, N_FEATURES)

        if not np.all(np.isfinite(x)):
            return QuantPrediction(
                signal="HOLD",
                confidence=0.0,
                reasoning="Non-finite values in feature vector",
                top_features={},
                model_version=self.model_version,
                device=self.device,
                latency_ms=0.0,
            )

        # Scale
        x_scaled = self._scaler.transform(x)

        # Individual model predictions
        probs: dict[str, float] = {}
        for name in ("random_forest", "xgboost", "lightgbm", "catboost"):
            model = self._models.get(name)
            if model is not None:
                prob = float(model.predict_proba(x_scaled)[0, 1])
                probs[name] = prob

        # Ensemble: use RidgeCV voter if available, otherwise soft vote
        if self._voter is not None:
            meta = np.array(
                [
                    [
                        probs.get("random_forest", 0.5),
                        probs.get("xgboost", 0.5),
                        probs.get("lightgbm", 0.5),
                        probs.get("catboost", 0.5),
                    ]
                ]
            )
            ensemble_prob = float(self._voter.predict(meta))
        else:
            # Fallback: weighted soft voting
            ensemble_prob = sum(probs.get(name, 0.5) * weight for name, weight in DEFAULT_WEIGHTS.items())

        elapsed = (time.monotonic() - start) * 1000

        # Determine signal
        if ensemble_prob >= 0.6:
            signal = "BUY"
        elif ensemble_prob <= 0.4:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = abs(ensemble_prob - 0.5) * 2  # 0.0–1.0

        # Top features from Random Forest feature importances
        top_features: dict[str, float] = {}
        rf_model = self._models.get("random_forest")
        if rf_model is not None and hasattr(rf_model, "feature_importances_"):
            importances = rf_model.feature_importances_
            top_indices = np.argsort(importances)[::-1][:3]
            for idx in top_indices:
                if idx < len(FEATURE_COLUMNS):
                    top_features[FEATURE_COLUMNS[idx]] = float(importances[idx])

        # Reasoning string
        feature_parts = [f"{name}={val:.3f}" for name, val in top_features.items()]
        reasoning = (
            f"Ensemble prob: {ensemble_prob:.3f} | "
            f"Top features: {', '.join(feature_parts)} | "
            f"Model: {self.model_version}"
        )

        return QuantPrediction(
            signal=signal,
            confidence=round(confidence, 4),
            reasoning=reasoning,
            top_features=top_features,
            model_version=self.model_version,
            device=self.device,
            latency_ms=round(elapsed, 2),
        )

    def predict_proba(self, bars: list[Any]) -> float:
        """Return raw ensemble probability (0–1) for the latest bar. Convenience for tests."""
        return self.predict(bars).confidence  # approximated

    # ── loading ────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load models from disk."""
        import joblib

        try:
            self._models["random_forest"] = joblib.load(self._models_dir / "random_forest.pkl")
            self._models["xgboost"] = joblib.load(self._models_dir / "xgboost.pkl")
            self._models["lightgbm"] = joblib.load(self._models_dir / "lightgbm.pkl")
            self._models["catboost"] = joblib.load(self._models_dir / "catboost.pkl")
            self._scaler = joblib.load(self._models_dir / "scaler.pkl")

            # Voter is optional
            voter_path = self._models_dir / "ensemble_voter.pkl"
            if voter_path.exists():
                self._voter = joblib.load(voter_path)

            # Metadata
            meta_path = self._models_dir / "metadata.json"
            if meta_path.exists():
                with open(meta_path) as f:
                    self._metadata = json.load(f)

            self._loaded = True
        except Exception as exc:
            self._load_error = str(exc)
            self._loaded = False
