"""Build Aphelion plugins into pip-installable distributions.

This package is the packaging engine behind ``aphelion-sdk build``. Plugin
authors should keep using ``import aphelion_sdk``; they do not need these
symbols unless they are driving the builder from their own scripts.
"""

from __future__ import annotations

from aphelion_sdk.packaging.builder import PackageBuildResult, build_plugin_package
from aphelion_sdk.packaging.discovery import DiscoveredPlugin
from aphelion_sdk.packaging.errors import PluginPackageError

__all__ = [
    "DiscoveredPlugin",
    "PackageBuildResult",
    "PluginPackageError",
    "build_plugin_package",
]
