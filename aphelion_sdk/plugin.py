"""Media-agnostic plugin metadata shared by video and (future) audio plugins."""

from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from aphelion_sdk.types import ColorRgb

_DEFAULT_PLUGIN_COLOR: ColorRgb = (120, 120, 120)


class Plugin(ABC):
    """Base for every Aphelion plugin, regardless of media type.

    Authors do not subclass this directly. Use ``VideoEffectPlugin`` (or a
    future audio base). ``plugin_*`` attributes are the public identity;
    ``node_*`` copies exist so the editor can register video plugins as nodes.

    Attributes:
        plugin_kind: Discriminator (``"video"``, later ``"audio"``).
        plugin_name: Display name in menus and the node graph.
        plugin_category: Menu group. Defaults to ``"Plugins"``.
        plugin_description: One-line tooltip / search text.
        plugin_color: RGB header color, each channel ``0-255``.
        plugin_author: Optional credit string.
    """

    plugin_kind: ClassVar[str] = "plugin"
    plugin_name: ClassVar[str] = "Untitled Plugin"
    plugin_category: ClassVar[str] = "Plugins"
    plugin_description: ClassVar[str] = ""
    plugin_color: ClassVar[ColorRgb] = _DEFAULT_PLUGIN_COLOR
    plugin_author: ClassVar[str] = "Unknown"
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
