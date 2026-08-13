"""Plugin registration and discovery.

Two ways for a plugin class to reach the host application:

1. ``@aphelion_sdk.register_plugin`` — for modules the editor imports at boot.
2. Installed-package entry points under the ``"aphelion.plugins"`` group.
"""

from __future__ import annotations

from importlib import metadata
from typing import TypeVar

from aphelion_sdk.plugin import Plugin

_PLUGIN_ENTRY_POINT_GROUP: str = "aphelion.plugins"

_registered_plugins: list[type[Plugin]] = []

PluginT = TypeVar("PluginT", bound=Plugin)


def register_plugin(plugin_class: type[PluginT]) -> type[PluginT]:
    """Class decorator that registers a plugin for in-process discovery.

    Usage:
        import aphelion_sdk

        @aphelion_sdk.register_plugin
        class MyEffect(aphelion_sdk.VideoEffectPlugin):
            ...
    """
    if not issubclass(plugin_class, Plugin):
        raise TypeError(
            f"{plugin_class!r} is not an aphelion_sdk.Plugin subclass"
        )
    if plugin_class not in _registered_plugins:
        _registered_plugins.append(plugin_class)
    return plugin_class


def get_registered_plugins() -> tuple[type[Plugin], ...]:
    """Return every plugin class registered so far via ``register_plugin``."""
    return tuple(_registered_plugins)


def discover_installed_plugins() -> tuple[type[Plugin], ...]:
    """Discover plugin classes exposed by installed packages.

    Third-party packages advertise plugins under the ``"aphelion.plugins"``
    entry-point group, each entry pointing at a ``Plugin`` subclass.

    Returns:
        Discovered plugin classes. Entries that fail to load or are not
        ``Plugin`` subclasses are skipped.
    """
    discovered: list[type[Plugin]] = []
    for entry_point in metadata.entry_points(group=_PLUGIN_ENTRY_POINT_GROUP):
        plugin_class = _load_entry_point(entry_point)
        if plugin_class is not None:
            discovered.append(plugin_class)
    return tuple(discovered)


def _load_entry_point(entry_point: metadata.EntryPoint) -> type[Plugin] | None:
    """Load one entry point and return it when it is a ``Plugin`` subclass."""
    try:
        loaded = entry_point.load()
    except (ImportError, AttributeError):
        return None
    if isinstance(loaded, type) and issubclass(loaded, Plugin):
        return loaded
    return None
