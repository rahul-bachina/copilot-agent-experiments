#!/usr/bin/env python3
"""Assemble a draft approval pack. The named approver decides.

The agent does not approve, reject, sign, submit, pay, or send. The only
record of a decision is record_approver_decision, and only when the named
directory approver matches the agent-held pack and its hash.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cues import category_hit, concern_hits
    from dates import as_date, parse_date
    from evidence import review_evidence
    from marking import RANK, above_ceiling
    from mask import suppress_request_fields
    from reuse import digest, identifier_counts, neighbour_hashes
    from routing import (
        approver_problem,
        combine_amounts,
        delegation_diff,
        eligible_refs,
        id_diff,
        matching_rules,
        people,
        person,
    )
    from sources import (
        AUTONOMY,
        CATALOGUE_ID,
        DECISIONS,
        EXPERIMENT_ID,
        LABEL,
        PROHIBITED_DECISIONS,
        PROHIBITED_REQUEST_KEYS,
        REQUEST_TYPES,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        limitations,
        pinned_sources,
        uk_context,
    )
else:
    from .cues import category_hit, concern_hits
    from .dates import as_date, parse_date
    from .evidence import review_evidence
    from .marking import RANK, above_ceiling
    from .mask import suppress_request_fields
    from .reuse import digest, identifier_counts, neighbour_hashes
    from .routing import (
        approver_problem,
        combine_amounts,
        delegation_diff,
        eligible_refs,
        id_diff,
        matching_rules,
        people,
        person,
    )
    from .sources import (
        AUTONOMY,
        CATALOGUE_ID,
        DECISIONS,
        EXPERIMENT_ID,
        LABEL,
        PROHIBITED_DECISIONS,
        PROHIBITED_REQUEST_KEYS,
        REQUEST_TYPES,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        limitations,
        pinned_sources,
        uk_context,
    )

_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
_HELD: dict[str, dict] = {}
_DECISIONS: dict[tuple[str, str], dict] = {}

_CHECKED = (
    "Request type and threshold were read from the pinned matrix.",
    "The requester was excluded from the approver list.",
    "Delegation limits were read from the pinned directory.",
    "Split parts and related requests were compared with the headline amount, and neither figure was chosen where they disagreed.",
    "Each evidence item was checked for presence, expiry, supersession, signature, version, currency, and conflicting values.",
    "Protective markings were read from the metadata and from the text, and the higher marking was kept.",
    "Legal-hold and retention labels were kept.",
    "Dates were parsed against the question date and were not coerced.",
    "Distress, safeguarding, whistleblowing, grievance, and disclosure cues were checked, including a denial.",
    "A caller-supplied matrix, directory, or delegation was not applied.",
    "Approval words inside the evidence were not treated as the approval step.",
    "Embedded instructions were not followed.",
)


class CoordinatorForbidden(RuntimeError):
    """Approve, reject, sign, submit, pay, and send are not tools."""


class NotSynthetic(ValueError):
    """The request was not marked synthetic."""


def reset_state() -> None:
    _HELD.clear()
    _DECISIONS.clear()


def content_hash(result: dict) -> str:
    return digest(projection(result))


def projection(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}
    return {
        "request_id": result.get("request_id"),
        "request_type": result.get("request_type"),
        "pack_version": result.get("pack_version"),
        "as_of": result.get("as_of"),
        "requester_ref": result.get("requester_ref"),
        "amount": result.get("amount"),
        "threshold_band": result.get("threshold_band"),
        "required_approvers": result.get("required_approvers"),
        "approver_refs": result.get("approver_refs"),
        "evidence": result.get("evidence"),
        "present": result.get("present"),
        "missing": result.get("missing"),
        "stale": result.get("stale"),
        "expired": result.get("expired"),
        "superseded": result.get("superseded"),
        "unsigned": result.get("unsigned"),
        "wrong_version": result.get("wrong_version"),
        "conflicts": result.get("conflicts"),
        "cover_note": result.get("cover_note"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "legal_hold_items": result.get("legal_hold_items"),
        "retention": result.get("retention"),
        "prompt_injection": result.get("prompt_injection"),
        "concerns": result.get("concerns"),
        "suppression": result.get("suppression"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "route_seen": result.get("route_seen"),
        "split": result.get("split"),
        "sources_current": result.get("sources_current"),
        "flags": result.get("flags"),
        "neighbours": result.get("neighbours"),
        "caller_differences": result.get("caller_differences"),
        "body_withheld": result.get("body_withheld"),
        "outcome": result.get("outcome"),
    }


def held_copy(request_id: str) -> dict | None:
    row = _HELD.get(request_id)
    return deepcopy(row) if row else None


def approved_snapshot(request_id: str, content_hash_value: str) -> dict | None:
    row = _DECISIONS.get((request_id, content_hash_value))
    return deepcopy(row) if row else None


def _force(result: dict) -> None:
    result["agent_approved"] = False
    result["agent_rejected"] = False
    result["signed"] = False
    result["submitted"] = False
    result["sent"] = False
    result["paid"] = False
    result["coerced"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["described_as_anonymised"] = False
    result["caller_matrix_applied"] = False
    result["caller_directory_applied"] = False
    result["caller_delegation_applied"] = False
    result["marked_acceptable"] = False
    result["value_chosen_on_conflict"] = False
    flags = result.get("flags")
    if isinstance(flags, dict):
        for key in (
            "agent_approved",
            "agent_rejected",
            "signed",
            "submitted",
            "sent",
            "paid",
            "coerced",
            "instructions_followed",
            "approval_marker_trusted",
            "described_as_anonymised",
            "caller_matrix_applied",
            "caller_directory_applied",
            "caller_delegation_applied",
            "marked_acceptable",
            "value_chosen_on_conflict",
            "self_approval_allowed",
            "split_applied_as_under_threshold",
            "leading_applied",
            "role_in_text_trusted",
        ):
            flags[key] = False


def _flags() -> dict:
    return {
        "agent_approved": False,
        "agent_rejected": False,
        "signed": False,
        "submitted": False,
        "sent": False,
        "paid": False,
        "coerced": False,
        "instructions_followed": False,
        "approval_marker_trusted": False,
        "described_as_anonymised": False,
        "caller_matrix_applied": False,
        "caller_directory_applied": False,
        "caller_delegation_applied": False,
        "marked_acceptable": False,
        "value_chosen_on_conflict": False,
        "self_approval_allowed": False,
        "split_applied_as_under_threshold": False,
        "leading_applied": False,
        "role_in_text_trusted": False,
    }


def assemble_pack(request: dict, as_of: str) -> dict:
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    question_reading = parse_date(as_of)
    question = as_date(question_reading)
    if question is None or question_reading.get("ambiguous"):
        raise ValueError("as_of must be an unambiguous calendar date")
    working, ignored = _strip(request)
    request_id = working.get("request_id")
    if not isinstance(request_id, str) or not _REQUEST_ID.fullmatch(request_id):
        raise ValueError("request_id must be 1 to 80 letters, digits, hyphens, or underscores")
    pinned = pinned_sources()
    directory = pinned["directory"]
    matrix = pinned["matrix"]
    checklist = pinned["checklist"]
    request_type = working.get("request_type") if working.get("request_type") in REQUEST_TYPES else None
    type_unreadable = request_type is None
    severity = working.get("severity") if isinstance(working.get("severity"), str) else None
    change_class = working.get("change_class") if isinstance(working.get("change_class"), str) else None
    if request_type == "policy_exception" and severity not in {"low", "medium", "high"}:
        severity = None
    if request_type == "change" and change_class not in {"standard", "normal", "emergency"}:
        change_class = None
    texts = _texts(working)
    blob = "\n".join(texts)
    amount = combine_amounts(working, matrix, blob)
    rules = []
    if request_type == "spend" and amount["routing_pence"] is not None and not amount["conflicting"] and not amount["unreadable"]:
        rules = matching_rules(matrix, "spend", amount["routing_pence"], None, None)
    elif request_type == "policy_exception" and severity:
        rules = matching_rules(matrix, "policy_exception", None, severity, None)
    elif request_type == "change" and change_class:
        rules = matching_rules(matrix, "change", None, None, change_class)
    rule = rules[0] if len(rules) == 1 else None
    matrix_ambiguous = len(rules) > 1
    requester = working.get("requester_ref")
    required = []
    approver_refs: list[str] = []
    if rule:
        for role in rule.get("approver_roles") or []:
            if not isinstance(role, str):
                continue
            refs = eligible_refs(directory, role, requester, request_type, amount["routing_pence"])
            required.append({"role": role, "employee_refs": refs, "gap": not refs})
            for ref in refs:
                if ref not in approver_refs:
                    approver_refs.append(ref)
    ceiling = _ceiling(directory, approver_refs) if approver_refs else "OFFICIAL"
    evidence = review_evidence(
        working.get("evidence"),
        checklist,
        request_type=request_type,
        routing_pence=amount["routing_pence"] if request_type == "spend" else None,
        severity=severity,
        change_class=change_class,
        supplier_name=working.get("supplier_name"),
        as_of=question,
        requester_ref=requester,
        ceiling=ceiling if ceiling in RANK else None,
        digest=digest,
    )
    neighbour = neighbour_hashes(
        [
            {
                "evidence_id": item.get("evidence_id"),
                "title": item.get("checklist_id"),
                "content": item.get("content"),
                "document_date": item.get("document_date") if isinstance(item.get("document_date"), str) else None,
            }
            for item in working.get("evidence") or []
            if isinstance(item, dict)
        ],
        on=question,
    )
    for row in evidence["items"]:
        row["citation"]["evidence_sha256"] = (neighbour.get("item_sha256") or {}).get(row["evidence_id"])
    identifiers = identifier_counts(blob, on=question)
    concerns = concern_hits(blob)
    concerns["cue_copied"] = False
    concerns["routed_to_human"] = bool(concerns["any"])
    leading = category_hit(blob, "leading_criterion")
    forged = category_hit(blob, "forged_approval")
    instructed = category_hit(blob, "embedded_instruction")
    self_declared = category_hit(blob, "self_declared")
    signals = []
    if instructed:
        signals.append("embedded_instruction")
    if forged:
        signals.append("forged_approval")
    if self_declared:
        signals.append("self_declared_status")
    suppression = suppress_request_fields(working, texts)
    caller_differences = {
        "matrix": id_diff(working.get("caller_matrix"), {row.get("rule_id") for row in matrix.get("rules") or [] if isinstance(row, dict)}, "rule_id"),
        "directory": id_diff(working.get("caller_directory"), {row.get("employee_ref") for row in people(directory) if isinstance(row.get("employee_ref"), str)}, "employee_ref"),
        "delegation": delegation_diff(working.get("caller_delegation"), directory),
        "applied": False,
    }
    pinned_day = as_date(parse_date(SOURCES_PINNED_ON))
    sources_current = pinned_day is not None and (question - pinned_day).days <= STALE_AFTER_DAYS
    approver_gap = bool(rule) and any(row["gap"] for row in required)
    band = None if rule is None else {
        "rule_id": rule.get("rule_id"),
        "request_type": rule.get("request_type"),
        "roles": list(rule.get("approver_roles") or []),
        "matrix_is_statutory": False,
    }
    route = bool(
        concerns["any"]
        or leading
        or type_unreadable
        or matrix_ambiguous
        or approver_gap
        or evidence["body_withheld"]
        or amount["conflicting"]
        or amount["unreadable"]
        or (request_type == "policy_exception" and severity is None)
        or (request_type == "change" and change_class is None)
        or rule is None
    )
    gaps = bool(
        evidence["missing"]
        or evidence["stale"]
        or evidence["expired"]
        or evidence["superseded"]
        or evidence["unsigned"]
        or evidence["wrong_version"]
        or evidence["support_gaps"]
        or evidence["dates_unreadable"]
    )
    if route:
        outcome = "route_to_human"
    elif gaps or evidence["conflicting"] or evidence["superseded"]:
        outcome = "draft_with_gaps"
    else:
        outcome = "ready_for_approver"
    acknowledgements = ["pins_seen"]
    if gaps or evidence["carve_outs"]:
        acknowledgements.append("gaps_seen")
    if evidence["conflicting"] or amount["conflicting"]:
        acknowledgements.append("conflicts_seen")
    if evidence["marking"]["applied"]:
        acknowledgements.append("markings_seen")
    if evidence["dates_unreadable"] or amount["unreadable"]:
        acknowledgements.append("dates_seen")
    if not sources_current or any(caller_differences[name] for name in ("matrix", "directory", "delegation")):
        acknowledgements.append("sources_seen")
    if amount["split_cue"] or amount["split_to_dodge_threshold"] or amount["conflicting"]:
        acknowledgements.append("split_seen")
    if suppression["applied"] or suppression["unreadable"]:
        acknowledgements.append("suppression_seen")
    if leading:
        acknowledgements.append("leading_seen")
    if evidence["legal_hold"]:
        acknowledgements.append("hold_seen")
    cover = {
        "addressed_to": list(approver_refs),
        "present": list(evidence["present"]),
        "missing": list(evidence["missing"]),
        "stale": list(evidence["stale"]),
        "expired": list(evidence["expired"]),
        "superseded": list(evidence["superseded"]),
        "unsigned": list(evidence["unsigned"]),
        "wrong_version": list(evidence["wrong_version"]),
        "conflicting": evidence["conflicting"],
        "support_gaps": list(evidence["support_gaps"]),
        "carve_outs": list(evidence["carve_outs"]),
        "checked": list(_CHECKED),
        "what_the_approver_decides": "Whether to approve, reject, or return this pack. The agent does not decide.",
        "split_to_dodge_threshold": amount["split_to_dodge_threshold"],
        "approver_gap": approver_gap,
    }
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "request_id": request_id,
        "request_type": working.get("request_type") if isinstance(working.get("request_type"), str) else None,
        "pack_version": 1,
        "as_of": question.isoformat(),
        "requester_ref": requester if isinstance(requester, str) else None,
        "amount": {
            "pence": amount["routing_pence"],
            "gbp": amount["routing_gbp"],
            "unreadable": amount["unreadable"],
            "conflicting": amount["conflicting"],
            "coerced": False,
        },
        "threshold_band": band,
        "required_approvers": required,
        "approver_refs": approver_refs,
        "evidence": evidence["items"],
        "present": evidence["present"],
        "missing": evidence["missing"],
        "stale": evidence["stale"],
        "expired": evidence["expired"],
        "superseded": evidence["superseded"],
        "unsigned": evidence["unsigned"],
        "wrong_version": evidence["wrong_version"],
        "conflicts": evidence["conflicting"],
        "cover_note": cover,
        "marking": evidence["marking"],
        "legal_hold": evidence["legal_hold"],
        "legal_hold_items": evidence["legal_hold_items"],
        "retention": evidence["retention"],
        "body_withheld": evidence["body_withheld"],
        "prompt_injection": {
            "signals": signals,
            "followed": False,
            "approval_marker_in_text": forged,
            "approval_marker_trusted": False,
        },
        "concerns": concerns,
        "suppression": suppression,
        "required_acknowledgements": acknowledgements,
        "route_seen": False,
        "split": {
            "cue": amount["split_cue"],
            "split_to_dodge_threshold": amount["split_to_dodge_threshold"],
            "conflicting": amount["conflicting"],
            "unreadable": amount["unreadable"],
            "applied_as_under_threshold": False,
            "coerced": False,
        },
        "sources_current": sources_current,
        "flags": _flags(),
        "neighbours": {
            "experiment_18": neighbour,
            "experiment_74": {
                "called": True,
                "experiment_id": "exp-74-board-governance-pack",
                "function": "digest",
                "paper_hash_called": False,
                "reason_paper_hash_not_called": "A board paper projection is not this approval pack.",
                "decides_approval": False,
            },
            "experiment_08": identifiers,
        },
        "caller_differences": caller_differences,
        "outcome": outcome,
        "human_approval": None,
        "ignored_request_fields": ignored,
        "ignored_instructions": True,
        "uk_context": uk_context(),
        "limitations": limitations(),
        "type_unreadable": type_unreadable,
        "matrix_ambiguous": matrix_ambiguous,
        "severity_unreadable": request_type == "policy_exception" and severity is None,
        "change_class_unreadable": request_type == "change" and change_class is None,
        "may_be_relied_on": False,
    }
    _force(result)
    result["content_hash"] = content_hash(result)
    _HELD[request_id] = {
        "request_id": request_id,
        "content_hash": result["content_hash"],
        "projection": deepcopy(projection(result)),
        "pack_version": 1,
        "store": "synthetic",
    }
    return result


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named approver has seen a human route. Nothing is decided."""

    updated = deepcopy(result) if isinstance(result, dict) else {}
    updated["human_approval"] = None
    updated["staged"] = False
    problem = _bind_problem(result, directory, approval, item="route-seen", decision="seen")
    if problem:
        updated["blocked_reason"] = problem
        _force(updated)
        return updated
    if result.get("outcome") != "route_to_human":
        updated["blocked_reason"] = "route_not_required"
        _force(updated)
        return updated
    reason = _person_problem(result, approval.get("approver_ref"), allow_over_limit=True)
    if reason:
        updated["blocked_reason"] = reason
        _force(updated)
        return updated
    updated["route_seen"] = True
    updated["pack_version"] = int(result.get("pack_version") or 1) + 1
    updated["concerns"] = deepcopy(result.get("concerns"))
    if isinstance(updated["concerns"], dict):
        updated["concerns"]["cue_copied"] = False
    _force(updated)
    updated["blocked_reason"] = None
    updated["content_hash"] = content_hash(updated)
    _HELD[result["request_id"]] = {
        "request_id": result["request_id"],
        "content_hash": updated["content_hash"],
        "projection": deepcopy(projection(updated)),
        "pack_version": updated["pack_version"],
        "store": "synthetic",
    }
    return updated


