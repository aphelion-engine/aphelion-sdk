"""Editor graph extension bases; all supported socket types are public."""
from aphelion_sdk.plugin import Plugin
from aphelion_sdk.widgets.host import WidgetHost, WidgetView
from core.nodes.base import NodeSocketType, NodeValue, NodePropertyInputType
from core.nodes.frame_base import FrameNode


class NodePlugin(Plugin, FrameNode):
    """Arbitrary source, effect, compositor, mask, logic or multi-output node.

    Implement setup_input_outputs and evaluate. Properties are initialized once
    after sockets. Evaluation uses the editor's caching and serialization path.
    """
    plugin_kind = "node"
    plugin_product = "editor"

    def _setup_sockets(self) -> None:
        self.setup_input_outputs()
        self.setup_effect_properties()

    def setup_input_outputs(self) -> None:
        """Declare inputs and outputs with add_input/add_output."""

    def setup_effect_properties(self) -> None:
        """Declare persisted parameters with set_property."""

    def build_property_panel(self, host: WidgetHost) -> WidgetView | None:
        return None

    def build_property_qt_widget(self, parent: object, host: WidgetHost) -> object | None:
        return None
