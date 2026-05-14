"""Tests for quant ML feature extraction.

Verifies that compute_features:
1. Produces N_FEATURES columns in the correct order
2. Returns sensible values for known bar sequences
3. Returns zeros for empty input
"""

from __future__ import annotations

import numpy as np
import pytest

from apex.ml.features import FEATURE_COLUMNS, N_FEATURES, compute_features


@pytest.fixture
def sample_bars() -> list:
    from datetime import UTC, datetime
    from decimal import Decimal

    from apex.domain.models.ohlcv import OHLCVBar

    bars: list[OHLCVBar] = []
    base = datetime(2025, 1, 2, tzinfo=UTC)
    for i in range(200):
        bars.append(
            OHLCVBar(
                ticker="AAPL",
                timestamp=base,
                open=Decimal("150"),
                high=Decimal("155"),
                low=Decimal("145"),
                close=Decimal("152") + Decimal(i * 0.5),
                volume=1_000_000,
                source="test",
            )
        )
    return bars


class TestComputeFeatures:
    def test_feature_count_matches_columns(self):
        """N_FEATURES must equal len(FEATURE_COLUMNS)."""
        assert N_FEATURES == len(FEATURE_COLUMNS) == 23

    def test_empty_bars_returns_empty(self):
        result = compute_features([])
        assert result.shape == (0, N_FEATURES)

    def test_output_shape(self, sample_bars):
        """Returns (n_bars, N_FEATURES) for any input length."""
        for n in (1, 10, 50, 200):
            features = compute_features(sample_bars[:n])
            assert features.shape == (n, N_FEATURES), f"Failed for n={n}"
            assert features.dtype == np.float64

    def test_latest_bar_has_all_features(self, sample_bars):
        """The last bar (which has full lookback) should have non-zero features."""
        features = compute_features(sample_bars)
        latest = features[-1, :]
        # Most features should be non-zero after full lookback
        nonzero = sum(1 for v in latest if abs(v) > 1e-10)
        assert nonzero >= 18, f"Only {nonzero}/22 features non-zero for latest bar"

    def test_return_1d_computation(self, sample_bars):
        """return_1d feature should capture daily price change."""
        features = compute_features(sample_bars)
        # Bar 0: return_1d = 0 (no previous bar)
        assert abs(features[0, 0]) < 1e-10
        # Bar 1: return_1d = (152.5 - 152) / 152 ≈ 0.0033
        expected = (152.5 - 152.0) / 152.0
        assert abs(features[1, 0] - expected) < 0.001

    def test_feature_names_are_str(self):
        """All feature column names must be strings (not None/empty)."""
        for name in FEATURE_COLUMNS:
            assert isinstance(name, str) and name

    def test_feature_order_is_deterministic(self):
        """FEATURE_COLUMNS order must not change between calls."""
        assert FEATURE_COLUMNS == [
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



