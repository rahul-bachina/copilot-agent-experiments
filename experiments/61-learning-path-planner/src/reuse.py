"""Load Experiments 58, 44, and 36 under private module names.

Shared names such as ``sources`` are restored after each load. This file
does not copy their statutory text into a second pin.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "handbook",
    "mask",
    "answer",
    "reuse",
    "gaps",
    "knowledge",
    "compare",
    "normalise",
    "siblings",
    "plan",
    "gateway",
    "detectors",
    "identifiers",
    "phrases",
    "scan",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load(folder: str, filename: str, module_name: str):
    if module_name in _cache:
        return _cache[module_name]
    saved = {name: sys.modules[name] for name in _COLLIDING if name in sys.modules}
    src = EXPERIMENTS / folder / "src"
    path = src / filename
    if not path.is_file():
        raise NeighbourMissing(folder)
    sys.path.insert(0, str(src))
    try:
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(module_name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        while str(src) in sys.path:
            sys.path.remove(str(src))
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        sys.modules.update(saved)
    _cache[module_name] = module
    return module


def handbook_module():
    module = _load("58-employee-handbook", "handbook.py", "exp58_handbook_for_learning")
    if not hasattr(module, "source_includes"):
        raise NeighbourMissing("58-employee-handbook")
    return module


def mask_module():
    module = _load("58-employee-handbook", "mask.py", "exp58_mask_for_learning")
    if not hasattr(module, "mask_counts"):
        raise NeighbourMissing("58-employee-handbook")
    return module


def answer_module():
    module = _load("58-employee-handbook", "answer.py", "exp58_answer_for_learning")
    if not hasattr(module, "answer_handbook"):
        raise NeighbourMissing("58-employee-handbook")
    return module


def gaps_module():
    module = _load("44-knowledge-gap-detector", "gaps.py", "exp44_gaps_for_learning")
    if not hasattr(module, "detect_gaps"):
        raise NeighbourMissing("44-knowledge-gap-detector")
    return module


def compare_module():
    module = _load("36-cross-source-validation", "compare.py", "exp36_compare_for_learning")
    if not hasattr(module, "compare"):
        raise NeighbourMissing("36-cross-source-validation")
    return module
