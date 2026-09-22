"""Drop into the editor's user plugins directory, then reload plugins."""
import numpy as np
from aphelion_sdk.editor import (
    AudioData, AudioEffectPlugin, DialogWidget, EditorCommand, EditorExtension,
    InspectorWidget, NodePlugin, NodeSocketType, PanelWidget, custom_property,
    number_property, register_plugin,
)


class GainInspector(InspectorWidget):
    widget_title = "Gain controls"

    def build_view(self, host):
        view = host.create_view()
        view.add_number("gain", "Gain", host.get_property_value("gain"), 0, 4,
                        lambda value: host.set_property_value("gain", value))
        view.add_button("reset", "Reset gain", lambda: host.set_property_value("gain", 1.0))
        view.add_button("notes", "Edit notes", lambda: host.open_dialog("notes"))
        return view


class Notes(DialogWidget):
    widget_id = "notes"
    widget_title = "Effect notes"
    widget_show_in_menu = False
    widget_modal = False

    def build_view(self, host):
        view = host.create_view()
        view.add_text("notes", str(host.get_property_value("notes") or ""))
        return view

    def on_accept(self, view, host):
        host.set_property_value("notes", view.get_text("notes"))


@register_plugin
class Gain(AudioEffectPlugin):
    plugin_name = "Example Gain"
    plugin_category = "SDK Examples"
    widgets = (GainInspector, Notes)

    def setup_effect_properties(self):
        self.set_property("gain", number_property(1.0, 0.0, 4.0, label="Gain"))
        self.set_property("notes", custom_property("", widget_id="notes", label="Notes"))

    def process_audio(self, audio, frame_num):
        samples = audio.samples * self.float_value("gain", 1.0)
        return AudioData(samples.astype(np.float32), audio.sample_rate)


@register_plugin
class Channels(NodePlugin):
    """A frame/mask/number node demonstrating arbitrary socket layouts."""
    plugin_name = "Example Channels"
    plugin_category = "SDK Examples"

    def setup_input_outputs(self):
        self.add_input("frame", NodeSocketType.Frame)
        self.add_output("frame", NodeSocketType.Frame)
        self.add_output("mask", NodeSocketType.Mask)
        self.add_output("average", NodeSocketType.Number)

    def evaluate(self, frame_num):
        frame = self.input_frame()
        if frame is None:
            frame = self.blank_frame()
        return {"frame": frame, "mask": frame.mean(axis=2), "average": float(frame.mean())}


def add_gain(host):
    host.create_node("SDK Examples", "Example Gain")


class Tools(PanelWidget):
    widget_title = "Audio tools"
    widget_default_visible = True

    def build_view(self, host):
        view = host.create_view()
        view.add_label("intro", "Create audio nodes from an editor extension.")
        view.add_button("add", "Add Gain", lambda: add_gain(host))
        return view


@register_plugin
class AudioTools(EditorExtension):
    plugin_name = "Example Audio Tools"
    widgets = (Tools,)
    commands = (EditorCommand("add-gain", "Add Gain", add_gain),)