def record_approver_decision(result: dict, directory: dict, approval: dict) -> dict:
    """Record the named approver's decision for the agent-held pack. The agent does not decide."""

    updated = deepcopy(result) if isinstance(result, dict) else {}
    updated["human_approval"] = None
    updated["staged"] = False
    updated["decisions_complete"] = False
    if isinstance(approval, dict) and approval.get("decision") in PROHIBITED_DECISIONS:
        updated["blocked_reason"] = "consequential_action_is_not_this_step"
        _force(updated)
        return updated
    problem = _bind_problem(result, directory, approval, item="approval-pack", decision=None)
    if problem:
        updated["blocked_reason"] = problem
        _force(updated)
        return updated
    decision = approval.get("decision")
    if decision not in DECISIONS:
        updated["blocked_reason"] = "wrong_item"
        _force(updated)
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        _force(updated)
        return updated
    reason = _person_problem(result, approval.get("approver_ref"), allow_over_limit=False)
    if reason:
        updated["blocked_reason"] = reason
        _force(updated)
        return updated
    if _above_clearance(result, approval.get("approver_ref")):
        updated["blocked_reason"] = "pack_above_approver_clearance"
        _force(updated)
        return updated
    if decision == "approve" and (result.get("amount") or {}).get("unreadable"):
        updated["blocked_reason"] = "amount_unreadable"
        _force(updated)
        return updated
    if decision == "approve" and (result.get("amount") or {}).get("conflicting"):
        updated["blocked_reason"] = "amount_unresolved"
        _force(updated)
        return updated
    if not result.get("approver_refs") and decision == "approve":
        updated["blocked_reason"] = "no_eligible_approver"
        _force(updated)
        return updated
    ack = _ack(result, approval)
    if ack:
        updated["blocked_reason"] = ack
        _force(updated)
        return updated
    request_id = result["request_id"]
    held_hash = result["content_hash"]
    key = (request_id, held_hash)
    snapshot = _DECISIONS.get(key)
    if snapshot is None:
        snapshot = _blank_snapshot(result)
        _DECISIONS[key] = snapshot
    previous = snapshot["by_approver"].get(approval.get("approver_ref"))
    if previous is not None and previous != decision:
        updated["blocked_reason"] = "decision_conflicts_with_recorded"
        _force(updated)
        return updated
    snapshot["by_approver"][approval["approver_ref"]] = decision
    complete, agreed = _complete(result, snapshot["by_approver"])
    snapshot["decisions_complete"] = complete
    snapshot["decision"] = agreed
    snapshot["disagreement"] = bool(snapshot["by_approver"]) and agreed is None and _roles_spoken(result, snapshot["by_approver"])
    updated["blocked_reason"] = None
    updated["staged"] = complete
    updated["decisions_complete"] = complete
    updated["human_approval"] = {
        "recorded": complete,
        "partial": not complete,
        "decision": agreed,
        "by_approver": dict(snapshot["by_approver"]),
        "approver_ref": approval["approver_ref"],
        "content_hash": held_hash,
        "agent_approved": False,
        "agent_rejected": False,
        "signed": False,
        "submitted": False,
        "sent": False,
        "paid": False,
    }
    updated["content_hash"] = held_hash
    updated["staging_store"] = "synthetic"
    _force(updated)
    return updated


