"""Call Experiments 55, 51, and 03 without copying their modules into this one.

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
    "digest",
    "extract",
    "lifecycle",
    "drafts",
    "evaluations",
    "inventory",
    "pack",
    "manifest_generator",
    "dataverse_csv",
    "onboard",
    "labels",
    "graph_sim",
)


class NeighbourMissing(RuntimeError):
    """A required experiment folder is not beside this one."""


def _load(folder: str, filename: str, module_name: str, attribute: str):
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
    return module


_finder = None
_digest = None
_manifest = None


def finder_module():
    global _finder
    if _finder is None:
        _finder = _load(
            "55-onedrive-document-finder",
            "find.py",
            "exp55_find_for_onboarding",
            "find_documents",
        )
    return _finder


def digest_module():
    global _digest
    if _digest is None:
        _digest = _load(
            "51-teams-channel-digest",
            "digest.py",
            "exp51_digest_for_onboarding",
            "produce_digest",
        )
    return _digest


def manifest_module():
    global _manifest
    if _manifest is None:
        _manifest = _load(
            "03-agent-inventory-atrs-assurance",
            "manifest_generator.py",
            "exp03_manifest_for_onboarding",
            "generate_manifest",
        )
    return _manifest
