# Authoring editor nodes

Plugins run inside Aphelion Editor. Import public classes and helpers from
`aphelion_sdk.editor`; use NumPy for data processing and PyQt6 for native UI.
You do not need imports from the editor's `core`, `effects`, `render` or `ui` packages.

## Local development

For a checkout with `aphelion-sdk` and `aphelion-editor` beside each other, activate
the editor's environment. From the parent directory, in PowerShell:

```powershell
python -m pip install -e ./aphelion-sdk -e ./aphelion-styling
$env:PYTHONPATH = (Resolve-Path ./aphelion-editor/src).Path
python -c "from aphelion_sdk.editor import VideoEffectPlugin; print(VideoEffectPlugin)"
```

The environment must also contain the editor's dependencies. Setting `PYTHONPATH`
here makes the editor runtime available to standalone development scripts; normal
editor startup already configures its runtime. Installing only the SDK does not
supply the renderer or make node classes standalone.

Copy your plugin to the user directory opened by **Preferences > Plugins > Open
user folder**, then enable user plugins and reload. See the [first-plugin
walkthrough](../README.md#install-and-run-your-first-plugin).

## Video effects

A complete effect with one parameter:

```python
from aphelion_sdk.editor import VideoEffectPlugin, slider_property, register_plugin


@register_plugin
class Grayscale(VideoEffectPlugin):
    plugin_name = "Tutorial Grayscale"
    plugin_category = "My Plugins"
    plugin_color = (140, 140, 140)

    def setup_effect_properties(self):
        self.set_property("amount", slider_property(100, 0, 100, label="Amount", suffix="%"))

    def process_frame(self, frame, frame_num):
        amount = self.float_value("amount", 100.0) / 100.0
        luma = frame[..., 0] * 0.2126 + frame[..., 1] * 0.7152 + frame[..., 2] * 0.0722
        gray = luma[..., None].repeat(3, axis=2)
        return frame * (1.0 - amount) + gray * amount
```

The default base supplies `frame` input/output sockets, `enabled`, and a `mix`
slider from 0 to 100. It preserves accompanying audio. With no frame input it
returns a blank frame. Implement `process_frame` for your operation and optionally
`setup_effect_properties` for parameters; the default processor passes through.

Frames are NumPy arrays with shape `(height, width, 3)` and dtype `float32`, with
nominal values from 0 to 1. There is no alpha channel. Return the same shape for
ordinary unary effects. Do not modify the input in place: other branches may
share it. For example, use `frame * gain`, not `frame *= gain`.

## Arbitrary sockets and multiple outputs

Use `NodePlugin` for generators, compositors, masks, utilities, logic or mixed-media
nodes. Define sockets in `setup_input_outputs` and calculate outputs in `evaluate`.
The editor calls `setup_effect_properties` after socket setup.

```python
from aphelion_sdk.editor import NodePlugin, NodeSocketType, register_plugin


@register_plugin
class AnalyzeFrame(NodePlugin):
    plugin_name = "Analyze Frame"
    plugin_category = "My Plugins"

    def setup_input_outputs(self):
        self.add_input("image", NodeSocketType.Frame)
        self.add_output("image", NodeSocketType.Frame)
        self.add_output("mask", NodeSocketType.Mask)
        self.add_output("average", NodeSocketType.Number)

    def evaluate(self, frame_num):
        frame = self.input_frame("image")
        if frame is None:
            frame = self.blank_frame()
        mask = frame.mean(axis=2)
        return {"image": frame, "mask": mask, "average": float(mask.mean())}
```

For a single output, return its payload directly. For multiple outputs, return a
dictionary whose keys exactly match output names. You can omit inputs to make a
generator or declare multiple inputs for a compositor. Available socket types are
`Frame`, `Mask`, `Number`, `Color`, `Audio`, `Any`, and legacy `Node`.

Read connections using `input_frame(slot)`, `input_audio(slot)`,
`input_number(slot, default=0.0)` or `get_input_value(slot)`. Missing frame/audio
inputs return None. `input_frame_with_audio(slot="frame")` returns the combined
container when present. Handle missing inputs explicitly.

`NodePlugin` has no automatic bypass/mix controls. For an existing custom
`VideoEffectPlugin`, overriding both `setup_input_outputs` and `evaluate` remains
supported; this bypasses the default unary effect behavior.

## Declare and read properties

```python
from enum import Enum
from aphelion_sdk.editor import NodePlugin, NodeSocketType, choice_property, number_property, register_plugin


class Operation(Enum):
    Multiply = "multiply"
    Add = "add"


@register_plugin
class AdjustNumber(NodePlugin):
    plugin_name = "Adjust Number"
    plugin_category = "My Plugins"

    def setup_input_outputs(self):
        self.add_input("value", NodeSocketType.Number)
        self.add_output("value", NodeSocketType.Number)

    def setup_effect_properties(self):
        self.set_property("amount", number_property(2.0, -100.0, 100.0, label="Amount"))
        self.set_property("operation", choice_property(Operation.Multiply, label="Operation"))
        self.expose_modulation_input("amount")

    def evaluate(self, frame_num):
        value = self.input_number("value")
        amount = self.float_value("amount", 2.0)
        operation = self.enum_value("operation", Operation, Operation.Multiply)
        return value * amount if operation == Operation.Multiply else value + amount
```

`expose_modulation_input("amount")` creates a Number socket named `in_amount`.
A connection there overrides the stored numeric value during evaluation. Property
Drive can also supply numeric overrides. Use the typed readers instead of reading
raw property storage when calculating outputs:

| Reader | Value |
| --- | --- |
| `float_value(key, default)` / `int_value(key, default)` | Numeric parameter |
| `bool_value(key, default)` | Toggle |
| `string_value(key, default="")` | Text |
| `color_value(key, default=(128, 128, 128))` | RGB channels clamped to 0 through 255 |
| `enum_value(key, enum_type, default)` | Enum with fallback |

Builders also support `description`, `group` and `priority` (lower first). See
[property signatures](api.md#property-builders). Keep property keys stable for
saved projects. UI edits should use the widget host setters to participate in undo.

## Identity, evaluation and persistence

| Class attribute | Meaning |
| --- | --- |
| `plugin_name` | Display name and saved node type |
| `plugin_category` | Add Node category; defaults to `Plugins` |
| `plugin_description` | Description/search text |
| `plugin_color` | Header RGB tuple |
| `plugin_author` | Credit |
| `widgets` | Tuple of attached inspector, dialog and panel classes |
| `plugin_product` | Defaults to `editor` |
| `plugin_api_version` | Defaults to `1`; host API compatibility, not package version |
| `is_temporal` | Set True if output depends on frame/time independently of inputs |

For example, a procedural flicker effect should set `is_temporal = True` and use
`frame_num` in its processor. Evaluation can revisit frames out of order after
scrubbing; do not assume sequential calls or exactly one call per frame. Keep UI
work out of evaluation and avoid relying on mutable global state for outputs.

The editor persists declared properties and graph connections. It does not
serialize arbitrary Python instance fields. Renaming a plugin's category/name,
sockets or property keys may break saved graphs. After a code reload, existing
node instances retain their class until recreated or the project is reopened.

Next: [audio processors](audio.md), [custom properties UI](widgets.md), or
[editor-wide extensions](extensions.md).
