"""Optional Quant ML package — feature engineering, device resolution, model registry.

Training pipeline lives in Snakefile_train / scripts/train_models.sh.
Inference-time modules are here.
"""

from apex.ml.features import compute_features, FEATURE_COLUMNS
from apex.ml.device import DeviceResolver, resolve_device
from apex.ml.model_registry import ModelRegistry, QuantPrediction

__all__ = [
    "compute_features",
    "DeviceResolver",
    "FEATURE_COLUMNS",
    "ModelRegistry",
    "QuantPrediction",
    "resolve_device",
]
