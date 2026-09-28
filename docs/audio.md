# Audio plugins

Import audio APIs from `aphelion_sdk.editor` or `aphelion_sdk.editor.audio`.
Use `AudioEffectPlugin` for a processor that preserves the input block's shape and
sample rate. Use `AudioNodePlugin` for custom sources, routing, analysis, multiple
inputs or resampling.

## A complete gain processor

Save as `gain.py`, install it as a [drop-in plugin](packaging.md#drop-in-files), then
add **My Plugins > Tutorial Gain**. Connect an audio source to `audio` and route its
output into your audio graph.

```python
import numpy as np
from aphelion_sdk.editor import AudioData, AudioEffectPlugin, number_property, register_plugin


@register_plugin
class Gain(AudioEffectPlugin):
    plugin_name = "Tutorial Gain"
    plugin_category = "My Plugins"

    def setup_effect_properties(self):
        self.set_property("gain", number_property(1.0, 0.0, 4.0, label="Gain"))

    def process_audio(self, audio, frame_num):
        samples = np.clip(audio.samples * self.float_value("gain", 1.0), -1.0, 1.0)
        return AudioData(samples.astype(np.float32), audio.sample_rate)
```

The base adds an `audio` input and output, `enabled`, and `mix` from 0 to 1.
With no input, evaluation returns None. Disabled processing or zero mix returns the
source unchanged. Partial mix blends dry input with your processed block. Do not
redeclare `enabled` or `mix` unless you intend to replace those controls.

`process_audio` must return `AudioData` with the same sample rate and sample shape
as its input. An invalid return type raises TypeError; a changed shape or sample
rate raises ValueError. The base does not automatically clip samples; the example
chooses to clip its gain output.

## Audio data

| API | Meaning |
| --- | --- |
| `AudioData(samples, sample_rate)` | float32 NumPy array and positive sample rate in Hz |
| `samples.shape == (N,)` | Mono |
| `samples.shape == (N, channels)` | Multichannel |
| `audio.num_samples` / `audio.num_channels` | Block dimensions |
| `audio.duration` | Number of samples divided by sample rate |
| `AudioData.silence(duration, sample_rate=48000, channels=1)` | Construct a silent block |
| `FrameWithAudio(frame, audio)` | Video plus optional synchronized audio |

Samples have a nominal range of -1 to 1. The container validates dtype, dimensions
and sample rate; it does not make the NumPy buffer read-only. Always allocate new
output samples instead of mutating upstream arrays.

Audio processing is driven by timeline frame evaluation, not a realtime device
callback. Blocks need not have one fixed length. Preview seeks and repeated
requests mean a plugin cannot assume callbacks arrive sequentially. The SDK does
not provide a dedicated streaming-DSP state/reset lifecycle.

## Custom routing node

This node returns separate audio and numeric outputs:

```python
import numpy as np
from aphelion_sdk.editor import AudioNodePlugin, NodeSocketType, register_plugin


@register_plugin
class AudioMeter(AudioNodePlugin):
    plugin_name = "Audio Meter"
    plugin_category = "My Plugins"

    def setup_input_outputs(self):
        self.add_input("audio", NodeSocketType.Audio)
        self.add_output("audio", NodeSocketType.Audio)
        self.add_output("peak", NodeSocketType.Number)

    def evaluate(self, frame_num):
        audio = self.input_audio("audio")
        peak = 0.0
        if audio is not None and audio.num_samples:
            peak = float(np.max(np.abs(audio.samples)))
        return {"audio": audio, "peak": peak}
```

`AudioNodePlugin` does not supply sockets, enabled/mix controls or shape validation.
Its `input_audio` helper can also extract audio from a `FrameWithAudio` input.
Generators should declare their output sockets and construct `AudioData` themselves;
resamplers must return the new sample rate with their output buffer.

To add gain controls or a custom audio editor in Properties, follow
[custom UI](widgets.md). The [combined example](../examples/editor_extension.py)
includes an audio processor with an inspector and notes window.
