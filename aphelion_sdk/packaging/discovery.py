"""Locate ``Plugin`` subclasses in author source without executing it."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from aphelion_sdk.packaging.errors import PluginPackageError
from aphelion_sdk.packaging.names import module_identifier

_PLUGIN_BASE_TERMINALS: frozenset[str] = frozenset({"Plugin", "VideoEffectPlugin", "NodePlugin", "AudioNodePlugin", "AudioEffectPlugin", "EditorExtension"})
_DEFAULT_AUTHOR: str = "Unknown"


@dataclass(frozen=True, slots=True)
class DiscoveredPlugin:
    """One plugin class found in author source.

    Attributes:
        class_name: Python class identifier.
        module_name: Destination module stem inside the generated package.
        source_path: Absolute path to the original ``.py`` file.
        plugin_name: Display name from ``plugin_name``, or the class name.
        plugin_description: ``plugin_description`` string, possibly empty.
        plugin_author: ``plugin_author`` string, or ``Unknown``.
        plugin_kind: ``plugin_kind`` string, or ``plugin``.
    """

    class_name: str
    module_name: str
    source_path: Path
    plugin_name: str
    plugin_description: str
    plugin_author: str
    plugin_kind: str


def plugin_source_files(source: Path) -> tuple[Path, ...]:
    """Return plugin modules under ``source``.

    Parameters:
        source: A ``.py`` file or a directory of top-level plugin modules.

    Returns:
        Absolute paths, sorted, excluding ``_``-prefixed files.

    Exceptions:
        PluginPackageError: If ``source`` is missing or has no ``.py`` files.

    Side effects:
        None.
    """
    resolved: Path = source.expanduser().resolve()
    if resolved.is_file():
        return _single_source_file(resolved)
    if not resolved.is_dir():
        raise PluginPackageError(f"Plugin source does not exist: {source}")
    files: tuple[Path, ...] = tuple(
        sorted(
            path
            for path in resolved.glob("*.py")
            if path.is_file() and not path.name.startswith("_")
        )
    )
    if not files:
        raise PluginPackageError(f"No plugin modules found in {resolved}")
    return files


def discover_plugins(source: Path) -> tuple[DiscoveredPlugin, ...]:
    """Return every plugin class declared under ``source``.

    Parameters:
        source: A ``.py`` file or a directory of plugin modules.

    Returns:
        Discovered plugin classes, in file then class order.

    Exceptions:
        PluginPackageError: If no plugin classes are found, sources collide
            on module names, or a file cannot be parsed.

    Side effects:
        Reads source files from disk.
    """
    files: tuple[Path, ...] = plugin_source_files(source)
    used_modules: dict[str, Path] = {}
    plugins: list[DiscoveredPlugin] = []
    for file_path in files:
        module_name: str = _unique_module_name(file_path, used_modules)
        plugins.extend(_discover_in_file(file_path, module_name))
    if not plugins:
        raise PluginPackageError(f"No Plugin subclasses found in {source}")
    return tuple(plugins)


def _single_source_file(resolved: Path) -> tuple[Path, ...]:
    """Validate and wrap a single plugin file path."""
    if resolved.suffix != ".py":
        raise PluginPackageError(f"Plugin source must be a .py file: {resolved}")
    return (resolved,)


def _unique_module_name(file_path: Path, used_modules: dict[str, Path]) -> str:
    """Return a module stem, rejecting collisions across different files."""
    module_name: str = module_identifier(file_path)
    previous: Path | None = used_modules.get(module_name)
    if previous is not None and previous != file_path:
        raise PluginPackageError(
            f"Module name {module_name!r} maps to both {previous} and {file_path}"
        )
    used_modules[module_name] = file_path
    return module_name


def _discover_in_file(file_path: Path, module_name: str) -> tuple[DiscoveredPlugin, ...]:
    """Parse ``file_path`` and return plugin classes defined at module scope."""
    try:
        source_text: str = file_path.read_text(encoding="utf-8")
        tree: ast.Module = ast.parse(source_text, filename=str(file_path))
    except (OSError, SyntaxError) as exc:
        raise PluginPackageError(f"Cannot parse plugin source {file_path}: {exc}") from exc
    aliases: dict[str, str] = _import_aliases(tree)
    discovered: list[DiscoveredPlugin] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and _class_is_plugin(node, aliases):
            discovered.append(_plugin_from_class(node, file_path, module_name))
    return tuple(discovered)


def _import_aliases(tree: ast.Module) -> dict[str, str]:
    """Map local import names to dotted module paths."""
    aliases: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            _record_import(node, aliases)
        elif isinstance(node, ast.ImportFrom):
            _record_import_from(node, aliases)
    return aliases


def _record_import(node: ast.Import, aliases: dict[str, str]) -> None:
    """Record ``import a.b as c`` bindings."""
    for alias in node.names:
        aliases[alias.asname or alias.name] = alias.name


def _record_import_from(node: ast.ImportFrom, aliases: dict[str, str]) -> None:
    """Record ``from a.b import Name as c`` bindings."""
    if node.module is None:
        return
    for alias in node.names:
        if alias.name == "*":
            continue
        aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"


def _class_is_plugin(node: ast.ClassDef, aliases: dict[str, str]) -> bool:
    """Return True when ``node`` subclasses an SDK plugin base."""
    if node.name in _PLUGIN_BASE_TERMINALS:
        return False
    return any(_is_plugin_base(_resolve_base(base, aliases)) for base in node.bases)


def _dotted_name(node: ast.expr) -> str | None:
    """Return a dotted name for ``Name`` / ``Attribute`` nodes."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent: str | None = _dotted_name(node.value)
        if parent is None:
            return None
        return f"{parent}.{node.attr}"
    return None


