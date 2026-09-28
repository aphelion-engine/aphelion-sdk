# Editor SDK API reference

Import these symbols from `aphelion_sdk.editor`. See [authoring](authoring.md),
[audio](audio.md), [widgets](widgets.md) and [extensions](extensions.md) for complete
examples. The product namespace is lazy; resolving runtime node classes requires
the editor runtime. Type declarations are included in the SDK.

## Plugin bases

| Class | Contract |
| --- | --- |
| `NodePlugin` | Define `setup_input_outputs()` and `evaluate(frame_num)` |
| `VideoEffectPlugin` | Default frame effect; override `process_frame(frame, frame_num)` |
| `AudioNodePlugin` | General node base with audio identity |
| `AudioEffectPlugin` | Override `process_audio(audio, frame_num)`; preserve rate and shape |
| `EditorExtension` | Attach `widgets` and `commands`; no graph node |
| `Plugin` | Shared identity metadata; prefer a concrete product base above |
| `EditorCommand(command_id, title, callback, shortcut="")` | Extension menu command; callback receives a WidgetHost |

Node bases support `setup_effect_properties()` and optional
`build_property_panel(host)` / `build_property_qt_widget(parent, host)`.
General node bases supply no default sockets. Video effects supply frame sockets
and enabled/mix (0 to 100); audio effects supply audio sockets and enabled/mix (0 to 1).

## Data and sockets

| Symbol | Contract |
| --- | --- |
| `Frame` | NumPy ndarray; RGB `(H, W, 3)`, float32, nominal 0 to 1 |
| `ColorRgb` | Three integer channels from 0 to 255 |
| `AudioData(samples, sample_rate)` | float32 mono `(N,)` or multichannel `(N, C)` buffer |
| `FrameWithAudio(frame, audio)` | Frame and optional AudioData |
| `NodeSocketType` | Frame, Mask, Number, Color, Audio, Any, legacy Node |
| `NodeValue` | Payload or output-name-to-payload dictionary; supports missing payloads |
| `NodePropertyInputType` | Host property control discriminator |

Node methods include `add_input(name, socket_type)`, `add_output(name, socket_type)`,
`get_input_value(slot)`, `input_frame(slot="frame")`, `input_audio(slot="audio")`,
`input_frame_with_audio(slot="frame")`, `input_number(slot, default=0.0)` and
`blank_frame()`. Multiple outputs must be keyed by their declared socket names.

## Property builders

Pass a builder's result to `self.set_property(key, property)` during setup.
All builders accept keyword-only `label`, `description=""`, `group="General"` and
`priority=100`. Lower priorities sort first.

| Builder | Additional arguments / behavior |
| --- | --- |
| `slider_property(value, minimum, maximum, *, label, ...)` | Integer slider; `suffix=""` |
| `number_property(value, minimum, maximum, *, label, ...)` | Numeric field; `suffix=""` |
| `toggle_property(value, *, label, ...)` | Boolean checkbox |
| `text_property(value, *, label, ...)` | Text field |
| `color_property(value, *, label, ...)` | RGB swatch |
| `choice_property(value, *, label, ...)` | An Enum member determines choices |
| `custom_property(value, *, widget_id, label, ...)` | Persisted JSON-serializable value and a dialog button |
| `PluginProperty` | Property handle type; prefer builders |

Use `float_value`, `int_value`, `bool_value`, `string_value`, `color_value` and
`enum_value` to read evaluated values. `expose_modulation_input(key)` adds an
`in_<key>` Number input for a numeric parameter. See [property examples](authoring.md#declare-and-read-properties).

## Widgets

| Class | Contract |
| --- | --- |
| `InspectorWidget` | Inline properties-page section |
| `PanelWidget` | Dockable editor panel |
| `DialogWidget` | Modal or modeless window; `on_accept(view, host)`, `on_reject(view, host)` |
| `PluginWidget` | Base for attached UI surfaces |
| `WidgetView` | Host primitive controls; [full method table](widgets.md#primitive-controls) |
| `WidgetHost` | Bound properties, window creation and graph operations |
| `WidgetContext` | `plugin_key`, `node_id`, `property_key`, `project_name` |
| `coerce_qt_parent(parent)` | Convert a host parent to a QWidget-compatible parent |
| `is_qt_widget(value)` | Check whether a value is a PyQt6 QWidget |

Attached widgets implement `build_view(host)` or
`build_qt_widget(parent, host)`. A valid native QWidget takes priority over the
primitive view. `on_dispose(host)` handles resource cleanup on destruction.

## WidgetHost

| Method | Contract |
| --- | --- |
| `create_view()` | Empty host-owned WidgetView |
| `context()` | Binding metadata |
| `qt_parent()` | Host Qt parent object |
| `open_dialog(widget_id)` | True when shown; resolves within the owning plugin |
| `get_property_value(key)` | Detached bound-node property value, or None |
| `set_property_value(key, value)` | Undoable write; missing bound nodes/keys are ignored |
| `available_nodes()` | Registered `(category, name)` pairs |
| `list_nodes()` | Current project node ids |
| `create_node(category, name, *, x=0, y=0)` | Create registered type and return its id |
| `remove_node(node_id)` | Undoable removal, returning bool |
| `connect_nodes(output_node_id, output_slot, input_node_id, input_slot)` | Undoable connection, returning bool |
| `get_node_property(node_id, key)` | Detached value; missing identifiers raise KeyError |
| `set_node_property(node_id, key, value)` | Undoable write; missing identifiers raise KeyError |
| `set_node_properties(node_id, values, label="Plugin properties")` | Atomic property batch in one undo step; bool |

Host methods must run on the UI thread. Context does not imply a selected node for
docks, commands or menu-opened dialogs. See [graph automation](extensions.md#graph-operations).

## Discovery and compatibility

| Symbol | Purpose |
| --- | --- |
| `register_plugin` | Decorator for node/extension classes, not widget classes |
| `get_registered_plugins()` | Snapshot of decorated classes |
| `discover_installed_plugins()` | Both `aphelion.editor.plugins` and legacy `aphelion.plugins` entry points |
| `clear_registered_plugins()` | Host reload helper; plugin code should not clear other registrations |
| `PRODUCT_ID` | `"editor"` |
| `API_VERSION` | `1` |
| `__version__` | SDK distribution version, distinct from API_VERSION |

Product metadata defaults to `plugin_product = "editor"` and
`plugin_api_version = 1`. The editor filters incompatible products/API versions.
See [migration](editor.md#migrating-existing-plugins).

## Installation and packaging tools

`aphelion_sdk.host` provides `locate_editor`, `discover_editors`,
`install_plugins_into_editor`, `EditorInstall` and `EditorHostError` for tooling.
These locate the editor or copy source plugins into its user folder.

```text
aphelion-sdk --version
aphelion-sdk build [source] [-o DIR] [-n NAME] [--package-version VER]
python -m aphelion_sdk build ...
```

See [packaging plugins](packaging.md) for building and installing your plugins.
