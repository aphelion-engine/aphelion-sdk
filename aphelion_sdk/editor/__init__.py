"""Aphelion Editor SDK. Product-specific APIs live under this namespace.

The top-level legacy API remains supported. Editor runtime types require an
installed editor (or its src directory on PYTHONPATH).
"""
from importlib import import_module
from aphelion_sdk import _EXPORT_MAP as _LEGACY

_EXPORT_MAP = dict(_LEGACY)
_EXPORT_MAP.update({
    "NodePlugin": ("aphelion_sdk.editor.nodes", "NodePlugin"),
    "NodeSocketType": ("aphelion_sdk.editor.nodes", "NodeSocketType"),
    "NodeValue": ("aphelion_sdk.editor.nodes", "NodeValue"),
    "NodePropertyInputType": ("aphelion_sdk.editor.nodes", "NodePropertyInputType"),
    "AudioNodePlugin": ("aphelion_sdk.editor.audio", "AudioNodePlugin"),
    "AudioEffectPlugin": ("aphelion_sdk.editor.audio", "AudioEffectPlugin"),
    "AudioData": ("aphelion_sdk.editor.audio", "AudioData"),
    "FrameWithAudio": ("aphelion_sdk.editor.audio", "FrameWithAudio"),
    "EditorCommand": ("aphelion_sdk.editor.extensions", "EditorCommand"),
    "EditorExtension": ("aphelion_sdk.editor.extensions", "EditorExtension"),
    "InspectorWidget": ("aphelion_sdk.widgets.inspector", "InspectorWidget"),
})
__all__ = list(_EXPORT_MAP)
PRODUCT_ID = "editor"
API_VERSION = 1


def __getattr__(name):
    if name not in _EXPORT_MAP:
        raise AttributeError(name)
    module, symbol = _EXPORT_MAP[name]
    value = getattr(import_module(module), symbol)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
