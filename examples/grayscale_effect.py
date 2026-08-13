"""Example video plugin: a single-slider grayscale effect.

Drop this file in ``plugins/`` or ``userdata/plugins/``, or use it as a
template. Authors only import ``aphelion_sdk``.
"""

from __future__ import annotations

import aphelion_sdk


@aphelion_sdk.register_plugin
class GrayscaleEffect(aphelion_sdk.VideoEffectPlugin):
    """Desaturates a frame by a user-controlled amount."""

    plugin_name = "Grayscale"
    plugin_category = "Plugins"
    plugin_description = "Blend a frame toward grayscale."
    plugin_color = (140, 140, 140)

    def setup_effect_properties(self) -> None:
        """Register the Amount slider control."""
        self.set_property(
            "amount",
            aphelion_sdk.slider_property(
                100,
                0,
                100,
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
        """Blend the frame toward its luma-derived grayscale value."""
        amount: float = self.float_value("amount", 100.0) / 100.0
        luma = (
            frame[..., 0] * 0.2126 + frame[..., 1] * 0.7152 + frame[..., 2] * 0.0722
        )
        gray = luma[..., None].repeat(3, axis=2)
        return frame * (1.0 - amount) + gray * amount
