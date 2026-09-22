"""UI surface attached to a plugin. Never registered with ``@register_plugin``."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from aphelion_sdk.widgets.host import WidgetHost, WidgetView
from aphelion_sdk.widgets.kinds import WIDGET_KIND_PANEL


class PluginWidget(ABC):
    """Host-rendered UI owned by a ``Plugin`` subclass.

    Declare widgets on the plugin via ``widgets = (MyDialog, MyPanel)``.
    The editor discovers them when it registers the parent plugin. Authors
    must not decorate a ``PluginWidget`` with ``@register_plugin``.

    Simple widgets implement ``build_view`` with host primitives. Advanced
    widgets may import PyQt6 and return a ``QWidget`` from
    ``build_qt_widget``, or ``embed_native`` one inside ``build_view``.
    Do not import editor packages (``ui``, ``core``, ``effects``, ``render``).

    Attributes:
        widget_id: Stable id used by ``custom_property(widget_id=...)``
            and ``host.open_dialog(...)``. Defaults to the class name.
        widget_title: Dock or window title. Defaults to ``widget_id``.
        widget_kind: ``panel`` or ``dialog``.
        widget_description: Optional tooltip / help text.
    """

    widget_id: ClassVar[str] = ""
    widget_title: ClassVar[str] = ""
    widget_kind: ClassVar[str] = WIDGET_KIND_PANEL
    widget_description: ClassVar[str] = ""

    @classmethod
    def resolved_id(cls) -> str:
        """Return ``widget_id``, or the class name when it is empty."""
        identifier: str = cls.widget_id.strip()
        if identifier:
            return identifier
        return cls.__name__

    @classmethod
    def resolved_title(cls) -> str:
        """Return ``widget_title``, or the resolved id when it is empty."""
        title: str = cls.widget_title.strip()
        if title:
            return title
        return cls.resolved_id()

    def build_qt_widget(self, parent: object, host: WidgetHost) -> object | None:
        """Advanced: return a PyQt6 ``QWidget`` as the entire surface.

        Parameters:
            parent: Host ``QWidget`` that should own the result.
            host: Bound plugin/node bridge (properties, dialogs).

        Returns:
            A ``QWidget``, or ``None`` to fall back to ``build_view``.
        """
        del parent, host
        return None

    def build_view(self, host: WidgetHost) -> WidgetView:
        """Create and return this widget's contents.

        Parameters:
            host: Editor-provided factory bound to the parent plugin/node.

        Returns:
            The view produced by ``host.create_view()`` after adding controls.
            Default is an empty view, used when ``build_qt_widget`` is set.
        """
        return host.create_view()

    def on_dispose(self, host: WidgetHost) -> None:
        """Release timers/subscriptions when this UI surface is destroyed."""
