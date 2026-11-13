"""Call Experiments 08, 15, 30, and 36 without copying their rules."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "cases",
    "detectors",
    "gateway",
    "identifiers",
    "injection",
    "model_assist",
    "normalise",
    "phrases",
    "siblings",
    "sources",
)


class NeighbourMissing(RuntimeError):
    """A required experiment folder is not beside this one."""


def _load(folder: str, filename: str, module_name: str):
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
    return module


def _load_package_file(folder: str, package_name: str, filename: str):
    src = EXPERIMENTS / folder / "src"
    init = src / "__init__.py"
    if not init.is_file():
        raise NeighbourMissing(folder)
    if package_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            package_name,
            init,
            submodule_search_locations=[str(src)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(package_name)
        package = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = package
        spec.loader.exec_module(package)
    sub_name = f"{package_name}.{Path(filename).stem}"
    if sub_name in sys.modules:
        return sys.modules[sub_name]
    spec = importlib.util.spec_from_file_location(sub_name, src / filename)
    if spec is None or spec.loader is None:
        raise ImportError(sub_name)
    module = importlib.util.module_from_spec(spec)
    module.__package__ = package_name
    sys.modules[sub_name] = module
    spec.loader.exec_module(module)
    return module


_propose = None
_find_phrases = None
_from_observation = None
_normalise = None
_classify = None
_fold = None


def propose():
    global _propose
    if _propose is None:
        module = _load("08-uk-pii-redaction-gateway", "gateway.py", "exp08_gateway_for_excel_review")
        if not hasattr(module, "propose"):
            raise NeighbourMissing("08-uk-pii-redaction-gateway")
        _propose = module.propose
    return _propose


def find_phrases():
    global _find_phrases
    if _find_phrases is None:
        module = _load(
            "15-vulnerability-urgency-scanner",
            "phrases.py",
            "exp15_phrases_for_excel_review",
        )
        if not hasattr(module, "find_phrases"):
            raise NeighbourMissing("15-vulnerability-urgency-scanner")
        _find_phrases = module.find_phrases
    return _find_phrases


def from_observation():
    global _from_observation
    if _from_observation is None:
        module = _load(
            "30-agent-regression-test-generator",
            "cases.py",
            "exp30_cases_for_excel_review",
        )
        if not hasattr(module, "from_observation"):
            raise NeighbourMissing("30-agent-regression-test-generator")
        _from_observation = module.from_observation
    return _from_observation


def cross_source() -> tuple[Any, Any, Any]:
    global _normalise, _classify, _fold
    if _normalise is None or _classify is None or _fold is None:
        module = _load_package_file(
            "36-cross-source-validation",
            "exp36_for_excel_review",
            "normalise.py",
        )
        if not hasattr(module, "normalise_value") or not hasattr(module, "classify_values"):
            raise NeighbourMissing("36-cross-source-validation")
        _normalise = module.normalise_value
        _classify = module.classify_values
        _fold = module.display_fold
    return _normalise, _classify, _fold
