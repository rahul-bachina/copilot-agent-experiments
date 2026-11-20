"""Call Experiments 12, 36, 03, and 08 under private module names.

Experiment 12 intake() does not confirm the file. Experiment 36 compare()
does not choose a source. Experiment 03's screen and injection check do not
clear this agent. Experiment 08 propose() does not return a reversible vault.
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
    "review",
    "reuse",
    "clauses",
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
    "architecture_bridge",
    "instruction_bridge",
    "manifest_bridge",
    "compare",
    "siblings",
    "drafts",
    "evaluations",
    "inventory",
    "pack",
    "lifecycle",
    "statements",
    "library",
    "mapping",
    "map_controls",
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


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_policy_mapping",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def intake_module():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_policy_mapping",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module


def compare_module():
    module = _load(
        "36-cross-source-validation",
        "compare.py",
        "exp36_compare_for_policy_mapping",
    )
    if not hasattr(module, "compare"):
        raise NeighbourMissing("36-cross-source-validation")
    return module


def assurance_modules() -> dict:
    drafts = _load(
        "03-agent-inventory-atrs-assurance",
        "drafts.py",
        "exp03_drafts_for_policy_mapping",
    )
    evaluations = _load(
        "03-agent-inventory-atrs-assurance",
        "evaluations.py",
        "exp03_evaluations_for_policy_mapping",
    )
    return {"drafts": drafts, "evaluations": evaluations}


def redact_uk_identifiers(text: str, *, rules_as_of: date | None) -> dict:
    def _run():
        return propose()(
            text,
            caller="exp-69-policy-control-mapping",
            now=datetime(rules_as_of.year, rules_as_of.month, rules_as_of.day) if rules_as_of else None,
            rules_as_of=rules_as_of,
            apply_model_suggestions=False,
            reversible=False,
        )

    proposal = _isolated(_run)
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
        "rules_stale": bool((proposal.get("audit_log") or {}).get("rules_stale")),
        "rules_pinned_on": (proposal.get("audit_log") or {}).get("rules_pinned_on"),
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
    }


def intake_policies(files: list[dict], *, as_of: date) -> dict:
    module = intake_module()
    batch = {"synthetic": True, "batch_id": "policy-set", "files": files}

    def _run():
        return module.intake(batch, as_of=as_of)

    draft = _isolated(_run)
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "files_confirmed": draft.get("files_confirmed"),
        "purpose_confirmed": draft.get("purpose_confirmed"),
        "any_document_not_current": draft.get("any_document_not_current"),
        "any_document_stale": draft.get("any_document_stale"),
        "catalogue_stale": draft.get("catalogue_stale"),
        "actions_taken": draft.get("actions_taken"),
        "files": [
            {
                "file_id": row.get("file_id"),
                "read_status": row.get("read_status"),
                "date_status": row.get("date_status"),
                "content_recorded": row.get("content_recorded"),
            }
            for row in draft.get("files") or []
        ],
    }


def compare_obligations(pack: dict, as_of: str) -> dict:
    module = compare_module()

    def _run():
        return module.compare(pack, as_of)

    draft = _isolated(_run)
    facts = []
    for fact in draft.get("facts") or []:
        facts.append(
            {
                "fact_key": fact.get("fact_key"),
                "classification": fact.get("classification"),
                "reason": fact.get("reason"),
                "agent_chose_source": fact.get("agent_chose_source"),
                "resolved": fact.get("resolved"),
            }
        )
    return {
        "called": True,
        "experiment_id": "exp-36-cross-source-validation",
        "agent_chose_source": draft.get("agent_chose_source"),
        "records_edited": draft.get("records_edited"),
        "all_material_resolved": draft.get("all_material_resolved"),
        "facts": facts,
        "kind_used": "register_extract",
        "kind_note": "Experiment 36 has no policy kind. register_extract is the permitted kind used here.",
    }


def assurance(text: str) -> dict:
    modules = assurance_modules()

    def _run():
        record = {
            "inventory_id": "exp-69-policy-control-mapping",
            "name": "Policy control mapping",
            "processing_regime": "general",
            "processes_personal_data": "yes",
            "meaningful_human_involvement": "yes",
            "significant_effect": "none",
            "profiling": "no",
            "special_category_data": "unknown",
            "lawful_basis": "",
            "sector": "public",
            "significant_effect_note": (
                "A mapping proposal is not a decision about a person. "
                "Wider uses of the same policies were not screened."
            ),
            "source_reviewed_on": "2026-11-20",
            "policies": text[:4000],
        }
        injection = modules["evaluations"].evaluate_injection(record, extra_text=text[:4000])
        handled = modules["evaluations"].handle_untrusted(record, text[:4000], {"approved": False})
        screen = modules["drafts"].screen_duaa(record)
        return injection, handled, screen

    injection, handled, screen = _isolated(_run)
    return {
        "called": True,
        "experiment_id": "exp-03-agent-inventory-atrs-assurance",
        "injection_cleared": injection.get("cleared"),
        "injection_approved": injection.get("approved"),
        "injection_finding_count": injection.get("finding_count"),
        "injection_codes": [row.get("code") for row in injection.get("findings") or []],
        "untrusted_approved": handled.get("approved"),
        "untrusted_actions_taken": handled.get("actions_taken"),
        "dataverse_written": handled.get("dataverse_written"),
        "screen_result": screen.get("screen_result"),
        "screen_approved": screen.get("approved"),
        "screen_determination": screen.get("determination"),
        "screen_clears_agent": False,
        "atrs_record_produced": False,
    }
