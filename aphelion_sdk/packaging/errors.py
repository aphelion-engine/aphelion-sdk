"""Errors raised while turning plugins into pip distributions."""

from __future__ import annotations


class PluginPackageError(Exception):
    """Raised when a plugin cannot be packaged as a pip distribution.

    Parameters:
        message: Human-readable explanation of what failed.

    Returns:
        None.

    Exceptions:
        None.

    Side effects:
        None.
    """
