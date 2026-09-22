# Authoring plugins

Plugins run **inside the editor process**. Import `aphelion_sdk` only. Never import `core`, `effects`, `render`, `ui`, or other editor packages.

Video, audio and general-purpose nodes are supported. New plugins should import `aphelion_sdk.editor`; see [Editor extensions](editor.md).

## Minimal effect

```python
import aphelion_sdk


@aphelion_sdk.register_plugin
class GrayscaleEffect(aphelion_sdk.VideoEffectPlugin):
    plugin_name = "Grayscale"
    plugin_category = "Plugins"
    plugin_description = "Blend a frame toward grayscale."
    plugin_color = (140, 140, 140)

    def setup_effect_properties(self) -> None:
        self.set_property(
            "amount",
            aphelion_sdk.slider_property(
                100, 0, 100,
                label="Amount",
                description="How much to desaturate the frame.",
                suffix="%",
            ),
        )

    def process_frame(
        self,
        frame: aphelion_sdk.Frame,
        _frame_num: int,
    ) -> aphelion_sdk.Frame:
        amount = self.float_value("amount", 100.0) / 100.0
        luma = (
            frame[..., 0] * 0.2126
            + frame[..., 1] * 0.7152
            + frame[..., 2] * 0.0722
        )
        gray = luma[..., None].repeat(3, axis=2)
        return frame * (1.0 - amount) + gray * amount
```

Full file: [`examples/grayscale_effect.py`](../examples/grayscale_effect.py). Widgets example: [`examples/effect_with_widget.py`](../examples/effect_with_widget.py).

## Class attributes

Set these on the plugin class (copied onto the host node schema):

| Attribute | Meaning |
|---|---|
| `plugin_name` | Display name and node type |
| `plugin_category` | Add Node menu group (default `Plugins`) |
| `plugin_description` | Tooltip / search text |
| `plugin_color` | Header RGB, each channel `0–255` |
| `plugin_author` | Optional credit |
| `widgets` | Tuple of `PluginWidget` classes (dialogs/panels) |

Do not subclass `Plugin` directly. Use `VideoEffectPlugin`.

## Required methods

`setup_effect_properties` — call `self.set_property(key, builder(...))` once per parameter.

`process_frame(frame, frame_num)` — return a processed `Frame` with the same shape and dtype. `frame` is `(height, width, 3)` `float32` in `[0, 1]`. Time-independent effects should name the second argument `_frame_num`. Time-based effects (grain, flicker) should keep `frame_num` and read it.

The host already adds frame sockets plus standard **Enabled** / **Mix** controls.

## Reading properties

Use the helpers inherited from the host node:

- `float_value(key, default)`
- `bool_value(key, default)`

A connected modulation socket or Property Drive can override numeric properties at evaluation time.

## Discovery

1. Drop a `.py` file in the editor's `plugins/` or `userdata/plugins/`.
2. Decorate the class with `@aphelion_sdk.register_plugin`.
3. Or ship a wheel with an `aphelion.editor.plugins` entry point.

The editor's **Preferences → Plugins** can disable types, skip discovery sources, and reload drop-in files. See [editor plugin docs](../../aphelion-editor/docs/plugins.md) and [packaging](packaging.md).

## Rules

- One public import: `aphelion_sdk` (PyQt6 is allowed only for widget bodies; see [widgets](widgets.md)).
- Do not decorate a `PluginWidget` with `@register_plugin`. Attach it via `widgets = (...)`.
- Return frames in the same layout as the input. Do not block the UI thread; `process_frame` already runs on the evaluation path.
