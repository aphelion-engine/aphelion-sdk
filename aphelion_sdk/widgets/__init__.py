"""Widgets attached to plugins: panels, dialogs, and the host protocols."""

from __future__ import annotations

from aphelion_sdk.widgets.base import PluginWidget
from aphelion_sdk.widgets.dialog import DialogWidget
from aphelion_sdk.widgets.host import WidgetContext, WidgetHost, WidgetView
from aphelion_sdk.widgets.kinds import WIDGET_KIND_DIALOG, WIDGET_KIND_PANEL
from aphelion_sdk.widgets.panel import PanelWidget
from aphelion_sdk.widgets.qt import coerce_qt_parent, is_qt_widget

__all__ = [
    "WIDGET_KIND_DIALOG",
    "WIDGET_KIND_PANEL",
    "DialogWidget",
    "PanelWidget",
    "PluginWidget",
    "WidgetContext",
    "WidgetHost",
    "WidgetView",
    "coerce_qt_parent",
    "is_qt_widget",
]
