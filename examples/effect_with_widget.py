"""Video effect with widgets attached to the plugin (not registered alone).

Drop this file in ``plugins/`` or ``userdata/plugins/``. The notes dialog
and status panel belong to ``Grayscale With Notes`` via ``widgets = (...)``.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

import aphelion_sdk


class NotesDialog(aphelion_sdk.DialogWidget):
    """Popup editor for the effect's notes property, built with PyQt6."""

    widget_id = "notes"
    widget_title = "Clip Notes"

    def __init__(self) -> None:
        self._editor: QTextEdit | None = None

    def build_qt_widget(
        self,
        parent: object,
        host: aphelion_sdk.WidgetHost,
    ) -> object | None:
        """Return a multi-line notes editor owned by the host dialog."""
        root = QWidget(aphelion_sdk.coerce_qt_parent(parent))
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        hint = QLabel("Notes are stored on this effect node.")
        hint.setWordWrap(True)
        self._editor = QTextEdit()
        self._editor.setPlainText(str(host.get_property_value("notes") or ""))
        layout.addWidget(hint)
        layout.addWidget(self._editor, 1)
        return root

    def on_accept(
        self,
        view: aphelion_sdk.WidgetView,
        host: aphelion_sdk.WidgetHost,
    ) -> None:
        """Write the editor contents back onto the bound node."""
        del view
        if self._editor is None:
            return
        host.set_property_value("notes", self._editor.toPlainText())


class StatusPanel(aphelion_sdk.PanelWidget):
    """Dock owned by the grayscale plugin."""

    widget_id = "status"
    widget_title = "Status"

    def build_view(self, host: aphelion_sdk.WidgetHost) -> aphelion_sdk.WidgetView:
        """Show a short help panel and a button that opens the notes dialog."""
        view = host.create_view()
        view.add_label("title", "Grayscale With Notes")
        view.add_label(
            "help",
            "Select the effect in the graph, then edit notes from Properties.",
        )
        view.add_separator()
        view.add_button("open_notes", "Open Notes…", self._open_notes(host))
        return view

    def _open_notes(
        self,
        host: aphelion_sdk.WidgetHost,
    ) -> Callable[[], None]:
        """Return a click handler that opens this plugin's notes dialog."""

        def _on_click() -> None:
            host.open_dialog("notes")

        return _on_click


@aphelion_sdk.register_plugin
class GrayscaleWithNotes(aphelion_sdk.VideoEffectPlugin):
    """Grayscale mix with an attached notes dialog and status dock."""

    plugin_name = "Grayscale With Notes"
    plugin_category = "Plugins"
    plugin_description = "Desaturate a frame; notes open in a plugin-owned popup."
    plugin_color = (140, 140, 140)
    widgets = (NotesDialog, StatusPanel)

    def setup_effect_properties(self) -> None:
        """Register mix amount and a custom notes editor."""
        self.set_property(
            "amount",
            aphelion_sdk.slider_property(
                100,
                0,
                100,
                label="Amount",
                suffix="%",
            ),
        )
        self.set_property(
            "notes",
            aphelion_sdk.custom_property(
                "",
                widget_id="notes",
                label="Notes",
                description="Opens this plugin's notes dialog.",
            ),
        )

    def build_property_panel(
        self,
        host: aphelion_sdk.WidgetHost,
    ) -> aphelion_sdk.WidgetView | None:
        """Inspector actions that call into the attached notes dialog."""
        view = host.create_view()
        view.add_button("edit_notes", "Edit Notes…", self._open_notes(host))
        return view

    def _open_notes(
        self,
        host: aphelion_sdk.WidgetHost,
    ) -> Callable[[], None]:
        """Return a click handler that opens this plugin's notes dialog."""

        def _on_click() -> None:
            host.open_dialog("notes")

        return _on_click

    def process_frame(
        self,
        frame: aphelion_sdk.Frame,
        frame_num: int,
    ) -> aphelion_sdk.Frame:
        """Blend the frame toward luma-derived grayscale."""
        del frame_num
        amount: float = self.float_value("amount", 100.0) / 100.0
        luma = (
            frame[..., 0] * 0.2126 + frame[..., 1] * 0.7152 + frame[..., 2] * 0.0722
        )
        gray = luma[..., None].repeat(3, axis=2)
        return frame * (1.0 - amount) + gray * amount
