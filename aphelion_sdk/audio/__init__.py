"""Compatibility exports; new plugins should use aphelion_sdk.editor.audio."""
from aphelion_sdk.editor.audio import AudioData, FrameWithAudio, AudioNodePlugin, AudioEffectPlugin
__all__ = ["AudioData", "FrameWithAudio", "AudioNodePlugin", "AudioEffectPlugin"]
