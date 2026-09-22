"""Editor video effects with optional arbitrary sockets and evaluation."""
from aphelion_sdk.editor.nodes import NodePlugin
from core.nodes.base import NodeSocketType, NodeValue
from core.nodes.frame_base import FrameEffectNode
from effects.frame_ops import ensure_rgb_f32


class VideoEffectPlugin(NodePlugin):
    """Unary frame effect by default; override sockets/evaluate for other layouts.

    Implement process_frame(frame, frame_num) for a float32 RGB effect with
    enabled/mix controls and automatic audio preservation. Existing plugins
    overriding setup_input_outputs and evaluate remain supported.
    """
    plugin_kind = "video"
    plugin_name = "Untitled Node"
    accepts_u8_frame = False

    def _setup_sockets(self) -> None:
        if type(self).setup_input_outputs is VideoEffectPlugin.setup_input_outputs:
            FrameEffectNode._setup_sockets(self)
        else:
            super()._setup_sockets()

    def setup_input_outputs(self) -> None:
        self.add_input("frame", NodeSocketType.Frame)
        self.add_output("frame", NodeSocketType.Frame)

    def evaluate(self, frame_num: int) -> NodeValue:
        return FrameEffectNode.evaluate(self, frame_num)

    def process_frame(self, frame, frame_num: int):
        """Override to transform an RGB frame without mutating the input."""
        return ensure_rgb_f32(frame)
