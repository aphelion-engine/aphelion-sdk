"""Dockable panel widget attached to a parent plugin."""

from __future__ import annotations

from typing import ClassVar

from aphelion_sdk.widgets.base import PluginWidget
from aphelion_sdk.widgets.host import WidgetView
from aphelion_sdk.widgets.kinds import DEFAULT_DOCK_AREA, WIDGET_KIND_PANEL, DockAreaName


class PanelWidget(PluginWidget):
    """Extra editor dock owned by a plugin.

    Shown under Window → Panels while the parent plugin is enabled.
    Authors never create ``QDockWidget`` instances. They may return a
    PyQt6 ``QWidget`` body from ``build_qt_widget``.

    Attributes:
        widget_kind: Always ``panel``.
        widget_default_visible: When True, the dock is shown at editor open.
        widget_dock_area: Hint for initial placement.
    """

    widget_kind: ClassVar[str] = WIDGET_KIND_PANEL
    widget_default_visible: ClassVar[bool] = False
    widget_dock_area: ClassVar[DockAreaName] = DEFAULT_DOCK_AREA

    def on_show(self, view: WidgetView) -> None:
        """Called when the dock becomes visible. Default is no-op."""
        del view

    def shutdown(self) -> None:
        """Release resources when the editor unmounts the panel."""
        return
