"""Single-input, single-output video frame effect plugins."""

from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar

from aphelion_sdk.plugin import Plugin
from aphelion_sdk.types import Frame
from aphelion_sdk.widgets.host import WidgetHost, WidgetView
from core.nodes.frame_base import FrameEffectNode


class VideoEffectPlugin(Plugin, FrameEffectNode):
    """Custom unary video effect: one frame in, one frame out.

    Set the ``plugin_*`` class attributes, then implement
    ``setup_effect_properties`` and ``process_frame``. The host wires frame
    sockets and the standard Enabled/Mix controls.

    Example:
        import aphelion_sdk

        @aphelion_sdk.register_plugin
        class Grayscale(aphelion_sdk.VideoEffectPlugin):
            plugin_name = "Grayscale"
            plugin_category = "Plugins"

            def setup_effect_properties(self) -> None:
                self.set_property(
                    "amount",
                    aphelion_sdk.slider_property(100, 0, 100, label="Amount"),
                )

            def process_frame(self, frame: aphelion_sdk.Frame, _frame_num: int) -> aphelion_sdk.Frame:
                ...
    """

    plugin_kind: ClassVar[str] = "video"
    plugin_name: ClassVar[str] = "Untitled Video Effect"

    @abstractmethod
    def setup_effect_properties(self) -> None:
        """Register this effect's editable properties.

        Call ``self.set_property(key, aphelion_sdk.slider_property(...))``
        (or another property builder) once per parameter.
        """
        raise NotImplementedError

    @abstractmethod
    def process_frame(self, frame: Frame, frame_num: int) -> Frame:
        """Return the processed frame.

        Parameters:
            frame: Source frame, shape ``(height, width, 3)``, ``float32``,
                values nominally in ``[0.0, 1.0]``.
            frame_num: Absolute frame number currently being evaluated.
                Time-independent effects may name this ``_frame_num``.

        Returns:
            The processed frame, same shape and dtype as ``frame``.
        """
        raise NotImplementedError

    def build_property_panel(self, host: WidgetHost) -> WidgetView | None:
        """Optional extra inspector section below generated property rows.

        Parameters:
            host: Editor-provided factory bound to this node instance.

        Returns:
            A view from ``host.create_view()``, or ``None`` for no extra UI.
        """
        del host
        return None

    def build_property_qt_widget(
        self,
        parent: object,
        host: WidgetHost,
    ) -> object | None:
        """Advanced: return a PyQt6 ``QWidget`` for the inspector section.

        Parameters:
            parent: Host ``QWidget`` that should own the result.
            host: Bound to this node instance.

        Returns:
            A ``QWidget``, or ``None`` to use ``build_property_panel``.
        """
        del parent, host
        return None
