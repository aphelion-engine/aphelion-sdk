# Aphelion Editor extensions

New plugins import `aphelion_sdk.editor`. This is the product boundary: another
Aphelion product will have its own namespace and runtime contracts. Shared
packaging and installation tooling remain under `aphelion_sdk`. Existing root,
`video`, `audio`, and `widgets` imports remain compatibility APIs.

Editor runtime bases use the installed editor's node engine. For local development,
put `aphelion-editor/src` and `aphelion-sdk` on `PYTHONPATH`; the SDK does not ship a
second renderer. Packaging and importing the lazy product namespace do not require
an editor runtime. Native UI uses PyQt6 supplied by the editor.

## Node APIs

| Base | Implement | Behavior |
| --- | --- | --- |
| `NodePlugin` | `setup_input_outputs`, `evaluate` | Arbitrary generators, effects, masks, compositors, logic, mixed-media and multiple outputs |
| `VideoEffectPlugin` | `process_frame` | Default frame sockets, enabled/mix controls, automatic audio preservation |
| `AudioNodePlugin` | `setup_input_outputs`, `evaluate` | Arbitrary audio generation, routing, resampling and analysis |
| `AudioEffectPlugin` | `process_audio` | Audio sockets, enabled/mix controls and block shape/rate validation |

Use `setup_effect_properties` to call `set_property(key, number_property(...))`
(or slider, toggle, text, choice, color, custom). It runs once after socket setup.
Properties use the normal editor persistence, animation and undo paths.
Read evaluated values with `float_value`, `int_value`, `bool_value`, `string_value`,
`color_value` or `enum_value`; use `expose_modulation_input` for numeric modulation.

`NodeSocketType` exposes Frame, Mask, Number, Color, Audio, Any and legacy Node.
Use `add_input` / `add_output` for any combination. `evaluate(frame_num)` returns
one payload, or a dictionary keyed by output socket names. Frames are float32 RGB
arrays; masks may be arrays; numbers are scalars. `AudioData(samples, sample_rate)`
uses float32 mono `(samples,)` or multichannel `(samples, channels)` buffers.
`FrameWithAudio` carries both. Do not mutate upstream input buffers.

Audio effects process timeline-aligned blocks, not a separate realtime audio
callback. `AudioEffectPlugin.process_audio` must preserve sample rate and shape;
use `AudioNodePlugin` for other contracts. Missing audio returns None. Mix is 0?1
for audio and 0?100 for the legacy video base. Custom video plugins can override
both `setup_input_outputs` and `evaluate` instead of using the unary effect path.

## Properties pages and windows

Attach classes using `widgets = (MyInspector, MyDialog, MyPanel)`:

- `InspectorWidget`: inline section in the selected node's properties page.
- `DialogWidget`: custom window opened by a `custom_property(widget_id=...)` row
  or `host.open_dialog(id)`. `widget_modal = False` opens a modeless window.
- `PanelWidget`: editor dock, available without selecting a node.

Implement `build_view(host)` using `host.create_view()`. Controls include labels,
buttons, text, numbers, toggles, choices and separators. Numeric, toggle, choice
and text controls accept `on_change`; `set_value` refreshes values without firing
change callbacks, and `get_value` reads them. Use `get_text` for text-based controls.
For arbitrary PyQt6 layouts implement `build_qt_widget(parent, host)` or use
`view.embed_native(widget)`. The host owns and destroys the widgets. Release timers
and external subscriptions in `on_dispose(host)`.

A node may also implement `build_property_panel(host)` or
`build_property_qt_widget(parent, host)`. Attached inspector sections and the node
hook can coexist. Dialog `on_accept(view, host)` commits staged edits;
`on_reject` handles cancellation. Edits made directly through host setters are
immediate, including edits made before a dialog is cancelled.

`host.context()` identifies the plugin, node and optional property. Bound
`get_property_value` / `set_property_value` access the selected node; setters use
undo history. Read values are detached copies, so editing a list or dictionary
cannot silently mutate the project. A missing bound node is a no-op for these
convenience methods. Dialog ids resolve strictly within their owning plugin.

## Extending the editor

An `EditorExtension` has no graph node. Attach docks/dialogs and define
`commands = (EditorCommand("id", "Title", callback, shortcut=""),)`.
Commands appear in Plugins ? extension name; callbacks receive a fresh host and
run on the UI thread. Exceptions are logged without escaping into Qt.

Every widget/command host provides:

- `available_nodes()`: `(category, name)` for every currently registered built-in
  or enabled plugin node; use these exact pairs with `create_node`.
- `create_node(category, name, x=0, y=0)`: create any registered effect/audio/node
  type, returning its stable instance id.
- `list_nodes()`, `remove_node(id)`, `connect_nodes(source, output, target, input)`.
- `get_node_property(id, key)` and `set_node_property(id, key, value)`.
- `set_node_properties(id, values, label=...)`: atomic batch with one undo step.

Graph edits use the editor's history, cache invalidation and document events.
Explicit node/property lookups raise KeyError for unknown identifiers. Connection
creation returns False when the editor rejects an incompatible link or cycle.
Call host methods on the UI thread. Node evaluation is separate from UI work.

## Discovery and compatibility

Decorate concrete plugin classes with `@register_plugin`. Drop source files into
`userdata/plugins`, or build a wheel with `aphelion-sdk build example.py -o dist`.
New wheels use the `aphelion.editor.plugins` entry-point group. The editor also
reads legacy `aphelion.plugins`, deduplicating classes appearing in both.

Plugins declare `plugin_product = "editor"` and `plugin_api_version = 1` by default.
The editor skips other products and unsupported API versions. Enabled extensions,
commands and widgets follow Preferences ? Plugins and reload. Plugins cannot
replace built-in registry entries. Existing node instances retain their old class
on reload; reopen a project to reconstruct them with new code.

See [the complete example](../examples/editor_extension.py) for audio processing,
a multi-output effect, an inline inspector, a modeless property window, a dock,
and a menu command. No editor-internal imports are needed in plugin source.
