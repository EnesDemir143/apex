"""ML device resolver — auto / cpu / mps / cuda.

For tree-based ensemble models the device selection is primarily cosmetic
(they run on CPU regardless), but this module provides a generic resolver API
that can be extended for future PyTorch deep learning support.
"""

from __future__ import annotations

import platform
from typing import Literal

DeviceType = Literal["auto", "cpu", "mps", "cuda"]


class DeviceResolver:
    """Resolve and cache the best available compute device."""

    def __init__(self, preference: DeviceType = "auto") -> None:
        self._device = self._resolve(preference)

    @staticmethod
    def _resolve(preference: DeviceType) -> str:
        if preference == "cpu":
            return "cpu"
        if preference == "cuda":
            try:
                # Lazy import so core installs without torch don't fail
                import torch  # type: ignore[import-untyped]

                if torch.cuda.is_available():
                    return "cuda"
            except ImportError:
                pass
            return "cpu"
        if preference == "mps":
            if platform.system() == "Darwin":
                try:
                    import torch  # type: ignore[import-untyped]

                    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                        return "mps"
                except ImportError:
                    pass
            return "cpu"
        # auto: try cuda -> mps -> cpu
        try:
            import torch  # type: ignore[import-untyped]

            if torch.cuda.is_available():
                return "cuda"
            if platform.system() == "Darwin" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    @property
    def device(self) -> str:
        return self._device

    def device_display(self) -> str:
        """Human-readable device label."""
        labels = {"cpu": "CPU", "mps": "MPS (Apple Silicon)", "cuda": "CUDA (GPU)"}
        return labels.get(self._device, self._device)


def resolve_device(preference: DeviceType = "auto") -> str:
    """One-shot device resolution without creating a DeviceResolver instance."""
    return DeviceResolver(preference).device
