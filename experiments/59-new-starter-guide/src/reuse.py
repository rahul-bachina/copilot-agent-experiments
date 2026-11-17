"""Call Experiments 58, 57, 21, 11, 15, and 08 without copying their modules.

Neighbour modules share names such as ``sources``. Each one is loaded under
a private module name, and the previous bindings are put back afterwards.
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
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "phrases",
    "desk",
    "catalogue",
    "identity",
    "onboard",
    "labels",
    "masking",
    "graph_sim",
    "guide",
    "case_categories",
    "case_sources",
    "case_injection",
    "draft",
    "curate",
    "scan",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load(folder: str, filename: str, module_name: str, attribute: str):
    if module_name in _cache:
        module = _cache[module_name]
        if not hasattr(module, attribute):
            raise NeighbourMissing(folder)
        return module
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
    if not hasattr(module, attribute):
        raise NeighbourMissing(folder)
    _cache[module_name] = module
    return module


def handbook_module():
    return _load(
        "58-employee-handbook",
        "handbook.py",
        "exp58_handbook_for_starter",
        "source_includes",
    )


def answer_module():
    return _load(
        "58-employee-handbook",
        "answer.py",
        "exp58_answer_for_starter",
        "answer_handbook",
    )


def mask_module():
    return _load(
        "58-employee-handbook",
        "mask.py",
        "exp58_mask_for_starter",
        "mask_counts",
    )


def onboard_module():
    return _load(
        "57-collaboration-space-onboarding",
        "onboard.py",
        "exp57_onboard_for_starter",
        "prepare_onboarding",
    )


def desk_module():
    return _load(
        "21-it-service-desk",
        "desk.py",
        "exp21_desk_for_starter",
        "triage",
    )


def era_module():
    return _load(
        "11-era-2025-hr-assistant",
        "sources.py",
        "exp11_sources_for_starter",
        "ALL_REASONABLE_STEPS_IN_FORCE",
    )


def phrases_module():
    return _load(
        "15-vulnerability-urgency-scanner",
        "phrases.py",
        "exp15_phrases_for_starter",
        "find_phrases",
    )


def gateway_module():
    return _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_starter",
        "propose",
    )
