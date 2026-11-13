"""Call Experiments 49, 50, and 08 without copying their text out.

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
    "catalogue",
    "injection",
    "screening",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "intake",
    "guards",
    "scheme",
    "reuse",
    "classify",
    "gaps",
    "knowledge",
    "curate",
    "find",
    "mask",
)

_classify = None
_curate = None
_gateway = None


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


def classify_module():
    global _classify
    if _classify is None:
        module = _load(
            "49-records-classification",
            "classify.py",
            "exp49_classify_for_finder",
        )
        if not hasattr(module, "classify_record"):
            raise NeighbourMissing("49-records-classification")
        _classify = module
    return _classify


def curate_module():
    global _curate
    if _curate is None:
        module = _load(
            "50-sharepoint-knowledge-curator",
            "curate.py",
            "exp50_curate_for_finder",
        )
        if not hasattr(module, "curate_site"):
            raise NeighbourMissing("50-sharepoint-knowledge-curator")
        _curate = module
    return _curate


def gateway_module():
    global _gateway
    if _gateway is None:
        module = _load(
            "08-uk-pii-redaction-gateway",
            "gateway.py",
            "exp08_gateway_for_finder",
        )
        if not hasattr(module, "propose"):
            raise NeighbourMissing("08-uk-pii-redaction-gateway")
        _gateway = module
    return _gateway
