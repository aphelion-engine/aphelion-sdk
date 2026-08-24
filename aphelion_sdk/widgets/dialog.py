"""Popup dialog widget attached to a parent plugin."""

from __future__ import annotations

from typing import ClassVar

from aphelion_sdk.widgets.base import PluginWidget
from aphelion_sdk.widgets.host import WidgetHost, WidgetView
from aphelion_sdk.widgets.kinds import (
    DEFAULT_DIALOG_HEIGHT_PX,
    DEFAULT_DIALOG_WIDTH_PX,
    WIDGET_KIND_DIALOG,
)


class DialogWidget(PluginWidget):
    """Popup window owned by a plugin.

    Opened from a custom property row, ``host.open_dialog(widget_id)``,
    or Window → Plugin Windows when ``widget_show_in_menu`` is True.
    The host owns title bar and OK/Close chrome. Advanced dialogs may
    return a PyQt6 ``QWidget`` from ``build_qt_widget`` and read it in
    ``on_accept``.

    Attributes:
        widget_kind: Always ``dialog``.
        widget_modal: When True, the popup blocks the editor.
        widget_width: Initial width in pixels.
        widget_height: Initial height in pixels.
        widget_show_in_menu: When True, listed under Plugin Windows.
    """

    widget_kind: ClassVar[str] = WIDGET_KIND_DIALOG
    widget_modal: ClassVar[bool] = True
    widget_width: ClassVar[int] = DEFAULT_DIALOG_WIDTH_PX
    widget_height: ClassVar[int] = DEFAULT_DIALOG_HEIGHT_PX
    widget_show_in_menu: ClassVar[bool] = True

    def on_accept(self, view: WidgetView, host: WidgetHost) -> None:
        """Called when the user confirms a modal dialog. Default is no-op."""
        del view, host

    def on_reject(self, view: WidgetView, host: WidgetHost) -> None:
        """Called when the user cancels or closes. Default is no-op."""
        del view, host
