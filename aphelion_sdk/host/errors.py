"""Errors raised while locating the editor or installing drop-in plugins."""

from __future__ import annotations


class EditorHostError(RuntimeError):
    """Raised when the SDK cannot find or write into Aphelion Editor.

    Parameters:
        message: Human-readable explanation of what failed.

    Returns:
        None.

    Exceptions:
        None.

    Side effects:
        None.
    """
