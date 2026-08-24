"""Media-agnostic plugin metadata shared by video and (future) audio plugins."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar

from aphelion_sdk.types import ColorRgb

if TYPE_CHECKING:
    from aphelion_sdk.widgets.base import PluginWidget

_DEFAULT_PLUGIN_COLOR: ColorRgb = (120, 120, 120)


class Plugin(ABC):
    """Base for every Aphelion plugin, regardless of media type.

    Authors do not subclass this directly. Use ``VideoEffectPlugin``
    (audio bases later). Attach UI with ``widgets = (MyDialog, MyPanel)``;
    those classes subclass ``PluginWidget``, not ``Plugin``.

    Attributes:
        plugin_kind: Discriminator (``"video"``, later ``"audio"``).
        plugin_name: Display name in menus and the node graph.
        plugin_category: Menu group. Defaults to ``"Plugins"``.
        plugin_description: One-line tooltip / search text.
        plugin_color: RGB header color, each channel ``0-255``.
        plugin_author: Optional credit string.
        widgets: ``PluginWidget`` classes owned by this plugin.
    """

    plugin_kind: ClassVar[str] = "plugin"
    plugin_name: ClassVar[str] = "Untitled Plugin"
    plugin_category: ClassVar[str] = "Plugins"
    plugin_description: ClassVar[str] = ""
    plugin_color: ClassVar[ColorRgb] = _DEFAULT_PLUGIN_COLOR
    plugin_author: ClassVar[str] = "Unknown"
    widgets: ClassVar[tuple[type[PluginWidget], ...]] = ()
    node_type: ClassVar[str] = "Untitled Plugin"
    node_category: ClassVar[str] = "Plugins"
    node_description: ClassVar[str] = ""
    node_color: ClassVar[ColorRgb] = _DEFAULT_PLUGIN_COLOR

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Copy ``plugin_*`` identity onto the host node schema fields."""
        super().__init_subclass__(**kwargs)
        cls.node_type = cls.plugin_name
        cls.node_category = cls.plugin_category
        cls.node_description = cls.plugin_description
        cls.node_color = cls.plugin_color
