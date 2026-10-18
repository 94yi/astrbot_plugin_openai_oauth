"""Resolve the AstrBot checkout used by integration-style plugin tests."""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path


def resolve_astrbot_root() -> Path:
    """Return an AstrBot root from the environment or deployed directory tree."""
    configured = os.environ.get("ASTRBOT_ROOT", "").strip()
    candidates = [Path(configured).expanduser()] if configured else []
    current = Path(__file__).resolve()
    candidates.extend(current.parents)
    candidates.append(current.parents[2] / "AstrBot")
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "astrbot").is_dir() and (resolved / "data").is_dir():
            return resolved
    raise FileNotFoundError(
        "AstrBot root was not found; set ASTRBOT_ROOT to the checkout directory"
    )


def configure_test_imports() -> Path:
    """Expose the source checkout through AstrBot's deployed plugin namespace."""
    astrbot_root = resolve_astrbot_root()
    plugin_root = Path(__file__).resolve().parents[1]
    deployed_root = astrbot_root / "data/plugins/astrbot_plugin_openai_oauth"
    if not deployed_root.is_dir():
        packages = (
            ("data", astrbot_root / "data"),
            ("data.plugins", astrbot_root / "data/plugins"),
            ("data.plugins.astrbot_plugin_openai_oauth", plugin_root),
        )
        for name, path in packages:
            module = sys.modules.setdefault(name, types.ModuleType(name))
            locations = list(getattr(module, "__path__", []))
            if str(path) not in locations:
                locations.append(str(path))
            module.__path__ = locations
    return astrbot_root
