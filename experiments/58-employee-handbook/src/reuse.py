"""Load Experiments 08, 11, 15, 32, and 50 under private module names.

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
    "gateway",
    "detectors",
    "identifiers",
    "phrases",
    "scan",
    "case_categories",
    "case_sources",
    "case_injection",
    "draft",
    "curate",
    "reuse",
    "mask",
    "answer",
    "handbook",
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


def gateway_module():
    module = _load("08-uk-pii-redaction-gateway", "gateway.py", "exp08_gateway_for_handbook")
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module


def era_module():
    module = _load("11-era-2025-hr-assistant", "sources.py", "exp11_sources_for_handbook")
    if not hasattr(module, "ALL_REASONABLE_STEPS_IN_FORCE"):
        raise NeighbourMissing("11-era-2025-hr-assistant")
    return module


def phrases_module():
    module = _load(
        "15-vulnerability-urgency-scanner",
        "phrases.py",
        "exp15_phrases_for_handbook",
    )
    if not hasattr(module, "find_phrases"):
        raise NeighbourMissing("15-vulnerability-urgency-scanner")
    return module


def categories_module():
    module = _load(
        "32-employee-case-intake",
        "case_categories.py",
        "exp32_categories_for_handbook",
    )
    if not hasattr(module, "keyword_hits"):
        raise NeighbourMissing("32-employee-case-intake")
    return module


def case_sources_module():
    module = _load(
        "32-employee-case-intake",
        "case_sources.py",
        "exp32_sources_for_handbook",
    )
    if not hasattr(module, "QUOTES"):
        raise NeighbourMissing("32-employee-case-intake")
    return module


def curate_module():
    module = _load(
        "50-sharepoint-knowledge-curator",
        "curate.py",
        "exp50_curate_for_handbook",
    )
    if not hasattr(module, "curate_site"):
        raise NeighbourMissing("50-sharepoint-knowledge-curator")
    return module
