"""Host-owned UI surface protocols. Plugin authors never construct Qt types."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class WidgetContext:
    """Binding from a widget surface back to its parent plugin and node.

    Attributes:
        plugin_key: Parent plugin registry key (``category.name``).
        node_id: Graph node instance, when the surface is inspector-scoped.
        property_key: Property a popup is editing, if any.
        project_name: Display name of the open project.
    """

    plugin_key: str = ""
    node_id: str | None = None
    property_key: str | None = None
    project_name: str = ""


class WidgetView(Protocol):
    """Declarative control tree built through ``WidgetHost.create_view``.

    Most plugins should use the primitive ``add_*`` methods. Advanced
    plugins may ``embed_native`` a PyQt6 ``QWidget`` on the same view.
    """

    def add_label(self, control_id: str, text: str) -> None:
        """Append a static text label."""

    def add_button(
        self,
        control_id: str,
        label: str,
        on_click: Callable[[], None],
    ) -> None:
        """Append a push button that invokes ``on_click`` on the UI thread."""

    def add_text(
        self,
        control_id: str,
        value: str,
        placeholder: str = "",
        on_change: Callable[[str], None] | None = None,
    ) -> None:
        """Append a single-line text field."""

    def add_number(self, control_id: str, label: str, value: float,
                   minimum: float = -1e9, maximum: float = 1e9,
                   on_change: Callable[[float], None] | None = None) -> None:
        """Append a labeled numeric control."""

    def add_toggle(self, control_id: str, label: str, value: bool,
                   on_change: Callable[[bool], None] | None = None) -> None:
        """Append a checkbox."""

    def add_choice(self, control_id: str, label: str, choices: list[str], value: str,
                   on_change: Callable[[str], None] | None = None) -> None:
        """Append a dropdown."""

    def get_value(self, control_id: str) -> object:
        """Read a control. Unknown ids raise KeyError."""

    def set_value(self, control_id: str, value: object) -> None:
        """Update a control without emitting its change callback."""

    def add_separator(self) -> None:
        """Append a horizontal divider."""

    def set_text(self, control_id: str, text: str) -> None:
        """Replace the visible text of a label, button, or text field."""

    def get_text(self, control_id: str) -> str:
        """Return the current text of a label, button, or text field."""

    def embed_native(self, widget: object) -> None:
        """Embed a PyQt6 ``QWidget`` in this view.

        Parameters:
            widget: A ``PyQt6.QtWidgets.QWidget`` instance. Other types
                are rejected by the host.

        Side effects:
            The widget is reparented into the host surface.
        """


class WidgetHost(Protocol):
    """Editor-provided factory and dialog/property bridge.

    ``open_dialog`` resolves ``widget_id`` against the bound parent plugin.
    Advanced plugins may import PyQt6 and parent widgets to ``qt_parent()``.
    Do not import editor packages (``ui``, ``core``, ``effects``, ``render``).
    """

    def create_view(self) -> WidgetView:
        """Return an empty view the widget populates and returns."""

    def context(self) -> WidgetContext:
        """Return the parent plugin / node binding for this surface."""

    def qt_parent(self) -> object:
        """Return the host PyQt6 ``QWidget`` to parent advanced widgets to."""

    def open_dialog(self, widget_id: str) -> bool:
        """Open a ``DialogWidget`` attached to the bound parent plugin.

        Parameters:
            widget_id: The dialog's ``widget_id`` (or class name).

        Returns:
            True when a dialog was shown.
        """

    def get_property_value(self, key: str) -> object | None:
        """Read a property on the bound node. None when unbound or missing."""

    def set_property_value(self, key: str, value: object) -> None:
        """Write a property on the bound node through the editor undo stack."""

    def available_nodes(self) -> tuple[tuple[str, str], ...]:
        """Return (category, name) pairs for all registered node types."""

    def list_nodes(self) -> tuple[str, ...]:
        """Return node instance ids in the current project."""

    def create_node(self, category: str, name: str, *, x: float = 0, y: float = 0) -> str:
        """Create any registered node through undo history; return its id."""

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its connections through undo history."""

    def connect_nodes(self, output_node_id: str, output_slot: str,
                      input_node_id: str, input_slot: str) -> bool:
        """Connect compatible sockets through undo history."""

    def get_node_property(self, node_id: str, key: str) -> object:
        """Return a detached property value; missing nodes/keys raise KeyError."""

    def set_node_property(self, node_id: str, key: str, value: object) -> None:
        """Set a node property through undo history; missing keys raise KeyError."""

    def set_node_properties(self, node_id: str, values: dict[str, object],
                            label: str = "Plugin properties") -> bool:
        """Apply a batch of property changes as one atomic undo step."""
