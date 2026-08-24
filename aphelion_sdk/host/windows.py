"""Windows registry and default-folder probes for the editor."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from aphelion_sdk.host.constants import (
    DEFAULT_MACHINE_INSTALL,
    DEFAULT_USER_INSTALL,
    REGISTRY_KEY,
    REGISTRY_VALUE_PATH,
)


def registry_install_roots() -> tuple[Path, ...]:
    """Return install roots recorded under ``Software\\Aphelion\\Editor``.

    Returns:
        Unique existing directory paths from HKCU then HKLM.

    Side effects:
        Reads the Windows registry when ``winreg`` is available.
    """
    try:
        import winreg
    except ImportError:
        return ()
    roots: list[Path] = []
    hives: tuple[int, ...] = (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE)
    for hive in hives:
        path = _registry_path(winreg, hive)
        if path is not None and path not in roots:
            roots.append(path)
    return tuple(roots)


def default_windows_roots() -> tuple[Path, ...]:
    """Return conventional per-user and per-machine install folders."""
    found: list[Path] = []
    local_app: str = os.environ.get("LOCALAPPDATA", "")
    program_files: str = os.environ.get("ProgramFiles", r"C:\Program Files")
    candidates: tuple[Path, ...] = (
        Path(local_app) / DEFAULT_USER_INSTALL if local_app else Path(),
        Path(program_files) / DEFAULT_MACHINE_INSTALL,
    )
    for candidate in candidates:
        if candidate != Path() and candidate.is_dir() and candidate not in found:
            found.append(candidate)
    return tuple(found)


def path_env_roots() -> Iterator[Path]:
    """Yield directories on ``PATH`` that may contain the editor."""
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if entry.strip() == "":
            continue
        yield Path(entry)


def _registry_path(winreg: object, hive: int) -> Path | None:
    """Read ``InstallPath`` from one registry hive."""
    open_key = getattr(winreg, "OpenKey")
    query_value = getattr(winreg, "QueryValueEx")
    error_type = getattr(winreg, "error")
    try:
        key = open_key(hive, REGISTRY_KEY)
        try:
            value, _kind = query_value(key, REGISTRY_VALUE_PATH)
        finally:
            getattr(winreg, "CloseKey")(key)
    except OSError:
        return None
    except error_type:
        return None
    if not isinstance(value, str) or value.strip() == "":
        return None
    path: Path = Path(value)
    return path if path.is_dir() else None
