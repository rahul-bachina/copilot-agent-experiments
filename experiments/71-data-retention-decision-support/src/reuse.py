"""Call Experiments 01, 08, and 12 under private module names.

Experiment 01 classification and urgency are signals. A negated sentence is
not turned into an open request or a distress finding by those keywords.
Experiment 08 propose() is not asked for a reversible vault. The redacted
text is not copied. Experiment 12 intake() does not confirm the file and
does not set a purpose. The file body is not copied.
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
    "advice",
    "match",
    "dates",
    "reuse",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "intake",
    "checklist",
    "mock_responses",
    "triage_agent",
    "prompts",
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


def detect_classification():
    module = _load(
        "01-foi-complaint-triage",
        "mock_responses.py",
        "exp01_mock_for_retention",
    )
    if not hasattr(module, "detect_classification"):
        raise NeighbourMissing("01-foi-complaint-triage")
    return module.detect_classification


def detect_urgency_flags():
    module = _load(
        "01-foi-complaint-triage",
        "mock_responses.py",
        "exp01_mock_for_retention",
    )
    if not hasattr(module, "detect_urgency_flags"):
        raise NeighbourMissing("01-foi-complaint-triage")
    return module.detect_urgency_flags


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_retention",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def intake():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_retention",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module.intake
