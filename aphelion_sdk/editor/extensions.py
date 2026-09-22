"""Editor-wide plugins that contribute UI without adding a graph node."""
from aphelion_sdk.plugin import Plugin
from aphelion_sdk.widgets.host import WidgetHost
from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class EditorCommand:
    """Action in the editor Plugins menu. Callback runs on the UI thread."""
    command_id: str
    title: str
    callback: Callable[[WidgetHost], None]
    shortcut: str = ""

    def __post_init__(self):
        if not self.command_id.strip() or not self.title.strip():
            raise ValueError("Commands require an id and title")
        if not callable(self.callback):
            raise TypeError("Command callback must be callable")



class EditorExtension(Plugin):
    """Attach PanelWidget and DialogWidget classes through widgets.

    Widgets receive an editor host for undoable graph edits and node discovery.
    Extensions respect the same discovery, enablement and reload as node plugins.
    """
    plugin_product = "editor"
    plugin_kind = "extension"
    commands: tuple[EditorCommand, ...] = ()
