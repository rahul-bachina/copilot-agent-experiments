"""Call Experiments 08, 41, and 29 without copying their decisions.

Neighbour modules share names. Each one is loaded under a private module
name, and the previous bindings are put back afterwards.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "injection",
    "citations",
    "score",
    "tokens",
    "sources",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "summarise",
)

_propose = None
_check_sentence = None
_score_claim = None
_passage_currency = None
_summarise_claims = None


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


def propose():
    global _propose
    if _propose is None:
        module = _load("08-uk-pii-redaction-gateway", "gateway.py", "exp08_gateway_for_digest")
        if not hasattr(module, "propose"):
            raise NeighbourMissing("08-uk-pii-redaction-gateway")
        _propose = module.propose
    return _propose


def _load_package_file(folder: str, package_name: str, filename: str):
    """Load a module that uses relative imports, under a private package name."""
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
    sys.modules[sub_name] = module
    spec.loader.exec_module(module)
    return module


def check_sentence():
    global _check_sentence
    if _check_sentence is None:
        module = _load_package_file(
            "41-case-summary",
            "exp41_for_teams_digest",
            "citations.py",
        )
        if not hasattr(module, "check_sentence"):
            raise NeighbourMissing("41-case-summary")
        _check_sentence = module.check_sentence
    return _check_sentence


def groundedness():
    """Return score_claim, passage_currency, and summarise from Experiment 29."""
    global _score_claim, _passage_currency, _summarise_claims
    if _score_claim is None:
        module = _load("29-groundedness-evaluation", "score.py", "exp29_score_for_digest")
        if not hasattr(module, "score_claim"):
            raise NeighbourMissing("29-groundedness-evaluation")
        _score_claim = module.score_claim
        _passage_currency = module.passage_currency
        _summarise_claims = module.summarise
    return _score_claim, _passage_currency, _summarise_claims


def redact(text: str) -> dict[str, Any]:
    """Mask UK identifiers. The raw value is not returned."""
    proposal = propose()(
        text,
        caller="exp-51-teams-channel-digest",
        reversible=False,
    )
    redacted = str(proposal.get("redacted_text") or "")
    banner, _, body = redacted.partition("\n")
    if banner.startswith("[REDACTION PROPOSAL"):
        redacted_body = body
    else:
        redacted_body = redacted
    findings = ((proposal.get("audit_log") or {}).get("findings")) or []
    leaked = False
    types: list[str] = []
    for finding in findings:
        if not finding.get("applied"):
            continue
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
        start = finding.get("start")
        end = finding.get("end")
        if isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text):
            value = text[start:end]
            if value and value in redacted_body:
                leaked = True
    anonymisation = proposal.get("anonymisation") or {}
    release = proposal.get("release") or {}
    security = proposal.get("security") or {}
    return {
        "text": redacted_body,
        "entity_types": types,
        "value_leaked": leaked,
        "output_is_anonymised": anonymisation.get("output_is_anonymised"),
        "agent_may_release": release.get("agent_may_release"),
        "prompt_injection_signals": list(security.get("prompt_injection_signals") or []),
    }
