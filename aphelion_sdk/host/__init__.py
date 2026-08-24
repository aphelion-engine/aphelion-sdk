"""Locate the installed Aphelion Editor and install drop-in plugins into it."""

from __future__ import annotations

from aphelion_sdk.host.errors import EditorHostError
from aphelion_sdk.host.install import install_plugins_into_editor
from aphelion_sdk.host.locate import discover_editors, locate_editor
from aphelion_sdk.host.models import EditorInstall

__all__ = [
    "EditorHostError",
    "EditorInstall",
    "discover_editors",
    "install_plugins_into_editor",
    "locate_editor",
]
