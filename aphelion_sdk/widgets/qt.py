"""Optional PyQt6 helpers for advanced plugin widgets.

The SDK does not depend on PyQt6. These helpers import it only when
the editor (or a plugin) has it installed.
"""

from __future__ import annotations

from typing import Any, TypeAlias

QtWidget: TypeAlias = Any


def is_qt_widget(value: object) -> bool:
    """Return whether ``value`` is a ``PyQt6.QtWidgets.QWidget``."""
    widget_type = _qwidget_type()
    if widget_type is None:
        return False
    return isinstance(value, widget_type)


def coerce_qt_parent(parent: object) -> QtWidget | None:
    """Return ``parent`` when it is a QWidget, otherwise ``None``."""
    if is_qt_widget(parent):
        return parent
    return None


def _qwidget_type() -> type[Any] | None:
    """Import ``QWidget`` when PyQt6 is available."""
    try:
        from PyQt6.QtWidgets import QWidget
    except ImportError:
        return None
    return QWidget
