"""Aphelion Plugin SDK.

Public, stable surface for custom Aphelion plugins. Authors should
``import aphelion_sdk`` and must never import editor internals
(``core``, ``effects``, ``render``, ``ui``).

Video effects subclass ``VideoEffectPlugin``. Attach UI with
``widgets = (MyDialog, MyPanel)``. Simple widgets use host primitives;
advanced widgets may import PyQt6 and return a ``QWidget`` from
``build_qt_widget`` or ``embed_native``.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from aphelion_sdk.plugin import Plugin
    from aphelion_sdk.properties import (
        PluginProperty,
        choice_property,
        color_property,
        custom_property,
        number_property,
        slider_property,
        text_property,
        toggle_property,
    )
    from aphelion_sdk.registration import (
        clear_registered_plugins,
        discover_installed_plugins,
        get_registered_plugins,
        register_plugin,
    )
    from aphelion_sdk.types import ColorRgb, Frame
    from aphelion_sdk.version import __version__
    from aphelion_sdk.video import VideoEffectPlugin
    from aphelion_sdk.widgets import (
        DialogWidget,
        PanelWidget,
        PluginWidget,
        WidgetContext,
        WidgetHost,
        WidgetView,
        coerce_qt_parent,
        is_qt_widget,
    )

__all__ = [
    "ColorRgb",
    "DialogWidget",
    "Frame",
    "PanelWidget",
    "Plugin",
    "PluginProperty",
    "PluginWidget",
    "VideoEffectPlugin",
    "WidgetContext",
    "WidgetHost",
    "WidgetView",
    "__version__",
    "choice_property",
    "clear_registered_plugins",
    "coerce_qt_parent",
    "color_property",
    "custom_property",
    "discover_editors",
    "discover_installed_plugins",
    "get_registered_plugins",
    "install_plugins_into_editor",
    "locate_editor",
    "is_qt_widget",
    "number_property",
    "register_plugin",
    "slider_property",
    "text_property",
    "toggle_property",
]

_EXPORT_MAP: Final[dict[str, tuple[str, str]]] = {
    "ColorRgb": ("aphelion_sdk.types", "ColorRgb"),
    "DialogWidget": ("aphelion_sdk.widgets.dialog", "DialogWidget"),
    "Frame": ("aphelion_sdk.types", "Frame"),
    "PanelWidget": ("aphelion_sdk.widgets.panel", "PanelWidget"),
    "Plugin": ("aphelion_sdk.plugin", "Plugin"),
    "PluginProperty": ("aphelion_sdk.properties", "PluginProperty"),
    "PluginWidget": ("aphelion_sdk.widgets.base", "PluginWidget"),
    "VideoEffectPlugin": ("aphelion_sdk.video", "VideoEffectPlugin"),
    "WidgetContext": ("aphelion_sdk.widgets.host", "WidgetContext"),
    "WidgetHost": ("aphelion_sdk.widgets.host", "WidgetHost"),
    "WidgetView": ("aphelion_sdk.widgets.host", "WidgetView"),
    "__version__": ("aphelion_sdk.version", "__version__"),
    "choice_property": ("aphelion_sdk.properties", "choice_property"),
    "clear_registered_plugins": (
        "aphelion_sdk.registration",
        "clear_registered_plugins",
    ),
    "coerce_qt_parent": ("aphelion_sdk.widgets.qt", "coerce_qt_parent"),
    "color_property": ("aphelion_sdk.properties", "color_property"),
    "custom_property": ("aphelion_sdk.properties", "custom_property"),
    "discover_editors": ("aphelion_sdk.host.locate", "discover_editors"),
    "discover_installed_plugins": (
        "aphelion_sdk.registration",
        "discover_installed_plugins",
    ),
    "install_plugins_into_editor": (
        "aphelion_sdk.host.install",
        "install_plugins_into_editor",
    ),
    "locate_editor": ("aphelion_sdk.host.locate", "locate_editor"),
    "get_registered_plugins": (
        "aphelion_sdk.registration",
        "get_registered_plugins",
    ),
    "is_qt_widget": ("aphelion_sdk.widgets.qt", "is_qt_widget"),
    "number_property": ("aphelion_sdk.properties", "number_property"),
    "register_plugin": ("aphelion_sdk.registration", "register_plugin"),
    "slider_property": ("aphelion_sdk.properties", "slider_property"),
    "text_property": ("aphelion_sdk.properties", "text_property"),
    "toggle_property": ("aphelion_sdk.properties", "toggle_property"),
}


_EDITOR_EXPORTS = {
    "NodePlugin": "nodes", "NodeSocketType": "nodes", "NodeValue": "nodes",
    "AudioNodePlugin": "audio", "AudioEffectPlugin": "audio",
    "AudioData": "audio", "FrameWithAudio": "audio", "EditorExtension": "extensions",
}
for _name, _module in _EDITOR_EXPORTS.items():
    _EXPORT_MAP[_name] = (f"aphelion_sdk.editor.{_module}", _name)
_EXPORT_MAP["InspectorWidget"] = ("aphelion_sdk.widgets.inspector", "InspectorWidget")
__all__ += [*_EDITOR_EXPORTS, "InspectorWidget"]


def __getattr__(name: str) -> object:
    """Resolve a public SDK symbol on first access.

    Parameters:
        name: Attribute requested on ``aphelion_sdk``.

    Returns:
        The exported object bound to ``name``.

    Exceptions:
        AttributeError: If ``name`` is not part of the public surface.

    Side effects:
        Imports the implementing submodule and caches the attribute.
    """
    location: tuple[str, str] | None = _EXPORT_MAP.get(name)
    if location is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = location
    value: object = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return module attributes including lazy public exports."""
    return sorted(set(globals()) | set(_EXPORT_MAP))