def _blank_snapshot(result: dict) -> dict:
    held = _HELD[result["request_id"]]
    return {
        "projection": deepcopy(held["projection"]),
        "by_approver": {},
        "legal_hold": held["projection"].get("legal_hold"),
        "retention": deepcopy(held["projection"].get("retention")),
        "marking": deepcopy(held["projection"].get("marking")),
        "prompt_injection": deepcopy(held["projection"].get("prompt_injection")),
        "concerns": deepcopy(held["projection"].get("concerns")),
        "required_acknowledgements": deepcopy(held["projection"].get("required_acknowledgements")),
        "suppression": deepcopy(held["projection"].get("suppression")),
        "route_seen": held["projection"].get("route_seen"),
        "paid": False,
        "sent": False,
        "signed": False,
        "submitted": False,
        "agent_approved": False,
        "agent_rejected": False,
        "store": "synthetic",
        "decisions_complete": False,
        "decision": None,
        "disagreement": False,
    }


def _complete(result: dict, by_approver: dict) -> tuple[bool, str | None]:
    if not by_approver:
        return False, None
    decisions = set(by_approver.values())
    if len(decisions) != 1:
        return False, None
    agreed = next(iter(decisions))
    directory = pinned_sources()["directory"]
    for role_row in result.get("required_approvers") or []:
        refs = role_row.get("employee_refs") or []
        if not refs:
            return False, None
        spoken = False
        for ref, decision in by_approver.items():
            row = person(directory, ref)
            if row and row.get("role") == role_row.get("role") and ref in refs and decision == agreed:
                spoken = True
        if not spoken:
            return False, None
    return True, agreed


