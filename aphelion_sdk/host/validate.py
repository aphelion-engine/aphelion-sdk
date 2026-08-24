"""Decide whether a directory is a usable Aphelion Editor install."""

from __future__ import annotations

import json
from pathlib import Path

from aphelion_sdk.host.constants import (
    EDITOR_EXE_NAME,
    HOST_MANIFEST_NAME,
    SOURCE_ENTRY_NAME,
)
from aphelion_sdk.host.models import EditorInstall


def install_from_root(root: Path, *, source: str) -> EditorInstall | None:
    """Return an ``EditorInstall`` when ``root`` looks like the editor.

    Parameters:
        root: Candidate install or project directory.
        source: Discovery origin recorded on the result.

    Returns:
        A validated install, or ``None`` when ``root`` is not the editor.

    Side effects:
        May read ``aphelion-host.json`` from disk.
    """
    resolved: Path = root.expanduser().resolve()
    if not resolved.is_dir():
        return None
    frozen_exe: Path = resolved / EDITOR_EXE_NAME
    source_entry: Path = resolved / SOURCE_ENTRY_NAME
    if frozen_exe.is_file():
        return _frozen_install(resolved, frozen_exe, source)
    if source_entry.is_file():
        return _source_install(resolved, source)
    return None


def _frozen_install(root: Path, executable: Path, source: str) -> EditorInstall:
    """Build a record for a frozen editor tree."""
    return EditorInstall(
        root=root,
        executable=executable,
        version=_manifest_version(root),
        source=source,
        is_frozen=True,
    )


def _source_install(root: Path, source: str) -> EditorInstall:
    """Build a record for an editor source checkout."""
    return EditorInstall(
        root=root,
        executable=root / SOURCE_ENTRY_NAME,
        version=_manifest_version(root),
        source=source,
        is_frozen=False,
    )


def _manifest_version(root: Path) -> str:
    """Return the version from the host manifest, or empty."""
    path: Path = root / HOST_MANIFEST_NAME
    if not path.is_file():
        return ""
    try:
        loaded: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(loaded, dict):
        return ""
    version: object = loaded.get("version")
    return version if isinstance(version, str) else ""
