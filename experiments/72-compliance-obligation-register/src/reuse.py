"""Call Experiments 68, 69, 12, and 08 under private module names.

Experiment 68 dates are a cross-check. A disagreement is flagged and is not
resolved by picking a neighbour date. Experiment 69's strength and
qualification are recorded. A qualified sentence is not treated as support,
which is the gap in Experiment 69's assess_sentence. Experiment 12 does not
confirm the file. Experiment 08 does not describe the text as anonymised.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "dates",
    "negate",
    "marking",
    "mask",
    "cues",
    "match",
    "reuse",
    "register",
    "statements",
    "library",
    "intake",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "checklist",
    "classify",
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


def _isolated(function):
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)
    try:
        return function()
    finally:
        sys.path[:] = saved_path
        extra = [name for name in list(sys.modules) if name not in saved_modules]
        for name in extra:
            sys.modules.pop(name, None)
        for name, module in saved_modules.items():
            sys.modules[name] = module


def cross_check_date(token: str) -> dict:
    """Experiment 68's reading. It does not replace the local reading."""

    def _run():
        module = _load(
            "68-regulatory-change-briefing",
            "dates.py",
            "exp68_dates_for_obligation_register",
        )
        parsed, bad = module.parse_date_token(token)
        iso = parsed.isoformat() if parsed is not None else None
        return {"called": True, "iso": iso, "unparseable": bool(bad)}

    try:
        return _isolated(_run)
    except NeighbourMissing as exc:
        return {"called": False, "error": str(exc), "iso": None, "unparseable": None}


def experiment_69_reading(sentence: str) -> dict:
    def _run():
        module = _load(
            "69-policy-control-mapping",
            "statements.py",
            "exp69_statements_for_obligation_register",
        )
        return {
            "called": True,
            "strength": module.strength_of(sentence),
            "qualified": bool(module.qualified(sentence)),
        }

    try:
        return _isolated(_run)
    except NeighbourMissing as exc:
        return {"called": False, "error": str(exc), "strength": None, "qualified": None}


def intake_extracts(files: list[dict], *, as_of: date) -> dict:
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_obligation_register",
    )
    batch = {"synthetic": True, "batch_id": "obligation-extracts", "files": files}

    def _run():
        return module.intake(batch, as_of=as_of)

    draft = _isolated(_run)
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "files_confirmed": draft.get("files_confirmed"),
        "purpose_confirmed": draft.get("purpose_confirmed"),
        "any_document_stale": draft.get("any_document_stale"),
        "catalogue_stale": draft.get("catalogue_stale"),
        "actions_taken": draft.get("actions_taken"),
    }


def redact_note(text: str, *, rules_as_of: date) -> dict:
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_obligation_register",
    )

    def _run():
        return module.propose(
            text,
            caller="exp-72-compliance-obligation-register",
            now=datetime(rules_as_of.year, rules_as_of.month, rules_as_of.day),
            rules_as_of=rules_as_of,
            apply_model_suggestions=False,
            reversible=False,
        )

    proposal = _isolated(_run)
    anonymised = (proposal.get("anonymisation") or {}).get("output_is_anonymised")
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
        "output_is_anonymised": anonymised,
        "finding_count": count,
        "entity_types": types,
        "values_stored": False,
        "note_copied": False,
    }
