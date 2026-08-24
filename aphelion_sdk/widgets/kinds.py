"""Widget surface kinds attached to a plugin. These are not plugin kinds."""

from __future__ import annotations

from typing import Final, Literal

WIDGET_KIND_PANEL: Final[str] = "panel"
WIDGET_KIND_DIALOG: Final[str] = "dialog"

DockAreaName = Literal["left", "right", "bottom", "top"]

DEFAULT_DOCK_AREA: Final[DockAreaName] = "right"
DEFAULT_DIALOG_WIDTH_PX: Final[int] = 420
DEFAULT_DIALOG_HEIGHT_PX: Final[int] = 320
