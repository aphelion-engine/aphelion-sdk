# Custom properties UI and windows

Widgets belong to a node plugin or an `EditorExtension`. Attach classes with
`widgets = (MyInspector, MyDialog, MyPanel)`; do not decorate widgets with
`@register_plugin`.

| Class | Where it appears |
| --- | --- |
| `InspectorWidget` | Inline in the selected node's properties page |
| `DialogWidget` | Custom window, opened from a property row, button or window menu |
| `PanelWidget` | Dock in the editor, independent of node selection |

## A complete inspector and property window

Copy this whole example into `inspector_example.py` in the user plugins folder and
reload. Add **My Plugins > Inspector Example**, select it, and use the inline
controls or **Notes** property button.

```python
from aphelion_sdk.editor import (
    DialogWidget, InspectorWidget, VideoEffectPlugin,
    custom_property, number_property, register_plugin,
)


class NotesDialog(DialogWidget):
    widget_id = "notes"
    widget_title = "Effect notes"
    widget_show_in_menu = False
    widget_modal = False

    def build_view(self, host):
        view = host.create_view()
        view.add_text("notes", str(host.get_property_value("notes") or ""))
        return view

    def on_accept(self, view, host):
        host.set_property_value("notes", view.get_text("notes"))


class GainInspector(InspectorWidget):
    widget_title = "Extra controls"

    def build_view(self, host):
        view = host.create_view()
        view.add_number("gain", "Gain", float(host.get_property_value("gain")),
                        minimum=0, maximum=4,
                        on_change=lambda value: host.set_property_value("gain", value))
        view.add_button("notes", "Open notes window", lambda: host.open_dialog("notes"))
        return view


@register_plugin
class InspectorExample(VideoEffectPlugin):
    plugin_name = "Inspector Example"
    plugin_category = "My Plugins"
    widgets = (GainInspector, NotesDialog)

    def setup_effect_properties(self):
        self.set_property("gain", number_property(1.0, 0.0, 4.0, label="Gain"))
        self.set_property("notes", custom_property("", widget_id="notes", label="Notes"))

    def process_frame(self, frame, frame_num):
        return frame * self.float_value("gain", 1.0)
```

Generated properties remain visible; an `InspectorWidget` adds a section. The
custom property stores the notes and references the dialog's `widget_id`. The
inline button opens the same window. Set `widget_modal = True` to block the editor
until the window is dismissed; False opens a modeless window.

The dialog stages text locally and commits only on OK. `on_reject(view, host)` is
available for cancellation cleanup. In contrast, calls to host setters take effect
immediately; cancelling a window does not revert edits already sent to the host.

## Primitive controls

`view = host.create_view()` returns a host-owned layout. Use unique control ids
within each view. Callbacks receive the new value, except button callbacks, which
receive no arguments.

| Method | Purpose |
| --- | --- |
| `add_label(id, text)` | Static, wrapping label |
| `add_button(id, label, on_click)` | Button |
| `add_text(id, value, placeholder="", on_change=None)` | Text field; callback on user edits |
| `add_number(id, label, value, minimum=-1e9, maximum=1e9, on_change=None)` | Numeric field |
| `add_toggle(id, label, value, on_change=None)` | Checkbox |
| `add_choice(id, label, choices, value, on_change=None)` | Dropdown; value must be in choices |
| `add_separator()` | Divider |
| `get_value(id)` | Read text, number, toggle or choice; unknown id raises KeyError |
| `set_value(id, value)` | Update those controls without firing change callbacks |
| `get_text(id)` / `set_text(id, text)` | Read/update a label, button or text field |
| `embed_native(widget)` | Insert a PyQt6 QWidget |

Primitive controls are not automatically bound to properties. Supply a callback
for writes and read initial values from the host. Refresh a retained view with
`set_value` when your UI needs to reflect outside edits. Plugin control callback
exceptions are logged by the editor.

## Node-bound context

`host.context()` provides `plugin_key`, optional `node_id`, optional `property_key`,
and `project_name`. Inspector widgets and dialogs opened from their controls keep
the bound node id; switching selection does not retarget an already open dialog.

`get_property_value(key)` returns a detached copy or None when the node/property is
missing. `set_property_value(key, value)` writes through undo history; missing
bindings are ignored. For several related values in one undo step:

```python
# Inside a widget callback; host is supplied by the editor.
node_id = host.context().node_id
if node_id is not None:
    host.set_node_properties(node_id, {"gain": 1.0, "notes": ""}, label="Reset effect")
```

Dialogs opened from the window menu and editor-wide docks have no selected-node
binding. Hide node-specific dialogs from that menu with `widget_show_in_menu = False`.
For explicit node ids, use the [graph host methods](extensions.md#graph-operations).
Dialog ids resolve within the owning plugin.

## Native PyQt6 bodies

For custom layouts, return a QWidget from `build_qt_widget(parent, host)`. That
method takes priority over `build_view` when it returns a valid widget. The editor
supplies the dock/dialog/inspector container and owns the returned body.

```python
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from aphelion_sdk.editor import InspectorWidget, coerce_qt_parent


class NativeInspector(InspectorWidget):
    widget_title = "Native controls"

    def build_qt_widget(self, parent, host):
        body = QWidget(coerce_qt_parent(parent))
        layout = QVBoxLayout(body)
        button = QPushButton("Reset gain", body)
        button.clicked.connect(lambda checked=False: host.set_property_value("gain", 1.0))
        layout.addWidget(button)
        return body
```

Attach `NativeInspector` to a node declaring `gain`. You can alternatively embed a
native widget in a primitive view using `embed_native`. Handle exceptions in your
own native Qt signal callbacks; those signals do not use the primitive callback wrapper.

A node can supply an additional UI directly through `build_property_panel(host)`
or `build_property_qt_widget(parent, host)`. Return a view or QWidget respectively,
or None for no UI. These hooks also work on general and audio node bases. Use an
attached `InspectorWidget` when you need its `on_dispose(host)` lifecycle hook.

## Widget metadata and cleanup

| Attribute | Applies to | Meaning |
| --- | --- | --- |
| `widget_id` | All | Stable id; defaults to class name |
| `widget_title` | All | Section/window title; defaults to id |
| `widget_modal` | Dialog | True by default |
| `widget_width`, `widget_height` | Dialog | Initial size in pixels |
| `widget_show_in_menu` | Dialog | Show under Window > Plugin Windows; True by default |
| `widget_default_visible` | Panel | Show dock initially; False by default |
| `widget_dock_area` | Panel | `left`, `right`, `top` or `bottom` placement hint |

The editor may recreate UI on selection changes, undo or reload. Store project
state in properties, not widget fields. Release owned timers or external
subscriptions in `on_dispose(host)`, called when an attached surface is destroyed.
Do not assume native child controls are still usable during disposal. Call host
methods on the UI thread and keep callbacks short.

See [editor extensions](extensions.md) for a complete dock example, or the
[native notes example](../examples/effect_with_widget.py) for a multiline editor.
