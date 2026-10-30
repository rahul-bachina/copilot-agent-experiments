#!/usr/bin/env python3
"""Draft an intake classification. Do not approve the use case.

The same proposal and the same as-of date produce the same JSON. Free text
is not an input to the rules. Autonomy A3 is never the suggestion.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from atrs import OUTSIDE_KINDS, WIDER_PUBLIC_KINDS, atrs_position
    from injection import signals_in, strip_instruction_sentences, strip_prohibited
    from patterns import match_pattern
    from reuse import (
        draft_assurance,
        experiment_14_stale,
        neighbour_pins,
        score_autonomy,
        screen_dpia,
    )
    from risk import risk_tier
    from sources import (
        ARTICLE_35_1,
        ARTICLE_35_3_INTRO,
        ARTICLE_35_4_NOTE,
        HARNESS_OVERVIEW_URL,
        PINNED_ON,
        STALE_AFTER_DAYS,
        UK_GDPR_ARTICLE_35_URL,
    )
else:
    from .atrs import OUTSIDE_KINDS, WIDER_PUBLIC_KINDS, atrs_position
    from .injection import signals_in, strip_instruction_sentences, strip_prohibited
    from .patterns import match_pattern
    from .reuse import (
        draft_assurance,
        experiment_14_stale,
        neighbour_pins,
        score_autonomy,
        screen_dpia,
    )
    from .risk import risk_tier
    from .sources import (
        ARTICLE_35_1,
        ARTICLE_35_3_INTRO,
        ARTICLE_35_4_NOTE,
        HARNESS_OVERVIEW_URL,
        PINNED_ON,
        STALE_AFTER_DAYS,
        UK_GDPR_ARTICLE_35_URL,
    )

LABEL = "DRAFT FOR THE GOVERNANCE TEAM"
CATALOGUE_ID = "G001"
CALLER = "exp-24-agent-use-case-intake"

SECTOR_FOR_EXPERIMENT_03 = {
    "government_department": "public",
    "alb_public_or_frontline": "public",
    "alb_other": "public",
    "local_authority": "public",
    "police": "public",
    "wider_public_sector": "public",
    "fca_firm": "fca_firm",
    "private": "other",
}


class IntakeForbidden(RuntimeError):
    """The agent has no approve, reject, or provision path."""


def approve_use_case(*_args, **_kwargs) -> None:
    raise IntakeForbidden("the agent does not approve a use case")


def reject_use_case(*_args, **_kwargs) -> None:
    raise IntakeForbidden("the agent does not reject a use case")


def provision_agent(*_args, **_kwargs) -> None:
    raise IntakeForbidden("the agent does not provision an agent")


def record_governance_decision(*_args, **_kwargs) -> None:
    raise IntakeForbidden("the agent does not record the governance team's decision")


def _parse_as_of(value: date | str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("as_of must be YYYY-MM-DD") from exc
    raise ValueError("as_of must be YYYY-MM-DD")


def _refused() -> dict[str, Any]:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": "A1",
        "refused": True,
        "reason": "This starter only reads a proposal marked synthetic. The text has not been copied.",
        "classification": None,
        "approved": False,
        "use_case_approved": False,
        "use_case_rejected": False,
        "provisioned": False,
        "governance_decision": None,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
    }


def _strings(node: Any) -> list[str]:
    found: list[str] = []
    if isinstance(node, str):
        found.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            found.extend(_strings(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_strings(value))
    return found


def _block(proposal: dict, key: str) -> dict:
    value = proposal.get(key)
    return value if isinstance(value, dict) else {}


def _tri(block: dict, key: str) -> str:
    value = block.get(key)
    if value in {"yes", "no", "unknown"}:
        return value
    return "unknown"


def _systems(proposal: dict) -> list[str]:
    raw = proposal.get("systems_touched")
    if not isinstance(raw, list):
        return []
    kept = []
    for item in raw:
        if isinstance(item, str) and item.strip() and not signals_in(item):
            kept.append(item.strip())
    return kept


def _architecture_case(proposal: dict, proposal_id: str) -> dict:
    data = _block(proposal, "data")
    users = _block(proposal, "users")
    decisions = _block(proposal, "decisions_affected")
    work = _block(proposal, "work")
    organisation = _block(proposal, "organisation")
    licences = organisation.get("licences") if isinstance(organisation.get("licences"), dict) else {}
    wanted = proposal.get("autonomy_wanted")
    if wanted not in {"A0", "A1", "A2", "A3"}:
        wanted = None
    personal = data.get("personal_data") == "yes"
    special = data.get("special_category") == "yes"
    actions = {
        "read": True,
        "draft": True,
        "classify": True,
        "create_files": work.get("create_files") is True,
        "fixed_workflow": work.get("fixed_workflow") is True,
        "multi_step_reasoning": work.get("multi_step_reasoning") is True,
        "long_running": work.get("long_running") is True,
        "needs_custom_code": work.get("needs_custom_code") is True,
        "needs_model_choice": work.get("needs_model_choice") is True,
        "needs_private_network": work.get("needs_private_network") is True,
        "needs_evaluations": work.get("needs_evaluations") is True,
        "production_write": decisions.get("production_write") is True,
        "external_send": decisions.get("external_send") is True,
        "spend": decisions.get("spend") is True,
        "approve_or_reject": decisions.get("approve_or_reject") is True,
        "regulated_decision": decisions.get("regulated_decision") is True,
    }
    return {
        "case_id": proposal_id,
        "title": proposal_id,
        "organisation": {
            "name": proposal_id,
            "sector": "not_recorded",
            "licences": {
                "copilot_studio": licences.get("copilot_studio", "unknown"),
                "microsoft_365_copilot": licences.get("microsoft_365_copilot", "unknown"),
                "power_automate": licences.get("power_automate", "unknown"),
                "foundry": licences.get("foundry", "unknown"),
                "github_copilot_service_only": licences.get("github_copilot_service_only") is True,
            },
        },
        "users": {
            "audience": users.get("audience", "internal_staff"),
            "channel": users.get("channel", "none"),
        },
        "data": {
            "description": "",
            "personal_data": personal,
            "special_category": special,
            "classification": data.get("classification", "unknown"),
            "volume": data.get("volume", "bounded"),
            "residency": data.get("residency", "unknown"),
        },
        "actions": actions,
        "risk": {
            "requested_autonomy": wanted,
            "named_approver": proposal.get("named_human_approver") is True,
            "approver_role": "",
            "significant_automated_decision": decisions.get("significant_automated_decision") is True,
        },
        "narrative": "",
    }


def _inventory(proposal: dict, proposal_id: str, suggested: str, as_of: date) -> dict | None:
    organisation = _block(proposal, "organisation")
    kind = organisation.get("kind")
    sector = SECTOR_FOR_EXPERIMENT_03.get(kind)
    if sector is None:
        return None
    data = _block(proposal, "data")
    decisions = _block(proposal, "decisions_affected")
    automated = _block(proposal, "automated_decision")
    record = {
        "inventory_id": proposal_id,
        "name": proposal_id,
        "sector": sector,
        "lifecycle_status": "proposed",
        "autonomy_level": suggested,
        "organisation_name": proposal_id,
        "source_reviewed_on": as_of.isoformat(),
        "processing_regime": automated.get("processing_regime", "unknown"),
        "processes_personal_data": _tri(data, "personal_data"),
        "special_category_data": _tri(data, "special_category"),
        "meaningful_human_involvement": _tri(automated, "meaningful_human_involvement"),
        "significant_effect": decisions.get("significant_effect")
        if decisions.get("significant_effect") in {"legal", "similarly_significant", "none", "unknown"}
        else "unknown",
        "profiling": _tri(automated, "profiling"),
        "explicit_consent": _tri(automated, "explicit_consent"),
        "article_9_2_g": _tri(automated, "article_9_2_g"),
        "contract_or_authorised_by_law": _tri(automated, "contract_or_authorised_by_law"),
        "safeguard_information": _tri(automated, "safeguard_information"),
        "safeguard_representations": _tri(automated, "safeguard_representations"),
        "safeguard_human_intervention": _tri(automated, "safeguard_human_intervention"),
        "safeguard_contest": _tri(automated, "safeguard_contest"),
    }
    basis = automated.get("lawful_basis")
    if isinstance(basis, str):
        record["lawful_basis"] = basis
    return record


def _pattern_text(proposal: dict) -> str:
    parts = []
    for key in ("problem", "narrative"):
        value = proposal.get(key)
        if isinstance(value, str):
            parts.append(strip_instruction_sentences(value))
    users = _block(proposal, "users")
    decisions = _block(proposal, "decisions_affected")
    data = _block(proposal, "data")
    for value in (users.get("who"), decisions.get("description"), data.get("involved")):
        if isinstance(value, str):
            parts.append(strip_instruction_sentences(value))
    return " ".join(parts)


def _approval_points(a3: bool, stale: bool) -> list[dict[str, Any]]:
    points = [
        {
            "action": "Approve or change the intake classification",
            "approver": "Governance team",
            "mandatory": True,
            "recorded_by_this_agent": False,
        }
    ]
    if a3:
        points.append(
            {
                "action": "Decide what to do with a request for autonomy A3",
                "approver": "Governance team",
                "mandatory": True,
                "recorded_by_this_agent": False,
                "rationale": "A3 is out of scope. The suggested level is not A3. The agent does not approve the use case.",
            }
        )
    points.append(
        {
            "action": "Treat a DPIA indication as a reason to start a DPIA",
            "approver": "Privacy officer",
            "mandatory": True,
            "recorded_by_this_agent": False,
        }
    )
    points.append(
        {
            "action": "Treat an ATRS indication as a reason to draft a record",
            "approver": "Governance team",
            "mandatory": True,
            "recorded_by_this_agent": False,
        }
    )
    if stale:
        points.append(
            {
                "action": "Re-open a pinned page before relying on a citation",
                "approver": "Governance team",
                "mandatory": True,
                "recorded_by_this_agent": False,
            }
        )
    return points


def _age_stale(as_of: date, pinned: date, stale_after_days: int) -> bool:
    return (as_of - pinned).days > stale_after_days


def classify(proposal: dict, *, as_of: date | str, stale_after_days: int = STALE_AFTER_DAYS) -> dict[str, Any]:
    """Return a draft classification. Approval stays null."""

    opened = _parse_as_of(as_of)
    if not isinstance(stale_after_days, int) or isinstance(stale_after_days, bool) or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if not isinstance(proposal, dict) or proposal.get("synthetic") is not True:
        return _refused()

    cleaned, stripped_keys = strip_prohibited(proposal)
    if not isinstance(cleaned, dict):
        return _refused()
    signals = signals_in(cleaned)
    proposal_id = cleaned.get("proposal_id")
    if not isinstance(proposal_id, str) or not proposal_id.strip():
        proposal_id = "unspecified"

    organisation = _block(cleaned, "organisation")
    kind = organisation.get("kind")
    atrs = atrs_position(
        kind,
        cleaned.get("significant_influence_on_a_decision_with_public_effect"),
        cleaned.get("public_interaction"),
    )
    tier = risk_tier(cleaned)
    architecture = score_autonomy(_architecture_case(cleaned, proposal_id))
    suggested = architecture["recommended_autonomy"]
    if suggested not in {"A0", "A1", "A2"}:
        raise IntakeForbidden("suggested autonomy must be A0, A1, or A2")
    wanted = cleaned.get("autonomy_wanted")
    a3 = wanted == "A3"

    article_answers = cleaned.get("article_35_answers")
    if not isinstance(article_answers, dict):
        article_answers = {}
    view = cleaned.get("article_35_1_view", "unknown")
    if not isinstance(view, str):
        view = "unknown"
    dpia = screen_dpia(article_answers, view)

    inventory = _inventory(cleaned, proposal_id, suggested, opened)
    if inventory is None:
        assurance = {
            "experiment": "03-agent-inventory-atrs-assurance",
            "catalogue_id": "G010",
            "called": False,
            "reason": "organisation.kind is not one Experiment 03 can take as a sector",
            "manifest_generator_called": False,
            "atrs_approved": False,
            "duaa_lawful": None,
            "actions_taken": [],
        }
    else:
        assurance = draft_assurance(inventory)

    pattern = match_pattern(
        cleaned.get("pattern_hint") if isinstance(cleaned.get("pattern_hint"), str) else None,
        _pattern_text(cleaned),
    )

    pins = neighbour_pins()
    our_stale = _age_stale(opened, PINNED_ON, stale_after_days)
    exp14_stale = experiment_14_stale(opened, stale_after_days)
    exp19_stale = _age_stale(opened, date.fromisoformat(pins["experiment_19_sources_pinned_on"]), stale_after_days)
    exp03_stale = _age_stale(opened, date.fromisoformat(pins["experiment_03_atrs_retrieved_on"]), stale_after_days)
    stale = our_stale or exp14_stale or exp19_stale or exp03_stale

    flags = []
    if wanted not in {"A0", "A1", "A2", "A3"}:
        flags.append("autonomy_wanted_not_recognised")
    if a3:
        flags.append("autonomy_a3_out_of_scope")
    if organisation.get("fictional") is False:
        flags.append("organisation_not_marked_fictional")
    if pattern.get("hint_rejected"):
        flags.append("pattern_hint_not_recognised")
    if stripped_keys:
        flags.append("prohibited_payload_keys_removed")

    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": "A1",
        "caller": CALLER,
        "refused": False,
        "proposal_id": proposal_id,
        "synthetic": True,
        "classification": {
            "suggested_autonomy": suggested,
            "autonomy_wanted": wanted if wanted in {"A0", "A1", "A2", "A3"} else None,
            "a3_requested": a3,
            "a3_out_of_scope": a3,
            "a3_recommended": False,
            "risk_tier": tier["risk_tier"],
            "risk_rules": tier["rules"],
            "risk_gaps": tier["gaps"],
            "risk_tier_is_a_legal_finding": False,
            "dpia_likely_needed": dpia["dpia_likely_needed"],
            "dpia_required": None,
            "dpia_required_decided_by_this_tool": False,
            "atrs_likely_needed": atrs["atrs_likely_needed"],
            "atrs_basis": atrs["atrs_basis"],
            "atrs_scope_decided_by_this_tool": False,
            "resembles": pattern["resembles"],
            "resemble_candidates": pattern["candidates"],
        },
        "approved": False,
        "use_case_approved": False,
        "use_case_rejected": False,
        "provisioned": False,
        "governance_decision": None,
        "governance_may_change_the_classification": True,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "systems_touched": _systems(cleaned),
        "systems_are_not_permissions": True,
        "sources_pinned_on": PINNED_ON.isoformat(),
        "sources_stale": stale,
        "rules_current": not stale,
        "stale_detail": {
            "this_experiment": our_stale,
            "experiment_14": exp14_stale,
            "experiment_19": exp19_stale,
            "experiment_03": exp03_stale,
        },
        "neighbour_pins": pins,
        "prompt_injection": {
            "detected": bool(signals),
            "followed": False,
            "signals": signals,
            "stripped_keys": stripped_keys,
        },
        "flags": flags,
        "experiment_14": architecture,
        "experiment_19": dpia,
        "experiment_03": assurance,
        "atrs": {
            "likely_needed": atrs["atrs_likely_needed"],
            "basis": atrs["atrs_basis"],
            "note": atrs["note"],
            "scope_decided_by_this_tool": False,
            "may_be_emailed": False,
            "scope_policy_opened": False,
        },
        "article_35": {
            "url": UK_GDPR_ARTICLE_35_URL,
            "paragraph_1": ARTICLE_35_1,
            "paragraph_3_intro": ARTICLE_35_3_INTRO,
            "paragraph_4_note": ARTICLE_35_4_NOTE,
            "opened_on": PINNED_ON.isoformat(),
        },
        "harness_overview_url": HARNESS_OVERVIEW_URL,
        "human_approval_points": _approval_points(a3, stale),
        "sector_passed_to_experiment_03": None if inventory is None else inventory["sector"],
        "wider_public_sector_kinds": sorted(WIDER_PUBLIC_KINDS),
        "outside_public_sector_kinds": sorted(OUTSIDE_KINDS),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft an intake classification. Does not approve a use case or provision anything."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=STALE_AFTER_DAYS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("The input JSON must be an object")
    draft = classify(payload, as_of=args.as_of, stale_after_days=args.stale_after_days)
    text = json.dumps(draft, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
