"""Argparse entry for ``aphelion-sdk`` and ``python -m aphelion_sdk``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from aphelion_sdk.host import EditorHostError, EditorInstall, locate_editor
from aphelion_sdk.host.install import install_plugins_into_editor
from aphelion_sdk.packaging import (
    PackageBuildResult,
    PluginPackageError,
    build_plugin_package,
)
from aphelion_sdk.version import DISTRIBUTION_NAME, __version__

_DESCRIPTION: str = (
    "Build Aphelion plugins, locate the installed editor, and copy "
    "drop-in plugins into that editor. Pass a .py file or plugin "
    "directory to wrap it, or a project root with pyproject.toml "
    "to run a standard PEP 517 build."
)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments and dispatch the requested command.

    Parameters:
        argv: Argument vector without the program name. Defaults to
            ``sys.argv[1:]``.

    Returns:
        Process exit code. ``0`` on success, ``1`` on packaging errors,
        ``2`` on usage errors (argparse).

    Exceptions:
        None. Packaging failures are printed to stderr.

    Side effects:
        May write wheel files and print status to stdout/stderr.
    """
    parser: argparse.ArgumentParser = _build_parser()
    args: argparse.Namespace = parser.parse_args(list(argv) if argv is not None else None)
    command: str | None = args.command
    if command == "build":
        return _handle_build(args)
    if command == "locate":
        return _handle_locate()
    if command == "install":
        return _handle_install(args)
    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    """Return the root parser with the ``build`` subcommand."""
    parser = argparse.ArgumentParser(prog="aphelion-sdk", description=_DESCRIPTION)
    parser.add_argument(
        "--version",
        action="version",
        version=f"{DISTRIBUTION_NAME} {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    _add_build_parser(subparsers)
    _add_locate_parser(subparsers)
    _add_install_parser(subparsers)
    return parser


def _add_build_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register ``aphelion-sdk build``."""
    parser = subparsers.add_parser(
        "build",
        help="Build a pip wheel from plugin source or an existing project.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Plugin .py file, plugin directory, or project root (default: cwd).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd() / "dist",
        help="Directory for built artifacts (default: ./dist).",
    )
    _add_build_metadata_flags(parser)


def _add_locate_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register ``aphelion-sdk locate``."""
    subparsers.add_parser(
        "locate",
        help="Print the Aphelion Editor install this SDK will target.",
    )


def _add_install_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register ``aphelion-sdk install``."""
    parser = subparsers.add_parser(
        "install",
        help="Copy plugin sources into the located editor's userdata/plugins.",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Plugin .py file or directory of plugin modules.",
    )


def _handle_locate() -> int:
    """Print the discovered editor install."""
    try:
        install: EditorInstall = locate_editor()
    except EditorHostError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    kind: str = "frozen" if install.is_frozen else "source"
    print(f"root: {install.root}")
    print(f"executable: {install.executable}")
    print(f"plugins: {install.user_plugin_dir}")
    print(f"version: {install.version or '(unknown)'}")
    print(f"source: {install.source} ({kind})")
    return 0


def _handle_install(args: argparse.Namespace) -> int:
    """Copy plugin files into the located editor."""
    try:
        written: tuple[Path, ...] = install_plugins_into_editor(args.source)
    except (EditorHostError, PluginPackageError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Installed {len(written)} plugin file(s) into {written[0].parent}")
    for path in written:
        print(f"  {path}")
    return 0


def _add_build_metadata_flags(parser: argparse.ArgumentParser) -> None:
    """Attach optional package-identity flags to the build parser."""
    parser.add_argument(
        "-n",
        "--name",
        default=None,
        help="Distribution name (generated packages only).",
    )
    parser.add_argument(
        "--package-version",
        default="0.1.0",
        help="Package version for generated packages (default: 0.1.0).",
    )
    parser.add_argument(
        "--author",
        default=None,
        help="Package author (generated packages only).",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Package summary (generated packages only).",
    )


def _handle_build(args: argparse.Namespace) -> int:
    """Run the packaging builder and print the resulting artifacts."""
    source: Path = args.source
    output: Path = args.output
    try:
        result: PackageBuildResult = build_plugin_package(
            source,
            output,
            distribution_name=args.name,
            version=args.package_version,
            author=args.author,
            description=args.description,
        )
    except PluginPackageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print_success(result)
    return 0


def _print_success(result: PackageBuildResult) -> None:
    """Write a short build summary to stdout."""
    kind: str = "project" if result.mode == "project" else "plugin package"
    print(f"Built {kind} {result.distribution_name} {result.version}")
    for plugin in result.plugins:
        print(f"  plugin: {plugin.plugin_name} ({plugin.class_name})")
    for artifact in result.artifacts:
        print(f"  {artifact}")
