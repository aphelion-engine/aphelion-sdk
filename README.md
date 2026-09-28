# Aphelion SDK

Build plugins for Aphelion Editor: video effects, audio processors, generators,
compositors, masks, logic nodes, custom properties UI, windows, docks and menu commands.

New editor plugins import `aphelion_sdk.editor`. Product APIs are kept in their own
namespaces; packaging and installation tools are shared. The existing root imports
remain supported for older plugins. Plugin code should not import editor internals
such as `core`, `effects`, `render` or `ui`.

## Install and run your first plugin

Use Python 3.11 or newer and an updated Aphelion Editor. Install the SDK in the
Python environment used by the editor:

```shell
python -m pip install --upgrade aphelion-plugin-sdk
```

The SDK provides an extension API, not a standalone editor runtime. Node classes
use the editor's runtime. For development against the sibling repositories, see
[local setup](docs/authoring.md#local-development).

Save this complete plugin as `brightness.py`:

```python
from aphelion_sdk.editor import VideoEffectPlugin, number_property, register_plugin


@register_plugin
class Brightness(VideoEffectPlugin):
    plugin_name = "Example Brightness"
    plugin_category = "My Plugins"
    plugin_description = "Multiply the brightness of a frame."

    def setup_effect_properties(self):
        self.set_property("gain", number_property(1.0, 0.0, 4.0, label="Gain"))

    def process_frame(self, frame, frame_num):
        return frame * self.float_value("gain", 1.0)
```

1. Open **Preferences > Plugins > Open user folder** in the editor and copy the file there.
2. Enable user plugins and select **Reload plugins**.
3. Add **My Plugins > Example Brightness** to the graph.
4. Connect a source frame to its `frame` input and its `frame` output to a viewer.
5. Select the node and change **Gain** in Properties. **Enabled** and **Mix** are supplied automatically.

## Choose your extension

| You want to build | Start with |
| --- | --- |
| A single-input video effect | `VideoEffectPlugin.process_frame` |
| An audio processor | `AudioEffectPlugin.process_audio` |
| A generator, compositor, mask, logic or multi-output node | `NodePlugin` |
| Audio generation, routing or a different audio socket layout | `AudioNodePlugin` |
| A custom section in a node's properties page | `InspectorWidget` |
| A custom property editor or popup window | `DialogWidget` |
| A dock or menu command without a graph node | `EditorExtension` with `PanelWidget` / `EditorCommand` |

## Learn the SDK

| Guide | What you will build or learn |
| --- | --- |
| [Authoring nodes](docs/authoring.md) | Video effects, arbitrary sockets, multiple outputs, properties and local setup |
| [Audio](docs/audio.md) | A gain processor, block formats, mixing and custom audio nodes |
| [Custom UI](docs/widgets.md) | Inline inspectors, property dialogs, modeless windows and native Qt bodies |
| [Editor extensions](docs/extensions.md) | Docks, menu commands and undoable graph automation |
| [API reference](docs/api.md) | Public classes, method signatures and host behavior |
| [Install and package plugins](docs/packaging.md) | Drop-in files, wheels, entry points and reload |
| [Compatibility and troubleshooting](docs/editor.md) | Product boundaries, migration and common problems |

## Examples

- [Grayscale effect](examples/grayscale_effect.py): one slider and a video processor.
- [Effect with native Qt UI](examples/effect_with_widget.py): notes dialog and dock.
- [Editor extension](examples/editor_extension.py): audio gain, multiple outputs,
  inline inspector, modeless dialog, dock and command in one file.

Copy an example into the user plugins folder, then reload. Changes to an existing
node's Python class take effect when you reopen the project or recreate the node.

The release version is defined in [version.py](aphelion_sdk/version.py).

## License

Proprietary (`LicenseRef-Proprietary` in `pyproject.toml`).
