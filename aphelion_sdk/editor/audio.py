"""Editor audio plugin contracts and host-compatible media containers."""
from aphelion_sdk.editor.nodes import NodePlugin, NodeSocketType
from aphelion_sdk.properties import number_property, toggle_property
from core.audio import AudioData, FrameWithAudio
import numpy as np


class AudioNodePlugin(NodePlugin):
    """Arbitrary audio source, routing, analysis or multi-input processing node."""
    plugin_kind = "audio"


class AudioEffectPlugin(AudioNodePlugin):
    """Block processor. Override process_audio; never mutate input samples.

    Blocks correspond to timeline frames. Return the same sample rate and shape;
    use AudioNodePlugin for resampling, generators or different socket layouts.
    """
    def setup_input_outputs(self) -> None:
        self.add_input("audio", NodeSocketType.Audio)
        self.add_output("audio", NodeSocketType.Audio)
        self.set_property("enabled", toggle_property(True, label="Enabled", group="Processing", priority=0))
        self.set_property("mix", number_property(1.0, 0.0, 1.0, label="Mix", group="Processing", priority=1))

    def evaluate(self, frame_num: int) -> AudioData | None:
        source = self.input_audio()
        if source is None or not self.bool_value("enabled", True):
            return source
        mix = max(0.0, min(1.0, self.float_value("mix", 1.0)))
        if mix == 0:
            return source
        result = self.process_audio(source, frame_num)
        if not isinstance(result, AudioData):
            raise TypeError("process_audio must return AudioData")
        if result.sample_rate != source.sample_rate or result.samples.shape != source.samples.shape:
            raise ValueError("AudioEffectPlugin must preserve sample rate and sample shape")
        if mix == 1:
            return result
        return AudioData(np.asarray(source.samples * (1 - mix) + result.samples * mix, dtype=np.float32), source.sample_rate)

    def process_audio(self, audio: AudioData, frame_num: int) -> AudioData:
        return audio
