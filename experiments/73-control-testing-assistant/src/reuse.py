"""Call Experiments 12, 69, and 08 under private module names.

Experiment 12 intake() does not confirm a file and does not set a purpose.
Experiment 69 map_controls() does not mark a control as met. Experiment 08
propose() is not asked for a reversible vault, and the redacted text is not
copied into this starter's result.
"""

from __future__ import annotations

import importlib.util
import json
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
    "map_controls",
    "compare",
    "siblings",
    "drafts",
    "evaluations",
    "inventory",
    "pack",
    "lifecycle",
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
        "exp08_gateway_for_control_testing",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def intake():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_control_testing",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module.intake


def map_controls():
    module = _load(
        "69-policy-control-mapping",
        "map_controls.py",
        "exp69_map_controls_for_control_testing",
    )
    if not hasattr(module, "map_controls"):
        raise NeighbourMissing("69-policy-control-mapping")
    return module.map_controls


def identifier_counts(text: str, *, on: date) -> dict:
    def _run():
        return propose()(
            text,
            caller="exp-73-control-testing-assistant",
            now=datetime(on.year, on.month, on.day),
            rules_as_of=on,
            apply_model_suggestions=False,
            reversible=False,
        )

    proposal = _run()
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


def intake_evidence(files: list[dict], *, on: date) -> dict:
    if not files:
        return {
            "called": False,
            "reason": "no_files",
            "experiment_id": "exp-12-document-intake",
            "files_confirmed": False,
            "purpose_confirmed": False,
        }
    batch = {"synthetic": True, "batch_id": "control-evidence", "files": files[:12]}
    draft = intake()(batch, as_of=on)
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "files_confirmed": draft.get("files_confirmed"),
        "purpose_confirmed": draft.get("purpose_confirmed"),
        "intake_capped": len(files) > 12,
        "file_count": len(draft.get("files") or []),
        "actions_taken": draft.get("actions_taken"),
        "content_recorded": False,
    }


def policy_mapping(clause: object, *, on: str) -> dict:
    """A mapping is context. It is not a test result and it does not pass a control."""

    base = {
        "called": False,
        "experiment_id": "exp-69-policy-control-mapping",
        "is_a_test_result": False,
        "control_met_by_mapping": False,
        "human_approval": None,
        "mapping_count": 0,
        "mappings": [],
    }
    if not isinstance(clause, str) or not clause.strip():
        base["reason"] = "no_policy_clause"
        return base
    folder = EXPERIMENTS / "69-policy-control-mapping" / "fixtures"
    library = json.loads((folder / "library.json").read_text(encoding="utf-8"))
    directory = json.loads((folder / "directory.json").read_text(encoding="utf-8"))
    request = {
        "synthetic": True,
        "caller_ref": "CTL-OWN-1001",
        "policies": [
            {
                "policy_id": "ctl-clause",
                "title": "Pinned control clause",
                "document_date": "2026-01-01",
                "marking": "OFFICIAL",
                "legal_hold": False,
                "clauses": [{"clause_ref": "1.1", "text": clause}],
            }
        ],
    }
    result = map_controls()(request, library, directory, on)
    mappings = []
    for row in result.get("mappings") or []:
        mappings.append(
            {
                "control_id": row.get("control_id"),
                "confidence": row.get("confidence"),
                "qualified": row.get("qualified"),
                "quote_present": bool(row.get("quote")),
            }
        )
    base.update(
        {
            "called": True,
            "reason": None,
            "control_met_ignored": result.get("control_met"),
            "mapping_count": len(mappings),
            "mappings": mappings,
            "gap_count": len(result.get("gaps") or []),
            "unmapped_count": len(result.get("unmapped_statements") or []),
        }
    )
    base["control_met_by_mapping"] = False
    base["is_a_test_result"] = False
    base["human_approval"] = None
    return base
