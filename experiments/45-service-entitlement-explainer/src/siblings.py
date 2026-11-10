"""Load Experiment 38's citation normalise. Do not copy the rule.

A support phrase has to be a contiguous part of the cited clause after case
and whitespace are folded. That is Experiment 38's normalise, which is
Experiment 33's normalise. A missing folder is a hard stop.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


class EntitlementForbidden(RuntimeError):
    """This agent has no grant, refusal, change, send, or write path."""


_ROOT = Path(__file__).resolve().parents[2]
_NORMALISE = None


def normalise(text: str) -> str:
    """Fold case and whitespace the way Experiment 38 folds a citation."""
    global _NORMALISE
    if _NORMALISE is None:
        _NORMALISE = _load()
    return _NORMALISE(text)


def _load():
    folder = _ROOT / "38-policy-wording-comparison" / "src"
    if not folder.is_dir():
        raise EntitlementForbidden(
            "Experiment 38 is not beside this experiment. The citation check will not be copied."
        )
    alias = "exp45_exp38"
    package = types.ModuleType(alias)
    package.__path__ = [str(folder)]
    package.__package__ = alias
    sys.modules[alias] = package
    for name in ("injection", "siblings", "citations"):
        path = folder / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"{alias}.{name}", path)
        if spec is None or spec.loader is None:
            raise EntitlementForbidden(f"Could not load Experiment 38 src/{name}.py")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = alias
        sys.modules[f"{alias}.{name}"] = module
        spec.loader.exec_module(module)
    function = sys.modules[f"{alias}.citations"].normalise
    if not callable(function):
        raise EntitlementForbidden("Experiment 38 citations.normalise is missing.")
    return function
