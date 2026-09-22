"""Generate a PEP 517 project tree for discovered plugin modules."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from aphelion_sdk.packaging.discovery import DiscoveredPlugin
from aphelion_sdk.packaging.names import (
    entry_point_name,
    import_package_name,
    resolve_distribution_name,
    validate_version,
)
from aphelion_sdk.version import DISTRIBUTION_NAME, __version__

_ENTRY_POINT_GROUP: str = "aphelion.editor.plugins"
_DEFAULT_DESCRIPTION: str = "Aphelion editor plugin."
_UNKNOWN_AUTHOR: str = "Unknown"


@dataclass(frozen=True, slots=True)
class PackageSpec:
    """Identity of a generated plugin distribution.

    Attributes:
        distribution_name: PEP 503 name written to ``pyproject.toml``.
        import_package: Importable package directory name.
        version: PEP 440 version.
        description: Short package summary.
        author: Optional author credit; omitted from metadata when empty.
        sdk_requirement: Dependency pin on the Aphelion Plugin SDK.
        entry_points: Mapping of entry-point name to ``module:Class``.
    """

    distribution_name: str
    import_package: str
    version: str
    description: str
    author: str
    sdk_requirement: str
    entry_points: tuple[tuple[str, str], ...]


def make_package_spec(
    plugins: tuple[DiscoveredPlugin, ...],
    *,
    distribution_name: str | None = None,
    version: str = "0.1.0",
    author: str | None = None,
    description: str | None = None,
) -> PackageSpec:
    """Build a ``PackageSpec`` from discovered plugins and CLI overrides.

    Parameters:
        plugins: Plugin classes to advertise as entry points. Must be non-empty.
        distribution_name: Optional explicit distribution name.
        version: Package version string.
        author: Optional author override.
        description: Optional summary override.

    Returns:
        Fully resolved package identity and entry points.

    Exceptions:
        PluginPackageError: If names or ``version`` are invalid.

    Side effects:
        None.
    """
    lead: DiscoveredPlugin = plugins[0]
    dist_name: str = resolve_distribution_name(distribution_name, lead.plugin_name)
    import_name: str = import_package_name(dist_name)
    return PackageSpec(
        distribution_name=dist_name,
        import_package=import_name,
        version=validate_version(version),
        description=_resolve_description(description, lead),
        author=_resolve_author(author, plugins),
        sdk_requirement=f"{DISTRIBUTION_NAME}>={__version__}",
        entry_points=_entry_points(plugins, import_name),
    )


def materialize_project(
    plugins: tuple[DiscoveredPlugin, ...],
    staging_dir: Path,
    spec: PackageSpec,
) -> Path:
    """Write a src-layout setuptools project into ``staging_dir``.

    Parameters:
        plugins: Plugin classes whose source files will be copied.
        staging_dir: Empty directory that will hold ``pyproject.toml`` and ``src/``.
        spec: Package identity used for names and metadata.

    Returns:
        ``staging_dir`` after the tree is written.

    Exceptions:
        OSError: If a source file cannot be copied.

    Side effects:
        Creates directories and files under ``staging_dir``.
    """
    package_dir: Path = staging_dir / "src" / spec.import_package
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text(_package_init(spec), encoding="utf-8")
    _copy_plugin_modules(plugins, package_dir)
    (staging_dir / "pyproject.toml").write_text(
        render_pyproject(spec),
        encoding="utf-8",
    )
    return staging_dir


def render_pyproject(spec: PackageSpec) -> str:
    """Return ``pyproject.toml`` contents for ``spec``.

    Parameters:
        spec: Package identity and entry points.

    Returns:
        TOML text for a setuptools src-layout project.

    Exceptions:
        None.

    Side effects:
        None.
    """
    lines: list[str] = [
        *_build_system_lines(),
        "",
        *_project_table_lines(spec),
        "",
        *_entry_point_lines(spec),
        "",
        "[tool.setuptools.packages.find]",
        'where = ["src"]',
        "",
    ]
    return "\n".join(lines)


def _resolve_description(explicit: str | None, lead: DiscoveredPlugin) -> str:
    """Return a package summary from an override or the lead plugin."""
    if explicit is not None and explicit.strip() != "":
        return explicit.strip()
    if lead.plugin_description.strip() != "":
        return lead.plugin_description.strip()
    return _DEFAULT_DESCRIPTION


def _resolve_author(
    explicit: str | None,
    plugins: tuple[DiscoveredPlugin, ...],
) -> str:
    """Return an author string, preferring an explicit override."""
    if explicit is not None and explicit.strip() != "":
        return explicit.strip()
    for plugin in plugins:
        if plugin.plugin_author not in ("", _UNKNOWN_AUTHOR):
            return plugin.plugin_author
    return ""


def _entry_points(
    plugins: tuple[DiscoveredPlugin, ...],
    import_package: str,
) -> tuple[tuple[str, str], ...]:
    """Return ``(name, target)`` pairs for the ``aphelion.editor.plugins`` group."""
    used: set[str] = set()
    pairs: list[tuple[str, str]] = []
    for plugin in plugins:
        name: str = entry_point_name(plugin.plugin_name, plugin.class_name, used)
        target: str = f"{import_package}.{plugin.module_name}:{plugin.class_name}"
        pairs.append((name, target))
    return tuple(pairs)


def _copy_plugin_modules(
    plugins: tuple[DiscoveredPlugin, ...],
    package_dir: Path,
) -> None:
    """Copy each unique plugin source into ``package_dir`` once."""
    copied: set[Path] = set()
    for plugin in plugins:
        if plugin.source_path in copied:
            continue
        shutil.copy2(plugin.source_path, package_dir / f"{plugin.module_name}.py")
        copied.add(plugin.source_path)


def _package_init(spec: PackageSpec) -> str:
    """Return ``__init__.py`` contents for the generated import package."""
    return (
        f'"""Generated Aphelion plugin package: {spec.distribution_name}."""\n'
        "from __future__ import annotations\n"
    )


def _build_system_lines() -> list[str]:
    """Return the ``[build-system]`` table."""
    return [
        "[build-system]",
        'requires = ["setuptools>=68.0", "wheel"]',
        'build-backend = "setuptools.build_meta"',
    ]


def _project_table_lines(spec: PackageSpec) -> list[str]:
    """Return the ``[project]`` table, including optional author."""
    lines: list[str] = [
        "[project]",
        f"name = {_toml_string(spec.distribution_name)}",
        f"version = {_toml_string(spec.version)}",
        f"description = {_toml_string(spec.description)}",
        'requires-python = ">=3.11"',
        "dependencies = [",
        f"    {_toml_string(spec.sdk_requirement)},",
        "]",
    ]
    if spec.author != "":
        lines.append(f"authors = [{{ name = {_toml_string(spec.author)} }}]")
    return lines


def _entry_point_lines(spec: PackageSpec) -> list[str]:
    """Return the ``aphelion.editor.plugins`` entry-point table."""
    lines: list[str] = [f'[project.entry-points."{_ENTRY_POINT_GROUP}"]']
    for name, target in spec.entry_points:
        lines.append(f"{name} = {_toml_string(target)}")
    return lines


def _toml_string(value: str) -> str:
    """Return ``value`` as a double-quoted TOML string."""
    escaped: str = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