def _roles_spoken(result: dict, by_approver: dict) -> bool:
    directory = pinned_sources()["directory"]
    for role_row in result.get("required_approvers") or []:
        refs = set(role_row.get("employee_refs") or [])
        if not any(ref in refs and person(directory, ref) and person(directory, ref).get("role") == role_row.get("role") for ref in by_approver):
            return False
    return bool(result.get("required_approvers"))


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def _person_problem(result: dict, approver_ref: object, *, allow_over_limit: bool) -> str | None:
    directory = pinned_sources()["directory"]
    row = person(directory, approver_ref)
    roles = [item.get("role") for item in result.get("required_approvers") or [] if isinstance(item, dict)]
    pence = (result.get("amount") or {}).get("pence")
    if allow_over_limit and result.get("request_type") == "spend":
        problem = approver_problem(row, result.get("requester_ref"), roles, "policy_exception", None)
        if problem == "not_a_required_approver" and row and row.get("role") in roles:
            return None
        return problem
    return approver_problem(row, result.get("requester_ref"), roles, result.get("request_type"), pence)


def _above_clearance(result: dict, approver_ref: object) -> bool:
    row = person(pinned_sources()["directory"], approver_ref)
    marking = (result.get("marking") or {}).get("applied")
    ceiling = row.get("clearance") if isinstance(row, dict) else None
    if marking is None:
        return False
    return above_ceiling(marking, ceiling)


