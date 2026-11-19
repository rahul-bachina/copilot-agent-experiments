"""Call Experiments 08 and 64 under private module names.

Redacted values are not stored. Experiment 64 supplies the example wording
list and the negation-aware affirmed() check. This module does not copy that
list into a second source of truth.
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
    "negate",
    "probes",
    "distress",
    "intents",
    "pack",
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
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_interview_pack",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def wording_module():
    module = _load(
        "64-job-description-quality",
        "words.py",
        "exp64_words_for_interview_pack",
    )
    if not hasattr(module, "affirmed") or not hasattr(module, "EXAMPLE_TERMS"):
        raise NeighbourMissing("64-job-description-quality")
    return module


def redact_uk_identifiers(text: str) -> dict:
    proposal = propose()(
        text,
        caller="exp-65-interview-pack-builder",
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


def wording_flags(text: str) -> list[dict]:
    """Example phrases from Experiment 64 that the text affirms. Not a statistic."""

    module = wording_module()
    found = []
    for row in module.EXAMPLE_TERMS:
        phrase = str(row.get("phrase") or "")
        if phrase and module.affirmed(text, phrase):
            found.append(
                {
                    "phrase": phrase,
                    "group": row.get("group"),
                    "alternative": row.get("alternative"),
                    "source": "exp-64-job-description-quality",
                    "example_list": True,
                    "statistic": False,
                }
            )
    return found
