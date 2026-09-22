# API reference

Editor nodes, audio, inspector UI, windows, docks and commands are documented in the [Editor SDK guide](editor.md). New plugins use `aphelion_sdk.editor`.

Import from `aphelion_sdk` only. Symbols are loaded lazily on first access.

Version: `aphelion_sdk.__version__` (distribution name `aphelion-plugin-sdk`).

## Plugins

| Symbol | Purpose |
|---|---|
| `Plugin` | Media-agnostic metadata base. Do not subclass directly. |
| `VideoEffectPlugin` | Unary video frame effect (`plugin_kind = "video"`). |
| `register_plugin` | Class decorator for in-process discovery. |
| `get_registered_plugins` | Classes registered via `register_plugin`. |
| `clear_registered_plugins` | Drop in-process registrations (editor reload). |
| `discover_installed_plugins` | Load `aphelion.editor.plugins` entry points. |

`VideoEffectPlugin` methods you implement: `setup_effect_properties`, `process_frame`. Optional: `build_property_panel`, `build_property_qt_widget`.

## Types

| Symbol | Purpose |
|---|---|
| `Frame` | `numpy.ndarray`, shape `(H, W, 3)`, `float32`, `[0, 1]`. No alpha. |
| `ColorRgb` | `tuple[int, int, int]`, each channel `0–255`. |

## Properties

Pass builder results to `self.set_property(key, ...)`. Common keyword args: `label`, `description`, `group` (default `General`), `priority` (lower first, default `100`).

| Builder | Control |
|---|---|
| `slider_property(value, min, max, *, label, suffix="")` | Integer slider |
| `number_property(value, min, max, *, label, suffix="")` | Float spin box |
| `toggle_property(value, *, label)` | Checkbox |
| `text_property(value, *, label)` | Line edit |
| `color_property(value, *, label)` | RGB swatch |
| `choice_property(enum_value, *, label)` | Enum dropdown |
| `custom_property(value, *, widget_id, label)` | Opens a `DialogWidget` on this plugin |
| `PluginProperty` | Opaque handle type (do not construct) |

## Widgets

| Symbol | Purpose |
|---|---|
| `PluginWidget` | Base UI surface. Not registered alone. |
| `PanelWidget` | Dockable panel. |
| `DialogWidget` | Popup (`on_accept` / `on_reject`). |
| `WidgetHost` | Factory, properties, `open_dialog`, `qt_parent`. |
| `WidgetView` | Primitive controls + `embed_native`. |
| `WidgetContext` | Binding to plugin/node/property. |
| `coerce_qt_parent` | Parent a `QWidget` to a host object. |
| `is_qt_widget` | Type check for embedded widgets. |

## Host helpers (optional)

`aphelion_sdk.host` is for tooling, not effect code:

| Symbol | Purpose |
|---|---|
| `locate_editor` / `discover_editors` | Find an installed Aphelion Editor |
| `install_plugins_into_editor` | Copy `.py` files into `userdata/plugins` |
| `EditorInstall` / `EditorHostError` | Result and error types |

## CLI

```text
aphelion-sdk --version
aphelion-sdk build [source] [-o DIR] [-n NAME] [--package-version VER]
python -m aphelion_sdk build ...
```

See [packaging](packaging.md).
