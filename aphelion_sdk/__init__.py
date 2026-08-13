"""Aphelion Plugin SDK.

Public, stable surface for custom Aphelion plugins. Authors should only
``import aphelion_sdk`` — never ``core``, ``effects``, ``render``, or ``ui``.

Video effects subclass ``VideoEffectPlugin`` today. Audio plugin bases will
land under this same package later; they are not available yet.

This SDK runs inside the Aphelion Editor process and depends on it.
"""

from __future__ import annotations

from aphelion_sdk.plugin import Plugin
from aphelion_sdk.properties import (
    PluginProperty,
    choice_property,
    color_property,
    number_property,
    slider_property,
    text_property,
    toggle_property,
)
from aphelion_sdk.registration import (
    discover_installed_plugins,
    get_registered_plugins,
    register_plugin,
)
from aphelion_sdk.types import ColorRgb, Frame
from aphelion_sdk.version import __version__
from aphelion_sdk.video import VideoEffectPlugin

__all__ = [
    "ColorRgb",
    "Frame",
    "Plugin",
    "PluginProperty",
    "VideoEffectPlugin",
    "__version__",
    "choice_property",
    "color_property",
    "discover_installed_plugins",
    "get_registered_plugins",
    "number_property",
    "register_plugin",
    "slider_property",
    "text_property",
    "toggle_property",
]
