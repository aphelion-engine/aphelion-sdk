"""Typed description of a discovered Aphelion Editor install."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EditorInstall:
    """One Aphelion Editor install the SDK can target.

    Attributes:
        root: Install or project directory that owns ``userdata/``.
        executable: Frozen ``AphelionEditor.exe``, or the interpreter for
            source checkouts.
        version: Product version from the host manifest or registry.
        source: How this install was discovered.
        is_frozen: True when ``root`` contains the frozen editor binary.
    """

    root: Path
    executable: Path
    version: str
    source: str
    is_frozen: bool

    @property
    def user_plugin_dir(self) -> Path:
        """Return the writable drop-in plugin folder for this install."""
        from aphelion_sdk.host.constants import PLUGINS_DIR_NAME, USERDATA_DIR_NAME

        return self.root / USERDATA_DIR_NAME / PLUGINS_DIR_NAME
