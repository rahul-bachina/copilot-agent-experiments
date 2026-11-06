"""Load Experiments 12, 29, and 33 without copying their rules.

The folders sit beside this one. A missing folder is a hard stop. This
module does not reimplement document intake, the pinpoint span check, or
the number and date boundary check.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


class CompareForbidden(RuntimeError):
    """The comparison has no favourability, recommendation, endorsement, send, or write path."""


_ROOT = Path(__file__).resolve().parents[2]
_LOADED = False
_CACHE: dict = {}


def _package(alias: str, folder: str, modules: tuple[str, ...]) -> dict:
    src = _ROOT / folder / "src"
    if not src.is_dir():
        raise CompareForbidden(
            f"{folder} is not beside this experiment. This starter will not copy its rules."
        )
    package = types.ModuleType(alias)
    package.__path__ = [str(src)]
    package.__package__ = alias
    sys.modules[alias] = package
    loaded = {}
    for name in modules:
        path = src / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"{alias}.{name}", path)
        if spec is None or spec.loader is None:
            raise CompareForbidden(f"Could not load {folder}/src/{name}.py")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = alias
        sys.modules[f"{alias}.{name}"] = module
        spec.loader.exec_module(module)
        loaded[name] = module
    return loaded


def load() -> dict:
    """Import the siblings once. Later calls return the same modules."""
    global _LOADED
    if _LOADED:
        return _CACHE
    exp12 = _package("exp38_exp12", "12-document-intake", ("catalogue", "injection", "intake"))
    exp33 = _package("exp38_exp33", "33-case-bundle-summariser", ("injection", "citations"))
    score_path = _ROOT / "29-groundedness-evaluation" / "src" / "score.py"
    if not score_path.is_file():
        raise CompareForbidden(
            "Experiment 29 is not beside this experiment. The number check will not be invented."
        )
    spec = importlib.util.spec_from_file_location("exp29_score_for_b008", score_path)
    if spec is None or spec.loader is None:
        raise CompareForbidden("Experiment 29 score.py could not be loaded.")
    score = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(score)
    for name in ("extract_numbers", "extract_dates", "number_in", "normalise"):
        if not hasattr(score, name):
            raise CompareForbidden(f"Experiment 29 score.py has no {name}.")
    _CACHE.update(
        {
            "intake": exp12["intake"].intake,
            "intake_not_synthetic": exp12["intake"].NotSynthetic,
            "intake_experiment_id": exp12["catalogue"].EXPERIMENT_ID,
            "resolve_span": exp33["citations"].resolve_span,
            "citation_normalise": exp33["citations"].normalise,
            "citation_experiment_id": "exp-33-case-bundle-summariser",
            "score": score,
        }
    )
    _LOADED = True
    return _CACHE
