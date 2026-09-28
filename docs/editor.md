# Product compatibility and troubleshooting

## Product namespaces

New plugins target Aphelion Editor through `aphelion_sdk.editor`. Editor is the
only current product. Its node, audio, UI and extension contracts live under that
namespace; another product can have its own namespace without mixing its APIs
into editor plugins. Packaging and installation tooling remain shared.

Convenience submodules include `aphelion_sdk.editor.nodes`, `.video`, `.audio`,
`.properties`, `.widgets` and `.extensions`. Prefer the main product namespace when
combining several features in one plugin.

`plugin_product` defaults to `"editor"`; `plugin_api_version` defaults to `1`.
The loader ignores other products and unsupported API versions. This API version
is separate from the SDK distribution's version number. Publishing/installing a
new SDK does not update the editor application: the new APIs require the editor
implementation that supports them.

## Migrating existing plugins

| Existing usage | Recommended usage |
| --- | --- |
| `import aphelion_sdk` | `from aphelion_sdk import editor as sdk` and use `sdk.*` |
| `aphelion_sdk.VideoEffectPlugin` | `aphelion_sdk.editor.VideoEffectPlugin` |
| Audio/general logic in a custom video plugin | `AudioEffectPlugin`, `AudioNodePlugin` or `NodePlugin` |
| Node-specific properties UI | Attached `InspectorWidget` or existing node UI hook |
| Dummy node used only to own a dock | `EditorExtension` |
| `aphelion.plugins` package entry points | `aphelion.editor.plugins` for new packages |

Root imports and old video/widget modules remain supported. Legacy entry points
are still discovered, and duplicate class objects are deduplicated. The video base
supports both `process_frame` effects and custom `setup_input_outputs` + `evaluate`
implementations. Properties now initialize after custom socket setup.

Use the actual hook signatures: `build_property_panel(host)` and
`build_property_qt_widget(parent, host)`. Zero-argument implementations do not match
the editor's calls. Attached widgets receive those arguments through `build_view`
and `build_qt_widget` instead.

Do not rename saved plugin categories/names, sockets or property keys merely to
adopt the new imports. Those identities are used by existing projects.

## Discovery and reload

Decorated source plugins load from bundled/user folders. A user file with the
same filename overrides the bundled module. Files beginning with `_` are skipped.
Installed packages can expose classes via entry points. Preferences > Plugins
controls discovery sources and per-plugin enablement.

Plugins cannot replace an already registered built-in node type. Use a distinct
category/name pair. Failed drop-in imports are logged and their partially
registered classes are excluded from discovery.

Reload updates discovery, menus and docks. Existing graph nodes keep their old
Python class; recreate them or reopen the project to use revised implementations.
The SDK does not automatically migrate renamed types or arbitrary instance state.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `ModuleNotFoundError: core` when importing a node base | The SDK needs the editor runtime. Use the editor environment and [local setup](authoring.md#local-development). |
| Plugin absent from Add Node | Check `@register_plugin`, folder, filename, preferences and import errors in the editor log. EditorExtension has no graph node by design. |
| Installed plugin not discovered | Install into the editor's Python environment; enable entry-point loading and check the entry-point group. |
| Old processing after Reload | Recreate the graph node or reopen the project. |
| Inline custom UI absent | Attach an InspectorWidget in `widgets = (...)`, select its node and return a view/QWidget from the correct hook. |
| Dialog cannot find a property | Check host.context().node_id. Docks and menu-opened dialogs are not bound to selection. |
| Custom property button opens nothing | Its widget_id must match a DialogWidget attached to the same plugin. |
| Cancel does not revert an edit | Host setters commit immediately. Stage values in the dialog and write them in on_accept for commit-on-OK behavior. |
| Audio processor fails on output | Return AudioData with float32 samples, unchanged shape and sample rate; use AudioNodePlugin for resampling. |
| Time-dependent output stays unchanged | Set is_temporal = True when output varies by frame independently of inputs. |
| A graph edit creates several undo steps | Each host operation is separate; only set_node_properties groups its property batch. |

## Tutorials and examples

- [First plugin](../README.md#install-and-run-your-first-plugin)
- [General nodes and properties](authoring.md)
- [Audio](audio.md)
- [Custom UI](widgets.md)
- [Docks, commands and graph edits](extensions.md)
- [Combined runnable example](../examples/editor_extension.py)
