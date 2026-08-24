"""Build pip wheels for Aphelion plugins."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from aphelion_sdk.packaging.discovery import DiscoveredPlugin, discover_plugins
from aphelion_sdk.packaging.errors import PluginPackageError
from aphelion_sdk.packaging.names import validate_version
from aphelion_sdk.packaging.project import PackageSpec, make_package_spec, materialize_project

BuildMode = Literal["generated", "project"]


@dataclass(frozen=True, slots=True)
class PackageBuildResult:
    """Outcome of a successful plugin (or project) pip build.

    Attributes:
        artifacts: Newly written wheel paths.
        distribution_name: Name recorded in package metadata.
        version: Version recorded in package metadata.
        plugins: Plugin classes packaged when generating a project.
        mode: ``generated`` wraps plugin sources; ``project`` builds in place.
    """

    artifacts: tuple[Path, ...]
    distribution_name: str
    version: str
    plugins: tuple[DiscoveredPlugin, ...]
    mode: BuildMode


def is_python_project(path: Path) -> bool:
    """Return True when ``path`` is a directory with ``pyproject.toml``.

    Parameters:
        path: Candidate project root.

    Returns:
        True if ``path`` is an existing directory containing ``pyproject.toml``.

    Exceptions:
        None.

    Side effects:
        None.
    """
    return path.is_dir() and (path / "pyproject.toml").is_file()


def build_plugin_package(
    source: Path,
    output_dir: Path,
    *,
    distribution_name: str | None = None,
    version: str = "0.1.0",
    author: str | None = None,
    description: str | None = None,
) -> PackageBuildResult:
    """Build a pip wheel from plugin source or an existing project.

    Parameters:
        source: Plugin ``.py`` file, plugin directory, or a project root
            that already contains ``pyproject.toml``.
        output_dir: Directory that receives the wheel.
        distribution_name: Optional distribution name for generated packages.
        version: Package version for generated packages.
        author: Optional author for generated packages.
        description: Optional summary for generated packages.

    Returns:
        Paths and metadata for the built artifacts.

    Exceptions:
        PluginPackageError: If discovery, project generation, or the
            PEP 517 build fails.

    Side effects:
        Creates ``output_dir``. Writes a wheel. Generated builds use a
        temporary staging tree that is deleted afterwards.
    """
    resolved: Path = source.expanduser().resolve()
    destination: Path = output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if is_python_project(resolved):
        return _build_existing_project(resolved, destination)
    return _build_generated_package(
        resolved,
        destination,
        distribution_name=distribution_name,
        version=version,
        author=author,
        description=description,
    )


def build_distributions(project_dir: Path, output_dir: Path) -> tuple[Path, ...]:
    """Build a wheel with ``python -m pip wheel``.

    Parameters:
        project_dir: Directory containing ``pyproject.toml``.
        output_dir: Directory that receives the built wheel.

    Returns:
        Artifact paths created by this invocation.

    Exceptions:
        PluginPackageError: If pip is missing or the build fails.

    Side effects:
        Spawns pip's isolated PEP 517 build. Writes a wheel into ``output_dir``.
    """
    destination: Path = output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    before: set[Path] = set(destination.iterdir())
    _run_pip_wheel(project_dir.resolve(), destination)
    created: list[Path] = sorted(
        path for path in (set(destination.iterdir()) - before) if path.suffix == ".whl"
    )
    if not created:
        raise PluginPackageError(f"Build produced no wheel in {destination}")
    return tuple(created)


def _build_generated_package(
    source: Path,
    output_dir: Path,
    *,
    distribution_name: str | None,
    version: str,
    author: str | None,
    description: str | None,
) -> PackageBuildResult:
    """Discover plugins, materialize a project, and build it."""
    plugins: tuple[DiscoveredPlugin, ...] = discover_plugins(source)
    spec: PackageSpec = make_package_spec(
        plugins,
        distribution_name=distribution_name,
        version=version,
        author=author,
        description=description,
    )
    with TemporaryDirectory(prefix="aphelion-plugin-build-") as tmp:
        staging: Path = Path(tmp)
        materialize_project(plugins, staging, spec)
        artifacts: tuple[Path, ...] = build_distributions(staging, output_dir)
    return PackageBuildResult(
        artifacts=artifacts,
        distribution_name=spec.distribution_name,
        version=spec.version,
        plugins=plugins,
        mode="generated",
    )


def _build_existing_project(
    project_dir: Path,
    output_dir: Path,
) -> PackageBuildResult:
    """Build an already-packaged Python project in place."""
    name, version = _read_project_identity(project_dir)
    artifacts: tuple[Path, ...] = build_distributions(project_dir, output_dir)
    return PackageBuildResult(
        artifacts=artifacts,
        distribution_name=name,
        version=version,
        plugins=(),
        mode="project",
    )


def _read_project_identity(project_dir: Path) -> tuple[str, str]:
    """Return ``(name, version)`` from ``pyproject.toml``."""
    path: Path = project_dir / "pyproject.toml"
    try:
        loaded: object = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise PluginPackageError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise PluginPackageError(f"{path} is not a TOML table")
    project: object = loaded.get("project")
    if not isinstance(project, dict):
        raise PluginPackageError(f"{path} is missing a [project] table")
    name = project.get("name")
    version = project.get("version")
    if not isinstance(name, str) or name.strip() == "":
        raise PluginPackageError(f"{path} is missing [project].name")
    if not isinstance(version, str) or version.strip() == "":
        raise PluginPackageError(f"{path} is missing [project].version")
    return name, validate_version(version)


def _run_pip_wheel(project_dir: Path, output_dir: Path) -> None:
    """Run ``pip wheel --no-deps`` against ``project_dir``."""
    command: list[str] = [
        sys.executable,
        "-m",
        "pip",
        "wheel",
        "--no-deps",
        "--wheel-dir",
        str(output_dir),
        str(project_dir),
    ]
    completed: subprocess.CompletedProcess[str] = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        detail: str = completed.stderr.strip() or completed.stdout.strip()
        raise PluginPackageError(f"Failed to build pip wheel:\n{detail}")
