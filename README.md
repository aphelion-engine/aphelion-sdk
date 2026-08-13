# Aphelion Plugin SDK

Public API for writing Aphelion plugins. This package lives beside
`aphelion-editor` (not inside it). Plugins run **inside the editor process**
and import editor internals through this SDK only.

Video effects are supported now. Audio plugin bases will land in
`aphelion_sdk.audio` later.

Authors must only `import aphelion_sdk`. Never import `core`, `effects`,
`render`, `ui`, or any other internal editor package.

## Installation

From the `aphelion-engine` root, with a virtual environment active:

```bash
pip install -e ./aphelion-editor
pip install -e ./aphelion-sdk
```

`aphelion-editor` requires this package, so installing the editor from
`aphelion-editor/` also pulls in `../aphelion-sdk`.

Build a wheel (from the engine root):

```bash
python -m build aphelion-sdk
pip install aphelion-sdk/dist/aphelion_plugin_sdk-*.whl
```

Or from this directory:

```bash
python -m build
```

## Quick start

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

See `examples/grayscale_effect.py` for the full runnable example.

If an effect does not use time, name the second argument `_frame_num`.
Time-based effects (grain, flicker, strobe) should keep `frame_num` and
read it.

## Registering a plugin

1. **Drop-in files** — put a `.py` module in the editor's `plugins/` or
   `userdata/plugins/`. The editor imports each file at boot.
2. **In-process registration** — `@aphelion_sdk.register_plugin` on a
   `Plugin` subclass.
3. **Installed packages** — advertise the class under `aphelion.plugins`:

```toml
[project.entry-points."aphelion.plugins"]
grayscale = "my_plugin_package.grayscale:GrayscaleEffect"
```

## API surface

| Symbol | Purpose |
|---|---|
| `Plugin` | Media-agnostic metadata base. Do not subclass directly. |
| `VideoEffectPlugin` | Unary video frame effect (`plugin_kind = "video"`). |
| `Frame` | Video frame buffer (`HxWx3` `float32`, `[0, 1]`). |
| `ColorRgb` | RGB property (`tuple[int, int, int]`, 0-255). |
| `slider_property`, `number_property`, `toggle_property`, `text_property`, `color_property`, `choice_property` | Property builders. |
| `register_plugin` | Decorator for in-process discovery. |
| `get_registered_plugins` | Classes registered via `register_plugin`. |

Audio plugin types are not exported yet (`aphelion_sdk.audio` is a reserved
package).
