"""Call Experiments 08, 12, and 32 under private module names.

Experiment 08 propose() is not asked for a reversible vault. The redacted
text is not copied into this starter's result. Experiment 12 intake() does
not confirm the file and does not set a purpose. Experiment 32 keyword and
injection helpers are read. Their narrative is not copied. This starter does
not call Experiment 32 draft_case(), because a declaration is not an HR case.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "cues",
    "mask",
    "marking",
    "negate",
    "review",
    "reuse",
    "declaration",
    "match",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "intake",
    "checklist",
    "case_categories",
    "case_injection",
    "case_sources",
    "draft",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load(folder: str, filename: str, module_name: str):
    if module_name in _cache:
        return _cache[module_name]
    saved = {name: sys.modules.get(name) for name in _COLLIDING}
    saved_path = list(sys.path)
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
        sys.path[:] = saved_path
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        for name, saved_module in saved.items():
            if saved_module is not None:
                sys.modules[name] = saved_module
    _cache[module_name] = module
    return module


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_coi",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def intake():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_coi",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module.intake


def case_categories():
    return _load(
        "32-employee-case-intake",
        "case_categories.py",
        "exp32_categories_for_coi",
    )


def case_injection():
    return _load(
        "32-employee-case-intake",
        "case_injection.py",
        "exp32_injection_for_coi",
    )
