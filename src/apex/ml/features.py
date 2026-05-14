"""Feature engineering for quant ML inference.

Must produce feature vectors in the EXACT same order and calculation
as the training pipeline (Snakefile_train / scripts/train_models.sh).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import numpy as np

# Must match the training pipeline's feature column order exactly.
# Sync this list with Snakefile_train and scripts/train_models.sh.
FEATURE_COLUMNS: list[str] = [
    "return_1d",
    "return_5d",
    "return_21d",
    "volatility_5d",
    "volatility_21d",
    "close_high_ratio",
    "close_low_ratio",
    "high_low_ratio",
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_histogram",
    "bollinger_pctb",
    "sma20_ratio",
    "sma50_ratio",
    "volume_ratio",
    "volume_price_trend",
    "rolling_min_5d",
    "rolling_max_5d",
    "rolling_mean_5d",
    "rolling_min_21d",
    "rolling_max_21d",
    "rolling_mean_21d",
]

N_FEATURES = len(FEATURE_COLUMNS)


def _to_float(value: Any) -> float:
    """Safely convert Decimal / int / float / str to float."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, str):
        return float(value)
    return float(value)


def compute_features(bars: list[Any]) -> np.ndarray:
    """Compute feature vector for each bar from an OHLCV bar list.

    Args:
        bars: List of OHLCV-like objects with .open, .high, .low, .close, .volume.

    Returns:
        (n_bars, N_FEATURES) numpy array. Early rows (before lookback windows
        are populated) will contain zeros — the caller should truncate or use
        the most recent row only.
    """
    n = len(bars)
    if n == 0:
        return np.zeros((0, N_FEATURES), dtype=np.float64)

    close = np.array([_to_float(b.close) for b in bars], dtype=np.float64)
    high = np.array([_to_float(b.high) for b in bars], dtype=np.float64)
    low = np.array([_to_float(b.low) for b in bars], dtype=np.float64)
    vol = np.array([_to_float(b.volume) for b in bars], dtype=np.float64)

    features = np.zeros((n, N_FEATURES), dtype=np.float64)

    for i in range(n):
        col = 0

        # Returns
        features[i, col] = float(close[i] / close[i - 1] - 1) if i >= 1 else 0.0
        col += 1
        features[i, col] = float(close[i] / close[i - 5] - 1) if i >= 5 else 0.0
        col += 1
        features[i, col] = float(close[i] / close[i - 21] - 1) if i >= 21 else 0.0
        col += 1

        # Volatility
        features[i, col] = float(np.std(close[max(0, i - 4) : i + 1]))
        col += 1
        features[i, col] = float(np.std(close[max(0, i - 20) : i + 1]))
        col += 1

        # Price ratios
        features[i, col] = float(close[i] / high[i]) if high[i] else 0.0
        col += 1
        features[i, col] = float(close[i] / low[i]) if low[i] else 0.0
        col += 1
        features[i, col] = float(high[i] / low[i]) if low[i] else 0.0
        col += 1

        # RSI(14)
        if i >= 14:
            gains, losses = [], []
            for j in range(i - 13, i + 1):
                ch = close[j] - close[j - 1]
                gains.append(max(ch, 0))
                losses.append(max(-ch, 0))
            avg_gain = float(np.mean(gains))
            avg_loss = float(np.mean(losses))
            rs = avg_gain / avg_loss if avg_loss > 0 else 100.0
            features[i, col] = float(100 - 100 / (1 + rs))
        else:
            features[i, col] = 50.0
        col += 1

        # MACD(12,26,9)
        if i >= 26:
            macd_val, macd_sig, _ = _compute_macd(close[: i + 1])
            features[i, col] = macd_val
            col += 1
            features[i, col] = macd_sig
            col += 1
            features[i, col] = macd_val - macd_sig
            col += 1
        else:
            features[i, col] = 0.0
            col += 1
            features[i, col] = 0.0
            col += 1
            features[i, col] = 0.0
            col += 1

        # Bollinger %b(20,2)
        if i >= 20:
            window = close[i - 19 : i + 1]
            sma20 = float(np.mean(window))
            std20 = float(np.std(window))
            upper = sma20 + 2 * std20
            lower = sma20 - 2 * std20
            pct_b = (close[i] - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
            features[i, col] = pct_b
        else:
            features[i, col] = 0.5
        col += 1

        # SMA20 ratio
        if i >= 20:
            sma20 = float(np.mean(close[i - 19 : i + 1]))
            features[i, col] = float(close[i] / sma20 - 1 if sma20 else 0.0)
        else:
            features[i, col] = 0.0
        col += 1

        # SMA50 ratio
        if i >= 50:
            sma50 = float(np.mean(close[i - 49 : i + 1]))
            features[i, col] = float(close[i] / sma50 - 1 if sma50 else 0.0)
        else:
            features[i, col] = 0.0
        col += 1

        # Volume ratio (vs 21d avg)
        if i >= 21:
            avg_vol = float(np.mean(vol[i - 20 : i + 1]))
            features[i, col] = float(vol[i] / avg_vol) if avg_vol else 1.0
        else:
            features[i, col] = 1.0
        col += 1

        # Volume price trend
        if i >= 1:
            delta = close[i] - close[i - 1]
            features[i, col] = float(vol[i] * delta / close[i - 1]) if close[i - 1] else 0.0
        else:
            features[i, col] = 0.0
        col += 1

        # Rolling stats 5d
        features[i, col] = float(np.min(close[max(0, i - 4) : i + 1]))
        col += 1
        features[i, col] = float(np.max(close[max(0, i - 4) : i + 1]))
        col += 1
        features[i, col] = float(np.mean(close[max(0, i - 4) : i + 1]))
        col += 1

        # Rolling stats 21d
        features[i, col] = float(np.min(close[max(0, i - 20) : i + 1]))
        col += 1
        features[i, col] = float(np.max(close[max(0, i - 20) : i + 1]))
        col += 1
        features[i, col] = float(np.mean(close[max(0, i - 20) : i + 1]))

    return features


def _ema(data: np.ndarray, span: int) -> np.ndarray:
    """Exponential moving average (forward pass, no pandas)."""
    k = 2.0 / (span + 1)
    result = np.zeros_like(data)
    result[0] = float(data[0])
    for i in range(1, len(data)):
        result[i] = float(data[i]) * k + result[i - 1] * (1 - k)
    return result


def _compute_macd(prices: np.ndarray) -> tuple[float, float, float]:
    """Return (macd, signal, histogram) for the latest value."""
    ema12 = _ema(prices, 12)
    ema26 = _ema(prices, 26)
    macd_series = ema12 - ema26
    signal_series = _ema(macd_series, 9)
    latest_macd = float(macd_series[-1])
    latest_signal = float(signal_series[-1])
    return latest_macd, latest_signal, latest_macd - latest_signal
