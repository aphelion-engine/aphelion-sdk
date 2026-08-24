"""Shared names used to locate an Aphelion Editor install."""

from __future__ import annotations

from typing import Final

ENV_EDITOR_HOME: Final[str] = "APHELION_EDITOR_HOME"
HOST_MANIFEST_NAME: Final[str] = "aphelion-host.json"
EDITOR_EXE_NAME: Final[str] = "AphelionEditor.exe"
SOURCE_ENTRY_NAME: Final[str] = "main.py"
REGISTRY_KEY: Final[str] = r"Software\Aphelion\Editor"
REGISTRY_VALUE_PATH: Final[str] = "InstallPath"
REGISTRY_VALUE_EXE: Final[str] = "Executable"
USERDATA_DIR_NAME: Final[str] = "userdata"
PLUGINS_DIR_NAME: Final[str] = "plugins"
DEFAULT_USER_INSTALL: Final[str] = r"Aphelion\Aphelion Editor"
DEFAULT_MACHINE_INSTALL: Final[str] = r"Aphelion\Aphelion Editor"
