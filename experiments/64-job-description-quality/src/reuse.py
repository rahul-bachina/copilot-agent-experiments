"""Call Experiments 08 and 36 under private module names.

Shared names are restored after each load. Redacted values and comparison
quotes are not stored by this module.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "words",
    "mask",
    "marking",
    "review",
    "reuse",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "compare",
    "normalise",
    "siblings",
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


def propose():
    """Experiment 08 propose(). reversible stays false. output is not anonymised."""

    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_job_description",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def compare_module():
    module = _load(
        "36-cross-source-validation",
        "compare.py",
        "exp36_compare_for_job_description",
    )
    if not hasattr(module, "compare"):
        raise NeighbourMissing("36-cross-source-validation")
    return module


def redact_uk_identifiers(text: str) -> dict:
    """Types and redacted body. The banner and the matched values are not returned."""

    proposal = propose()(
        text,
        caller="exp-64-job-description-quality",
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 reported anonymised output. This starter will not use it.")
    redacted = str(proposal.get("redacted_text") or "")
    banner, _sep, body = redacted.partition("\n")
    shown = body if banner.startswith("[REDACTION PROPOSAL") else redacted
    types: list[str] = []
    count = 0
    for finding in (proposal.get("audit_log") or {}).get("findings") or []:
        if not finding.get("applied"):
            continue
        count += 1
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
    return {
        "text": shown,
        "types": types,
        "count": count,
        "output_is_anonymised": False,
        "values_stored": False,
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
    }
