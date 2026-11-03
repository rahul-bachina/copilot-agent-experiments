"""Load Experiment 25's YAML reader under a name that does not collide.

The clean install does not include PyYAML. A file the reader cannot parse
raises YamlError. The tests report that. They do not guess a pass.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_READER = Path(__file__).resolve().parents[2] / "25-instruction-quality-reviewer" / "src" / "manifest_yaml.py"
_MODULE = None


class YamlError(ValueError):
    """The manifest is not in the subset the reader accepts."""


def load_yaml(text: str) -> Any:
    module = _load()
    try:
        return module.load_yaml(text)
    except module.YamlError as exc:
        raise YamlError(str(exc)) from exc


def _load():
    global _MODULE
    if _MODULE is not None:
        return _MODULE
    spec = importlib.util.spec_from_file_location("exp25_manifest_yaml", _READER)
    if spec is None or spec.loader is None:
        raise YamlError("Experiment 25's YAML reader could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _MODULE = module
    return module
