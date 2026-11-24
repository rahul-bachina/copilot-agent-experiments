"""Call Experiments 08 and 13 without copying their text into the answer.

Experiment 08 propose() is not asked for a reversible vault. The redacted
text is not copied. Experiment 13 triage() is a contact-route reading.
Its reply is not the benefits answer, and it does not decide eligibility.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "cues",
    "mask",
    "marking",
    "negate",
    "dates",
    "reuse",
    "knowledge",
    "paraphrases",
    "assistant",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "front_door",
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
        "exp08_gateway_for_benefits",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def triage():
    module = _load(
        "13-council-contact-front-door",
        "front_door.py",
        "exp13_front_door_for_benefits",
    )
    if not hasattr(module, "triage"):
        raise NeighbourMissing("13-council-contact-front-door")
    return module.triage


def identifier_counts(text: str, *, on: date) -> dict:
    try:
        proposal = propose()(
            text,
            caller="exp-75-benefits-information-assistant",
            now=datetime(on.year, on.month, on.day),
            rules_as_of=on,
            apply_model_suggestions=False,
            reversible=False,
        )
    except NeighbourMissing as exc:
        return _identifier_gap(str(exc))
    anonymised = (proposal.get("anonymisation") or {}).get("output_is_anonymised")
    if anonymised is not False:
        return _identifier_gap("experiment_08_reported_anonymised")
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
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "count": count,
        "types": types,
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
    }


def contact_route(text: str, *, on: date) -> dict:
    """Record that the contact front door was read. Do not copy its reply."""

    enquiry = {
        "synthetic": True,
        "enquiry_id": "SYN-BEN-FD",
        "channel": "web_chat",
        "text": text[:4000],
    }
    try:
        draft = triage()(enquiry, on)
    except NeighbourMissing as exc:
        return _route_gap(str(exc))
    flags = draft.get("flags") or {}
    if flags.get("eligibility_decided") is not False or flags.get("message_sent") is not False:
        return _route_gap("experiment_13_unexpected_action")
    return {
        "called": True,
        "experiment_id": "exp-13-council-contact-front-door",
        "council": "Northmarsh Borough Council",
        "outcome": draft.get("outcome"),
        "eligibility_decided": False,
        "message_sent": False,
        "case_created": flags.get("case_created"),
        "human_approval": None,
        "reply_copied": False,
        "handover_required": (draft.get("handover") or {}).get("required"),
    }


def _identifier_gap(reason: str) -> dict:
    return {
        "called": False,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "reason": reason,
        "count": None,
        "types": [],
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
    }


def _route_gap(reason: str) -> dict:
    return {
        "called": False,
        "experiment_id": "exp-13-council-contact-front-door",
        "reason": reason,
        "reply_copied": False,
        "eligibility_decided": False,
        "message_sent": False,
        "human_approval": None,
    }