def _resolve_base(node: ast.expr, aliases: dict[str, str]) -> str:
    """Return a fully resolved dotted base name, or empty if unknown."""
    dotted: str | None = _dotted_name(node)
    if dotted is None:
        return ""
    parts: list[str] = dotted.split(".")
    root: str = parts[0]
    if root in aliases:
        return ".".join([aliases[root], *parts[1:]])
    return dotted


def _is_plugin_base(resolved: str) -> bool:
    """Return True when ``resolved`` names an SDK plugin base class."""
    if resolved == "":
        return False
    terminal: str = resolved.rsplit(".", 1)[-1]
    if terminal not in _PLUGIN_BASE_TERMINALS:
        return False
    return resolved == terminal or resolved.startswith("aphelion_sdk")


def _plugin_from_class(
    node: ast.ClassDef,
    file_path: Path,
    module_name: str,
) -> DiscoveredPlugin:
    """Build a ``DiscoveredPlugin`` from a class definition."""
    plugin_name: str = _class_str_attr(node, "plugin_name") or node.name
    return DiscoveredPlugin(
        class_name=node.name,
        module_name=module_name,
        source_path=file_path,
        plugin_name=plugin_name,
        plugin_description=_class_str_attr(node, "plugin_description") or "",
        plugin_author=_class_str_attr(node, "plugin_author") or _DEFAULT_AUTHOR,
        plugin_kind=_class_str_attr(node, "plugin_kind") or "plugin",
    )


def _class_str_attr(node: ast.ClassDef, attr_name: str) -> str | None:
    """Return a class-body string assignment named ``attr_name``."""
    for stmt in node.body:
        value: str | None = _assigned_str(stmt, attr_name)
        if value is not None:
            return value
    return None


def _assigned_str(stmt: ast.stmt, attr_name: str) -> str | None:
    """Return a string constant assigned to ``attr_name``, if present."""
    target_name: str | None
    value_node: ast.expr | None
    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
        target_name = _name_id(stmt.targets[0])
        value_node = stmt.value
    elif isinstance(stmt, ast.AnnAssign):
        target_name = _name_id(stmt.target)
        value_node = stmt.value
    else:
        return None
    if target_name != attr_name or value_node is None:
        return None
    if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
        return value_node.value
    return None


def _name_id(node: ast.expr) -> str | None:
    """Return the identifier of a bare ``Name`` node."""
    if isinstance(node, ast.Name):
        return node.id
    return None