def _bind_problem(result: dict, directory: dict, approval: dict, *, item: str, decision: str | None) -> str | None:
    if not isinstance(result, dict):
        return "not_held"
    if not isinstance(approval, dict):
        return "approval_not_object"
    if approval.get("item") != item:
        return "wrong_item"
    if decision is not None and approval.get("decision") != decision:
        return "wrong_item"
    if directory != pinned_sources()["directory"]:
        return "caller_directory_not_used"
    if approval.get("request_id") != result.get("request_id"):
        return "request_mismatch"
    held = _HELD.get(result.get("request_id"))
    if held is None:
        return "not_held"
    if not isinstance(result.get("content_hash"), str):
        return "content_tampered"
    recomputed = content_hash(result)
    if result.get("content_hash") != recomputed:
        return "content_tampered"
    if recomputed != held["content_hash"] or projection(result) != held["projection"]:
        return "caller_rehash_rejected"
    if approval.get("content_hash") != held["content_hash"]:
        return "content_hash_mismatch"
    return None


def _ceiling(directory: dict, refs: list[str]) -> str | None:
    chosen = None
    for ref in refs:
        row = person(directory, ref)
        clearance = row.get("clearance") if isinstance(row, dict) else None
        if clearance not in RANK:
            return None
        if chosen is None or RANK[clearance] < RANK[chosen]:
            chosen = clearance
    return chosen


def _texts(request: dict) -> list[str]:
    found = []
    for key in ("title", "description", "note"):
        if isinstance(request.get(key), str):
            found.append(request[key])
    evidence = request.get("evidence")
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, dict) and isinstance(item.get("content"), str):
                found.append(item["content"])
    return found


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in list(working):
        if key in PROHIBITED_REQUEST_KEYS:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


def approve_pack(*_args, **_kwargs) -> None:
    raise CoordinatorForbidden("The agent does not approve a pack.")


def reject_pack(*_args, **_kwargs) -> None:
    raise CoordinatorForbidden("The agent does not reject a pack.")


def sign_pack(*_args, **_kwargs) -> None:
    raise CoordinatorForbidden("The agent does not sign a pack.")


def submit_pack(*_args, **_kwargs) -> None:
    raise CoordinatorForbidden("The agent does not submit a pack.")


def send_pack(*_args, **_kwargs) -> None:
    raise CoordinatorForbidden("The agent does not send a pack.")


def pay_pack(*_args, **_kwargs) -> None:
    raise CoordinatorForbidden("The agent does not pay a pack.")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble a synthetic approval pack.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = assemble_pack(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
