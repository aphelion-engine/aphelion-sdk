"""Shared type aliases exposed to plugin authors.

These aliases describe the shapes plugins exchange with the host
application without requiring plugin authors to import anything from
``core``.
"""

from __future__ import annotations

from typing import TypeAlias

import numpy as np

# RGB color property: ``(r, g, b)`` with each channel in ``0-255``.
ColorRgb: TypeAlias = tuple[int, int, int]

# A video plugin frame buffer: shape ``(height, width, 3)``, dtype ``float32``,
# nominal value range ``[0.0, 1.0]``. Alpha is not carried on this buffer.
Frame: TypeAlias = np.ndarray
