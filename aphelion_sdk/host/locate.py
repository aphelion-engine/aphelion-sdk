"""Find the Aphelion Editor install this SDK should target."""

from __future__ import annotations

import os
from pathlib import Path

from aphelion_sdk.host.constants import ENV_EDITOR_HOME
from aphelion_sdk.host.errors import EditorHostError
from aphelion_sdk.host.models import EditorInstall
from aphelion_sdk.host.validate import install_from_root
from aphelion_sdk.host.windows import (
    default_windows_roots,
    path_env_roots,
    registry_install_roots,
)
from aphelion_sdk.version import __version__


def locate_editor() -> EditorInstall:
    """Return the preferred Aphelion Editor install on this machine.

    Search order: ``APHELION_EDITOR_HOME``, Windows registry, ``PATH``,
    default install folders, then a sibling source checkout.

    Returns:
        The selected install.

    Exceptions:
        EditorHostError: If no valid editor install can be found.

    Side effects:
        Reads environment variables, the registry, and the filesystem.
    """
    installs: tuple[EditorInstall, ...] = discover_editors()
    if not installs:
        raise EditorHostError(
            "Could not find Aphelion Editor. Install the editor, or set "
            f"{ENV_EDITOR_HOME} to its install folder."
        )
    return _prefer_install(installs)


def discover_editors() -> tuple[EditorInstall, ...]:
    """Return every valid editor install discovered on this machine."""
    found: list[EditorInstall] = []
    seen: set[Path] = set()
    for root, origin in _candidate_roots():
        install = install_from_root(root, source=origin)
        if install is None or install.root in seen:
            continue
        seen.add(install.root)
        found.append(install)
    return tuple(found)


def _candidate_roots() -> tuple[tuple[Path, str], ...]:
    """Return ``(path, source)`` pairs in preference order."""
    pairs: list[tuple[Path, str]] = []
    env_home: str = os.environ.get(ENV_EDITOR_HOME, "").strip()
    if env_home:
        pairs.append((Path(env_home), "environment"))
    for root in registry_install_roots():
        pairs.append((root, "registry"))
    for root in path_env_roots():
        pairs.append((root, "path"))
    for root in default_windows_roots():
        pairs.append((root, "default"))
    sibling: Path = Path(__file__).resolve().parents[3] / "aphelion-editor"
    pairs.append((sibling, "sibling"))
    return tuple(pairs)


def _prefer_install(installs: tuple[EditorInstall, ...]) -> EditorInstall:
    """Pick the install whose version matches this SDK, else the first."""
    matches: tuple[EditorInstall, ...] = tuple(
        item for item in installs if item.version == __version__
    )
    if matches:
        return matches[0]
    return installs[0]
