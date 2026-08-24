"""Copy plugin sources into the located editor's user plugin folder."""

from __future__ import annotations

import shutil
from pathlib import Path

from aphelion_sdk.host.errors import EditorHostError
from aphelion_sdk.host.locate import locate_editor
from aphelion_sdk.host.models import EditorInstall
from aphelion_sdk.packaging.discovery import plugin_source_files
from aphelion_sdk.packaging.errors import PluginPackageError


def install_plugins_into_editor(
    source: Path,
    *,
    editor: EditorInstall | None = None,
) -> tuple[Path, ...]:
    """Copy plugin modules into the editor's ``userdata/plugins`` folder.

    Parameters:
        source: A ``.py`` file or a directory of plugin modules.
        editor: Install to target. Defaults to ``locate_editor()``.

    Returns:
        Destination paths written on disk.

    Exceptions:
        EditorHostError: If the editor cannot be found or copy fails.
        PluginPackageError: If ``source`` is not a valid plugin path.

    Side effects:
        Creates the user plugin directory and overwrites same-named files.
    """
    target: EditorInstall = editor if editor is not None else locate_editor()
    files: tuple[Path, ...] = plugin_source_files(source)
    destination_dir: Path = target.user_plugin_dir
    destination_dir.mkdir(parents=True, exist_ok=True)
    return _copy_plugin_files(files, destination_dir)


def _copy_plugin_files(files: tuple[Path, ...], destination_dir: Path) -> tuple[Path, ...]:
    """Copy each plugin file into ``destination_dir``."""
    written: list[Path] = []
    for file_path in files:
        dest: Path = destination_dir / file_path.name
        try:
            shutil.copy2(file_path, dest)
        except OSError as exc:
            raise EditorHostError(
                f"Failed to install {file_path} -> {dest}: {exc}"
            ) from exc
        written.append(dest)
    return tuple(written)
