"""Call Experiments 12, 08, and 70 under private module names.

Experiment 12 intake() does not confirm a file and does not set a purpose.
Experiment 08 propose() is not asked for a reversible vault, and the redacted
text is not copied. Experiment 70 mentioned_supplier_ids() and
procurement_view() do not decide that a conflict exists.

Experiment 73 binds an approval to the named directory role and the exact
content hash. That function expects a tester and a working paper, so it is
not called. The same binding rules are implemented in pack.py and tested
with a tampered pack.
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
    "sample",
    "reuse",
    "testing",
    "paraphrases",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "intake",
    "checklist",
    "diffing",
    "normalise",
    "prohibited",
    "yaml_reader",
    "statements",
    "library",
    "mapping",
    "match",
    "declaration",
    "pack",
    "checks",
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
        "exp08_gateway_for_board_pack",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def intake():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_board_pack",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module.intake


def supplier_match():
    module = _load(
        "70-conflict-of-interest-intake",
        "match.py",
        "exp70_match_for_board_pack",
    )
    if not hasattr(module, "mentioned_supplier_ids") or not hasattr(module, "procurement_view"):
        raise NeighbourMissing("70-conflict-of-interest-intake")
    return module.mentioned_supplier_ids, module.procurement_view


def identifier_counts(text: str, *, on: date) -> dict:
    proposal = propose()(
        text,
        caller="exp-74-board-governance-pack",
        now=datetime(on.year, on.month, on.day),
        rules_as_of=on,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 reported anonymised output. This starter will not use it.")
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


def intake_papers(files: list[dict], *, on: date) -> dict:
    base = {
        "called": False,
        "experiment_id": "exp-12-document-intake",
        "files_confirmed": False,
        "purpose_confirmed": False,
        "content_recorded": False,
    }
    if not files:
        base["reason"] = "no_files"
        return base
    batch = {"synthetic": True, "batch_id": "board-papers", "files": files[:12]}
    try:
        draft = intake()(batch, as_of=on)
    except (OSError, ValueError, TypeError) as exc:
        base["reason"] = type(exc).__name__
        return base
    base.update(
        {
            "called": True,
            "reason": None,
            "files_confirmed": draft.get("files_confirmed"),
            "purpose_confirmed": draft.get("purpose_confirmed"),
            "intake_capped": len(files) > 12,
            "file_count": len(draft.get("files") or []),
            "actions_taken": draft.get("actions_taken"),
        }
    )
    return base


def conflict_links(text: str, suppliers: dict, procurements: dict, *, on: date) -> dict:
    base = {
        "called": False,
        "experiment_id": "exp-70-conflict-of-interest-intake",
        "conflict_exists": None,
        "decides_conflict": False,
        "supplier_ids": [],
        "potential_link_count": 0,
    }
    try:
        mentioned, view = supplier_match()
    except (NeighbourMissing, ImportError, OSError):
        base["reason"] = "neighbour_missing"
        return base
    supplier_ids = mentioned(text, suppliers)
    linked = view(procurements, supplier_ids, [], on)
    base.update(
        {
            "called": True,
            "reason": None,
            "supplier_ids": supplier_ids,
            "potential_link_count": len(linked.get("potential_links") or []),
            "conflict_exists": None,
            "decides_conflict": False,
        }
    )
    return base
