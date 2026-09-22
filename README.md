# Aphelion Plugin SDK

Editor nodes, audio, inspector UI, windows, docks and commands are documented in the [Editor SDK guide](docs/editor.md). New plugins use `aphelion_sdk.editor`.

Public API for plugins that run **inside Aphelion Editor**. This package sits beside `aphelion-editor`, not inside it.

Import **`aphelion_sdk` only**. Never import `core`, `effects`, `render`, or `ui`.

Video, audio, arbitrary graph nodes and editor extensions are available under `aphelion_sdk.editor`.

Version **0.1.0**. Python **3.11+**. Install with **`pip install aphelion-plugin-sdk`**. Import **`aphelion_sdk`**.

## Install

```bash
pip install aphelion-plugin-sdk
```

From the `aphelion-engine` root, with a venv active:

```bash
pip install -e ./aphelion-editor
pip install -e ./aphelion-sdk
```

Installing the editor already depends on this package (`aphelion-plugin-sdk @ file:../aphelion-sdk`).

```bash
aphelion-sdk --version
python -m aphelion_sdk --help
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

Drop the file in the editor's `plugins/` or `userdata/plugins/`, or pack a wheel (below). Time-independent effects should name the unused argument `_frame_num`.

Examples:

- [`examples/grayscale_effect.py`](examples/grayscale_effect.py)
- [`examples/effect_with_widget.py`](examples/effect_with_widget.py) — dialog + panel via `widgets = (...)`

## Documentation

| Guide | Contents |
|---|---|
| [Authoring](docs/authoring.md) | Effect class, properties, discovery rules |
| [Widgets](docs/widgets.md) | Panels, dialogs, primitives, PyQt6 |
| [API reference](docs/api.md) | Public symbols |
| [Packaging](docs/packaging.md) | `aphelion-sdk build`, entry points, drop-in install |
| [Editor plugins](../aphelion-editor/docs/plugins.md) | How the host loads and reloads plugins |

## Package a plugin

```bash
aphelion-sdk build examples/grayscale_effect.py -o dist
pip install dist/aphelion_plugin_grayscale-*.whl
```

Entry point group: `aphelion.editor.plugins`. Widgets are declared on the plugin (`widgets = (MyDialog, MyPanel)`); they are not registered on their own.

## License

Proprietary (`LicenseRef-Proprietary` in `pyproject.toml`).
