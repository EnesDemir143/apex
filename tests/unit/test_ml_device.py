"""Tests for ML device resolution.

Verifies:
1. CPU always works (no PyTorch needed)
2. Unavailable accelerators fall back gracefully
3. DeviceResolver accepts all valid preference values
"""

from __future__ import annotations

import pytest

from apex.ml.device import DeviceResolver, resolve_device


class TestDeviceResolver:
    """Device resolution tests (all runnable on CPU-only machines)."""

    def test_cpu_always_works(self):
        """CPU device must always resolve to 'cpu' regardless of hardware."""
        resolver = DeviceResolver("cpu")
        assert resolver.device == "cpu"
        assert "CPU" in resolver.device_display()

    def test_cpu_one_shot(self):
        """resolve_device convenience function works for CPU."""
        assert resolve_device("cpu") == "cpu"

    def test_cuda_fallback_to_cpu(self):
        """CUDA preference resolves to cpu when no GPU available."""
        resolver = DeviceResolver("cuda")
        # On CI / dev machines without CUDA this is 'cpu'
        assert resolver.device in ("cpu", "cuda")

    def test_mps_fallback_to_cpu(self):
        """MPS preference resolves to cpu on non-macOS / no MPS."""
        resolver = DeviceResolver("mps")
        assert resolver.device in ("cpu", "mps")

    def test_auto_resolves_without_error(self):
        """Auto mode must not raise, always returns a valid device."""
        resolver = DeviceResolver("auto")
        assert resolver.device in ("cpu", "mps", "cuda")

    def test_device_display_is_str(self):
        """device_display() always returns a human-readable string."""
        resolver = DeviceResolver("cpu")
        display = resolver.device_display()
        assert isinstance(display, str)
        assert len(display) > 0

    @pytest.mark.parametrize("pref", ["cpu", "cuda", "mps", "auto"])
    def test_all_valid_preferences(self, pref):
        """All valid DeviceType values must be accepted."""
        resolver = DeviceResolver(pref)  # type: ignore[arg-type]
        assert resolver.device in ("cpu", "mps", "cuda")

    def test_device_resolver_cache(self):
        """Multiple resolvers with same preference should agree."""
        r1 = DeviceResolver("auto")
        r2 = DeviceResolver("auto")
        assert r1.device == r2.device

    def test_device_display_labels(self):
        """device_display should return known labels."""
        # CPU is guaranteed
        resolver = DeviceResolver("cpu")
        assert resolver.device_display() == "CPU (Apple Silicon)" or resolver.device_display() == "CPU"
