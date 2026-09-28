# Extending the editor

`EditorExtension` contributes tools without adding a node type to the graph. It
can own dock panels, dialogs and menu commands. For inline Properties UI, attach
an `InspectorWidget` to a [node plugin](authoring.md) instead.

## A complete dock and menu command

Save this module as `node_tools.py`, place it in the user plugins folder and reload.
It defines a node, a dock button, and **Plugins > Tutorial Tools > Add Number**.

```python
from aphelion_sdk.editor import (
    EditorCommand, EditorExtension, NodePlugin, NodeSocketType, PanelWidget,
    number_property, register_plugin,
)


@register_plugin
class TutorialNumber(NodePlugin):
    plugin_name = "Tutorial Number"
    plugin_category = "My Plugins"

    def setup_input_outputs(self):
        self.add_output("value", NodeSocketType.Number)

    def setup_effect_properties(self):
        self.set_property("value", number_property(1.0, -100.0, 100.0, label="Value"))

    def evaluate(self, frame_num):
        return self.float_value("value", 1.0)


def add_number(host):
    host.create_node("My Plugins", "Tutorial Number", x=100, y=100)


class ToolPanel(PanelWidget):
    widget_id = "tools"
    widget_title = "Node tools"
    widget_default_visible = True
    widget_dock_area = "right"

    def build_view(self, host):
        view = host.create_view()
        view.add_button("add", "Add Number", lambda: add_number(host))
        return view


@register_plugin
class TutorialTools(EditorExtension):
    plugin_name = "Tutorial Tools"
    widgets = (ToolPanel,)
    commands = (EditorCommand("add-number", "Add Number", add_number),)
```

The node and extension are separately listed in Preferences > Plugins. Keep both
enabled for this example. The dock also appears under Window > Panels. Commands
run on the UI thread and receive a host for the current project. The optional
`shortcut` argument accepts a Qt shortcut string; avoid collisions with editor or
other plugin shortcuts. Command ids must be unique within the extension.

## Graph operations

The host can create any currently registered built-in or plugin node. Discover
exact category/name pairs with `available_nodes()` instead of guessing labels.
Graph mutations go through editor history and cache invalidation.

| Method | Result and behavior |
| --- | --- |
| `available_nodes()` | Tuple of `(category, name)` pairs |
| `list_nodes()` | Tuple of current project node ids |
| `create_node(category, name, *, x=0, y=0)` | New stable node id; unknown type raises KeyError |
| `remove_node(node_id)` | True if a removal was recorded; connections are included in undo |
| `connect_nodes(output_node_id, output_slot, input_node_id, input_slot)` | True if accepted; False for invalid connections |
| `get_node_property(node_id, key)` | Detached property value; missing node/key raises KeyError |
| `set_node_property(node_id, key, value)` | Undoable property write; missing node/key raises KeyError |
| `set_node_properties(node_id, values, label="Plugin properties")` | Atomic property batch, one undo step; returns whether applied |

For example, a command can create two instances of a known audio processor and
connect them. This callback requires the `Tutorial Gain` node from the
[audio tutorial](audio.md) to be installed and enabled:

```python
# Pass this function as an EditorCommand callback.
def add_gain_chain(host):
    if ("My Plugins", "Tutorial Gain") not in host.available_nodes():
        return
    first = host.create_node("My Plugins", "Tutorial Gain", x=100, y=100)
    second = host.create_node("My Plugins", "Tutorial Gain", x=350, y=100)
    host.set_node_properties(first, {"gain": 0.5, "mix": 1.0}, label="Configure gain")
    host.connect_nodes(first, "audio", second, "audio")
```

Each graph operation is its own undo step. Only `set_node_properties` groups the
property writes passed to that call; the SDK does not expose a general graph
transaction API. The source input in this example remains unconnected for the user.

The host does not expose socket introspection for arbitrary types. When connecting
nodes, use the documented sockets of the type you create. A dock or command has no
implicit selected-node binding; use explicit node ids for property access.

## Windows and lifecycle

An extension may attach `DialogWidget` classes and open them with
`host.open_dialog(widget_id)` or expose them in Window > Plugin Windows. See
[custom UI](widgets.md) for modal/modeless windows and staged edits.

Disabling or reloading extensions rebuilds their command menu and docks. The
widget host targets the live editor project, so do not retain old node ids as if
they belong to every project. Catch missing-node errors if a user can remove a
node while your tool remains open.

Implement `on_dispose(host)` on attached widgets to release resources. There are
no general `EditorExtension.on_load`/`on_unload` hooks or public project-event
subscription API in this version. The supported extension surfaces are registered
nodes, attached widgets, commands and the host methods documented here.
