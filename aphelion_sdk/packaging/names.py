"""Normalize distribution, import, and entry-point names for plugin wheels."""

from __future__ import annotations

import re
from pathlib import Path

from aphelion_sdk.packaging.errors import PluginPackageError

_NON_ALNUM_RE: re.Pattern[str] = re.compile(r"[^a-z0-9]+")
_IDENTIFIER_RE: re.Pattern[str] = re.compile(r"[^0-9A-Za-z_]")
_VERSION_RE: re.Pattern[str] = re.compile(r"^[0-9][0-9A-Za-z._+\-]*$")
_DISTRIBUTION_PREFIX: str = "aphelion-plugin-"


def slugify(value: str) -> str:
    """Return a lowercase hyphenated slug, safe for distribution names.

    Parameters:
        value: Free-form display name or file stem.

    Returns:
        Non-empty slug such as ``grayscale``.

    Exceptions:
        PluginPackageError: If ``value`` has no alphanumeric characters.

    Side effects:
        None.
    """
    slug: str = _NON_ALNUM_RE.sub("-", value.strip().lower()).strip("-")
    if slug == "":
        raise PluginPackageError(f"Cannot derive a package name from {value!r}")
    if slug[0].isdigit():
        return f"plugin-{slug}"
    return slug


def distribution_name(plugin_name: str) -> str:
    """Return the default PyPI-style name for a plugin.

    Parameters:
        plugin_name: Plugin display name (``plugin_name`` class attribute).

    Returns:
        Name like ``aphelion-plugin-grayscale``.

    Exceptions:
        PluginPackageError: If ``plugin_name`` cannot be slugified.

    Side effects:
        None.
    """
    return f"{_DISTRIBUTION_PREFIX}{slugify(plugin_name)}"


def resolve_distribution_name(explicit: str | None, plugin_name: str) -> str:
    """Return a distribution name from an override or the plugin identity.

    Parameters:
        explicit: Optional ``--name`` value from the CLI.
        plugin_name: Fallback plugin display name.

    Returns:
        Normalized distribution name, prefixed with ``aphelion-plugin-``
        unless ``explicit`` already uses that prefix.

    Exceptions:
        PluginPackageError: If the chosen name cannot be slugified.

    Side effects:
        None.
    """
    if explicit is None:
        return distribution_name(plugin_name)
    slug: str = slugify(explicit)
    if slug.startswith(_DISTRIBUTION_PREFIX):
        return slug
    return f"{_DISTRIBUTION_PREFIX}{slug}"


def import_package_name(distribution: str) -> str:
    """Return the importable package name for a distribution.

    Parameters:
        distribution: Hyphenated distribution name.

    Returns:
        Valid module name such as ``aphelion_plugin_grayscale``.

    Exceptions:
        None.

    Side effects:
        None.
    """
    return distribution.replace("-", "_").replace(".", "_")


def module_identifier(source_path: Path) -> str:
    """Return a valid module stem for a plugin source file.

    Parameters:
        source_path: Path to the ``.py`` file being wrapped.

    Returns:
        Lowercase identifier derived from the file stem.

    Exceptions:
        PluginPackageError: If the stem has no usable characters.

    Side effects:
        None.
    """
    raw: str = _IDENTIFIER_RE.sub("_", source_path.stem).strip("_")
    if raw == "":
        raise PluginPackageError(
            f"Cannot derive a module name from {source_path.name!r}"
        )
    lowered: str = raw.lower()
    if lowered[0].isdigit():
        return f"plugin_{lowered}"
    return lowered


def entry_point_name(plugin_name: str, class_name: str, used: set[str]) -> str:
    """Return a unique entry-point name for one plugin class.

    Parameters:
        plugin_name: Plugin display name.
        class_name: Python class name, used when the slug collides.
        used: Names already assigned in this package.

    Returns:
        Unique ``[a-z0-9_]+`` entry-point name.

    Exceptions:
        PluginPackageError: If ``plugin_name`` cannot be slugified.

    Side effects:
        Adds the chosen name to ``used``.
    """
    base: str = slugify(plugin_name).replace("-", "_")
    candidate: str = base
    if candidate in used:
        candidate = f"{base}_{slugify(class_name).replace('-', '_')}"
    suffix: int = 2
    unique: str = candidate
    while unique in used:
        unique = f"{candidate}_{suffix}"
        suffix += 1
    used.add(unique)
    return unique


def validate_version(version: str) -> str:
    """Return ``version`` when it is a plausible PEP 440 string.

    Parameters:
        version: Caller-supplied package version.

    Returns:
        Stripped version string.

    Exceptions:
        PluginPackageError: If ``version`` is empty or illegal.

    Side effects:
        None.
    """
    stripped: str = version.strip()
    if _VERSION_RE.fullmatch(stripped) is None:
        raise PluginPackageError(f"Invalid package version: {version!r}")
    return stripped
