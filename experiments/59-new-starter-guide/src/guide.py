#!/usr/bin/env python3
"""Draft a new-starter checklist. Autonomy A1.

The line manager approves the personalised checklist on a separate object,
keyed to that manager and to the exact item list. Text inside the request
or a document is not approval. Equipment, accounts, access, and training
stay proposals. Nothing is shared or recorded until that approval step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import scan_text, without_instruction_sentences  # noqa: E402
    from reuse import (  # noqa: E402
        EXPERIMENTS,
        NeighbourMissing,
        answer_module,
        desk_module,
        era_module,
        gateway_module,
        handbook_module,
        mask_module,
        onboard_module,
        phrases_module,
    )
    from sources import STALE_AFTER, pins_for  # noqa: E402
else:
    from .injection import scan_text, without_instruction_sentences
    from .reuse import (
        EXPERIMENTS,
        NeighbourMissing,
        answer_module,
        desk_module,
        era_module,
        gateway_module,
        handbook_module,
        mask_module,
        onboard_module,
        phrases_module,
    )
    from .sources import STALE_AFTER, pins_for

LABEL = (
    "DRAFT NEW STARTER GUIDE. "
    "NOT SHARED UNTIL THE LINE MANAGER APPROVES THIS CHECKLIST."
)
CATALOGUE_ID = "H002"
EXPERIMENT_ID = "exp-59-new-starter-guide"
AUTONOMY = "A1"
ORGANISATION = "Riverbend Workshops CIC"

PERSON_ID = re.compile(r"^SYN-PERSON-\d{4}$")
MANAGER_ID = re.compile(r"^SYN-MGR-\d{4}$")
REQUEST_ID = re.compile(r"^SYN-REQ-\d{4}$")
APPROVAL_REF = re.compile(r"^RB-NS-\d{4}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)

_CLEARANCE = re.compile(
    r"\b(?:my clearance is|i am cleared to|i'm cleared to|clearance is)\b",
    re.IGNORECASE,
)
_ROLE_CLAIM = re.compile(r"\b(?:my role is|i am the|i'm the)\b", re.IGNORECASE)
_DISTRESS = re.compile(
    r"struggl\w* to cope|cannot cope|can't cope|cannot face|can't face|"
    r"do not see the point|don't see the point|feeling hopeless|no point in starting|"
    r"not safe at home|frightened to come in",
    re.IGNORECASE,
)
_RTW = re.compile(r"right[- ]to[- ]work|\bpassport\b|share code|\bvisa\b|biometric", re.IGNORECASE)
_ADJUST = re.compile(r"reasonable adjustment|\bdisabled\b|\bdisability\b", re.IGNORECASE)
_HEALTH = re.compile(r"health condition|\bmedical\b|sick note|occupational health", re.IGNORECASE)
_PREGNANCY = re.compile(r"pregnan\w*|\bmaternity\b", re.IGNORECASE)
_HARASS = re.compile(r"\bharassment\b|\bbullied\b|\bbullying\b", re.IGNORECASE)
_ORDER = re.compile(r"\border\s+(?P<qty>\d+|many|none|zero)\s+laptops\b", re.IGNORECASE)

_STRIP = frozenset(
    {
        "human_approval",
        "approved",
        "approval",
        "checklist_approved",
        "shared",
        "recorded",
        "provisioned",
        "access_granted",
        "account_created",
        "enrolled",
        "equipment_requested",
        "clearance",
        "self_declared_clearance",
        "role_id",
        "claimed_role",
        "line_manager_id",
        "special_category",
        "health",
        "pregnancy",
        "executed",
        "sent",
    }
)

_CANARIES = (
    "MEDICAL-FILE-CANARY",
    "CANARY-DRAFT-BODY",
    "MIX-CANARY",
    "OLD-LEAVE-CANARY",
)

_CLAIM_PHRASES = ("client entertainment", "fire briefing", "building tour")

# Process-local record of approvals this interpreter actually issued.
# A marker inside a document or a copied JSON object is not in this set.
_ISSUED: set[tuple] = set()

__all__ = [
    "LABEL",
    "CATALOGUE_ID",
    "AUTONOMY",
    "GuideForbidden",
    "draft_guide",
    "approve_checklist",
    "share_checklist",
    "request_equipment",
    "create_account",
    "grant_access",
    "enrol_training",
    "send_externally",
    "write_hr_record",
    "collect_special_category",
]


class GuideForbidden(RuntimeError):
    """The guide has no provision, send, or special-category path."""


def request_equipment(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not request equipment")


def create_account(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not create an account")


def grant_access(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not grant access")


def enrol_training(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not enrol anyone on training")


def send_externally(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not send email or a message")


def write_hr_record(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not write an HR record")


def collect_special_category(*_args, **_kwargs) -> None:
    raise GuideForbidden("the agent does not collect special-category data")


def _flags() -> dict:
    return {
        "shared_with_starter": False,
        "recorded_in_memory": False,
        "external_send": False,
        "provisioned": False,
        "equipment_requested": False,
        "account_created": False,
        "access_granted": False,
        "training_enrolled": False,
        "hr_system_written": False,
        "network_called": False,
        "model_called": False,
        "graph_called": False,
        "special_category_collected": False,
    }


def _parse_day(value: object) -> date | None:
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _strip(node: dict) -> list[str]:
    removed = []
    if not isinstance(node, dict):
        return removed
    for key in list(node):
        if key in _STRIP:
            node.pop(key, None)
            removed.append(key)
    return removed


def _shell(as_of_text: str | None) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "organisation_is_fictional": True,
        "as_of": as_of_text,
        "outcome": "needs_human",
        "human_approval": None,
        "checklist_id": None,
        "item_digest": None,
        "line_manager_id": None,
        "person_id": None,
        "role_id": None,
        "role_title": None,
        "role_source": None,
        "start_date": None,
        "self_declared_role_ignored": False,
        "self_declared_clearance_ignored": False,
        "checklist": [],
        "proposals": [],
        "citations": [],
        "withheld": [],
        "not_selected": [],
        "claims": [],
        "answer": "",
        "question_copied": False,
        "question_covered": False,
        "human_route": {"named": None, "reason": None},
        "routine_processing": False,
        "special_category_collected": False,
        "statutory": [],
        "stale": {"rules_current": False, "opened_on": "2026-11-17", "stale_after": STALE_AFTER.isoformat()},
        "may_be_relied_on": False,
        "prompt_injection": {"detected": False, "followed": False, "signal_count": 0, "signals_copied": False},
        "document_injection": {"detected": False, "followed": False, "document_ids": []},
        "masking": {
            "counts": {
                "phone": 0,
                "email": 0,
                "date_of_birth": 0,
                "postal_address": 0,
                "personal_name": 0,
            },
            "values_stored": False,
            "described_as_anonymised": False,
        },
        "experiment_08": {"called": False, "redacted_text_copied": False, "output_is_anonymised": False, "values_stored": False},
        "experiment_11": {"called": False, "reopened_by_this_starter": False, "compliance_conclusion": None},
        "experiment_15": {"called": False, "categories": [], "phrases_copied": False},
        "experiment_21": {"called": False, "user_text_forwarded": False, "grant_access_called": False, "executed": False},
        "experiment_57": {"called": False, "applied": False, "user_text_forwarded": False},
        "experiment_58": {"called": False, "user_text_forwarded": False, "entitlement_decision": None, "answer_copied": False},
        "unparseable_fields": [],
        "quantity_applied": None,
        "quantity_problem": None,
        "flags": _flags(),
        "legal_advice": False,
        "medical_advice": False,
        "adjustment_decided": None,
        "right_to_work_decided": None,
        "share_receipt": None,
        "stripped_keys": [],
    }


def _digest(items: list[dict]) -> str:
    payload = "|".join(sorted(item["item_id"] for item in items))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _combined(document: dict) -> str:
    parts = []
    cover = document.get("cover_page")
    if isinstance(cover, str):
        parts.append(cover)
    for section in document.get("sections") or []:
        if isinstance(section, dict) and isinstance(section.get("text"), str):
            parts.append(section["text"])
    return "\n".join(parts)


def _labels(handbook, document: dict, text: str) -> dict:
    metadata = document.get("marking") if isinstance(document.get("marking"), str) else ""
    found = handbook.markings_in(metadata, text)
    marking = handbook.higher_marking(found)
    return {
        "marking": marking,
        "labels_seen": found,
        "legal_hold": handbook.legal_hold(document, text),
        "retention_labels": handbook.retention_labels(document, text),
    }


def _quantity(request: dict, question: str) -> tuple[None, str | None] | tuple[int, None]:
    problem = None
    applied: int | None = None
    if "quantity" in request:
        raw = request.get("quantity")
        if isinstance(raw, bool) or not isinstance(raw, int):
            problem = "unparseable_quantity"
        elif raw < 1 or raw > 5:
            problem = "out_of_range_quantity"
        else:
            applied = raw
    match = _ORDER.search(question)
    if match:
        token = match.group("qty")
        if token.isdigit():
            number = int(token)
            if number < 1 or number > 5:
                problem = "out_of_range_quantity"
                applied = None
        else:
            problem = "unparseable_quantity"
            applied = None
    return applied, problem


def _route(question: str, categories: list[str], local_distress: bool) -> tuple[str, str] | None:
    if local_distress or "possible_safeguarding_risk" in categories or "possible_self_harm_risk" in categories:
        return "Named safeguarding route", "distress"
    if _HARASS.search(question):
        return "HR route", "harassment"
    if _PREGNANCY.search(question):
        return "HR route", "pregnancy"
    if _HEALTH.search(question):
        return "HR occupational-health route", "health"
    if _ADJUST.search(question):
        return "HR reasonable-adjustments route", "reasonable_adjustment"
    if "possible_financial_hardship" in categories:
        return "HR route", "vulnerability"
    if _RTW.search(question):
        return "HR right-to-work route", "right_to_work"
    return None


def _topics(question: str, items: list[dict], reason: str | None) -> set[str]:
    topics = set()
    ids = {item["item_id"] for item in items}
    if "ITEM-STATEMENT" in ids or re.search(r"written statement|particulars", question, re.I):
        topics.add("statement")
    if "ITEM-PRIVACY" in ids or re.search(r"privacy|notice", question, re.I):
        topics.add("privacy")
    if "ITEM-RTW" in ids or reason == "right_to_work":
        topics.add("right_to_work")
    if reason in {"reasonable_adjustment", "health", "pregnancy"}:
        topics.add("adjustment")
    return topics


def _mask(question: str) -> tuple[dict, dict]:
    extra = {
        "counts": {"phone": 0, "email": 0, "date_of_birth": 0, "postal_address": 0, "personal_name": 0},
        "values_stored": False,
        "described_as_anonymised": False,
    }
    gateway = {"called": False, "redacted_text_copied": False, "output_is_anonymised": False, "values_stored": False}
    try:
        extra = mask_module().mask_counts(question)
        extra["described_as_anonymised"] = False
        extra["values_stored"] = False
    except NeighbourMissing:
        extra["reason"] = "neighbour_missing"
    try:
        proposal = gateway_module().propose(
            question,
            caller="exp-59-new-starter-guide",
            reversible=False,
        )
        findings = proposal.get("audit_log", {}).get("findings") or []
        gateway = {
            "called": True,
            "finding_count": len(findings),
            "entity_types": sorted({row.get("entity_type") for row in findings if row.get("entity_type")}),
            "redacted_text_copied": False,
            "output_is_anonymised": False,
            "values_stored": False,
        }
    except NeighbourMissing:
        gateway["reason"] = "neighbour_missing"
    return extra, gateway


def _phrases(question: str) -> dict:
    try:
        found = phrases_module().find_phrases(question)
    except NeighbourMissing:
        return {"called": False, "categories": [], "phrases_copied": False, "reason": "neighbour_missing"}
    categories = sorted({row["category"] for row in found if isinstance(row, dict) and row.get("category")})
    return {"called": True, "categories": categories, "phrases_copied": False}


def _era() -> dict:
    try:
        era = era_module()
    except NeighbourMissing:
        return {
            "called": False,
            "reopened_by_this_starter": False,
            "compliance_conclusion": None,
            "reason": "neighbour_missing",
        }
    return {
        "called": True,
        "reopened_by_this_starter": False,
        "last_verified_in_experiment_11": era.LAST_VERIFIED,
        "all_reasonable_steps_in_force": era.ALL_REASONABLE_STEPS_IN_FORCE.isoformat(),
        "third_party_harassment_in_force": era.THIRD_PARTY_IN_FORCE.isoformat(),
        "compliance_conclusion": None,
        "applied_to_this_starter": False,
        "note": "Experiment 11 dates were not re-opened on 17 November 2026.",
    }


def _desk(as_of: str) -> dict:
    try:
        desk = desk_module()
    except NeighbourMissing:
        return {
            "called": False,
            "user_text_forwarded": False,
            "grant_access_called": False,
            "executed": False,
            "reason": "neighbour_missing",
        }
    ticket = {
        "synthetic": True,
        "ticket_id": "SYN-5901",
        "channel": "email",
        "summary": "What are the service desk hours?",
        "requester": {"staff_id": "SYN-STAFF-591", "signed_in": False},
        "subject_account": {"staff_id": "SYN-STAFF-591"},
    }
    try:
        draft = desk.triage(ticket, as_of)
    except Exception as exc:  # noqa: BLE001 — a neighbour import must not abort the draft
        return {
            "called": False,
            "user_text_forwarded": False,
            "grant_access_called": False,
            "executed": False,
            "reason": type(exc).__name__,
        }
    article = draft.get("article") if isinstance(draft.get("article"), dict) else {}
    return {
        "called": True,
        "user_text_forwarded": False,
        "fixed_question": "service desk hours",
        "outcome": draft.get("outcome"),
        "article_id": article.get("id"),
        "executed": draft.get("executed") is True,
        "human_approval": draft.get("human_approval"),
        "grant_access_called": False,
        "answer_copied": False,
    }


def _handbook(as_of: str) -> dict:
    try:
        answer = answer_module()
    except NeighbourMissing:
        return {
            "called": False,
            "user_text_forwarded": False,
            "entitlement_decision": None,
            "answer_copied": False,
            "reason": "neighbour_missing",
        }
    folder = EXPERIMENTS / "58-employee-handbook"
    handbook = json.loads((folder / "fixtures" / "handbook.json").read_text(encoding="utf-8"))
    scope = json.loads((folder / "examples" / "sample_scope.json").read_text(encoding="utf-8"))
    question = {
        "synthetic": True,
        "question": "What does the leave policy state for a worker on a five-day week?",
    }
    try:
        result = answer.answer_handbook(question, handbook, scope, as_of)
    except NeighbourMissing:
        return {
            "called": False,
            "user_text_forwarded": False,
            "entitlement_decision": None,
            "answer_copied": False,
            "reason": "neighbour_missing",
        }
    except Exception as exc:  # noqa: BLE001 — a neighbour import must not abort the draft
        return {
            "called": False,
            "user_text_forwarded": False,
            "entitlement_decision": None,
            "answer_copied": False,
            "reason": type(exc).__name__,
        }
    sections = [
        row.get("section_id")
        for row in result.get("citations") or []
        if isinstance(row, dict)
    ]
    return {
        "called": True,
        "user_text_forwarded": False,
        "fixed_question": "leave policy for a five-day week",
        "outcome": result.get("outcome"),
        "section_ids": sections,
        "entitlement_decision": result.get("entitlement_decision"),
        "human_approval": result.get("human_approval"),
        "answer_copied": False,
    }


def _space(as_of: str, person_id: str) -> dict:
    try:
        onboard = onboard_module()
    except NeighbourMissing:
        return {"called": False, "applied": False, "user_text_forwarded": False, "reason": "neighbour_missing"}
    folder = EXPERIMENTS / "57-collaboration-space-onboarding"
    space = json.loads((folder / "examples" / "sample_space.json").read_text(encoding="utf-8"))
    request = {
        "request_id": "SYN-REQ-5957",
        "person_ref": person_id if PERSON_ID.fullmatch(person_id or "") else "SYN-PERSON-5902",
        "account_type": "internal",
        "requested_role": "member",
        "requested_channels": ["SYN-CH-GENERAL"],
        "justification": "I need the programme board pack for the repairs review.",
    }
    try:
        draft = onboard.prepare_onboarding(space, request, as_of)
    except NeighbourMissing:
        return {"called": False, "applied": False, "user_text_forwarded": False, "reason": "neighbour_missing"}
    except Exception as exc:  # noqa: BLE001 — a neighbour import must not abort the draft
        return {
            "called": False,
            "applied": False,
            "user_text_forwarded": False,
            "reason": type(exc).__name__,
            "explanation_copied": False,
        }
    return {
        "called": True,
        "applied": draft.get("applied") is True,
        "outcome": draft.get("outcome"),
        "human_approval": draft.get("human_approval"),
        "user_text_forwarded": False,
        "live_graph_called": False,
        "explanation_copied": False,
    }


def _guard(result: dict, question: str) -> dict:
    blob = json.dumps(result)
    for canary in _CANARIES:
        if canary in blob:
            raise GuideForbidden("withheld or superseded text was copied")
    if isinstance(question, str) and len(question) >= 20 and question in blob:
        raise GuideForbidden("the question was copied into the result")
    for email in EMAIL.findall(question or ""):
        if email in blob:
            raise GuideForbidden("an email address was copied into the result")
    if result["human_approval"] is not None:
        raise GuideForbidden("draft_guide must not approve")
    flags = result["flags"]
    for key in (
        "shared_with_starter",
        "recorded_in_memory",
        "external_send",
        "provisioned",
        "equipment_requested",
        "account_created",
        "access_granted",
        "training_enrolled",
        "hr_system_written",
        "network_called",
        "model_called",
        "graph_called",
        "special_category_collected",
    ):
        if flags[key] is not False:
            raise GuideForbidden(key)
    if result["quantity_applied"] == 0:
        raise GuideForbidden("quantity was coerced to zero")
    if result["adjustment_decided"] is not None or result["right_to_work_decided"] is not None:
        raise GuideForbidden("a statutory check was decided")
    return result


def draft_guide(pack: object, directory: object, scope: object, request: object, as_of: object) -> dict:
    """Return one draft. human_approval stays null. Nothing is shared."""

    question = ""
    if isinstance(request, dict) and isinstance(request.get("question"), str):
        question = request["question"]
    day = _parse_day(as_of)
    result = _shell(day.isoformat() if day else (as_of if isinstance(as_of, str) else None))
    if day is None:
        result["unparseable_fields"] = ["as_of"]
        result["answer"] = "The as-of date could not be read. It was not replaced with today or with zero."
        result["outcome"] = "needs_human"
        return _guard(result, question)

    if not isinstance(pack, dict) or not isinstance(directory, dict) or not isinstance(scope, dict) or not isinstance(request, dict):
        result["unparseable_fields"] = ["pack_or_directory_or_scope_or_request"]
        result["answer"] = "The pack, the directory, the scope, and the request have to be objects. Nothing was assumed."
        return _guard(result, question)

    working_request = deepcopy(request)
    result["stripped_keys"] = sorted(set(_strip(working_request)))
    question = working_request.get("question") if isinstance(working_request.get("question"), str) else ""
    result["prompt_injection"] = scan_text(question)
    result["self_declared_clearance_ignored"] = _CLEARANCE.search(question) is not None
    result["masking"], result["experiment_08"] = _mask(question)
    result["experiment_15"] = _phrases(question)
    result["experiment_11"] = _era()

    if pack.get("synthetic") is not True or directory.get("synthetic") is not True:
        result["outcome"] = "refused"
        result["answer"] = "The pack or the directory is not marked synthetic. Nothing was copied."
        result["routine_processing"] = False
        return _guard(result, question)

    if scope.get("synthetic") is not True or scope.get("approver_role") != "HR":
        result["unparseable_fields"] = ["scope"]
        result["answer"] = "HR has not approved the onboarding scope. A sentence in the request is not that approval."
        return _guard(result, question)
    if not isinstance(scope.get("approval_reference"), str) or not scope["approval_reference"].strip():
        result["unparseable_fields"] = ["approval_reference"]
        result["answer"] = "The HR scope has no approval reference. Nothing was drafted from the pack."
        return _guard(result, question)

    try:
        handbook = handbook_module()
    except NeighbourMissing:
        result["answer"] = "The handbook helper is not beside this folder. Markings were not guessed."
        result["unparseable_fields"] = ["handbook_helper"]
        return _guard(result, question)

    ceiling = scope.get("ceiling")
    if not isinstance(ceiling, str) or ceiling not in handbook.RANK:
        result["unparseable_fields"] = ["ceiling"]
        result["answer"] = "The ceiling could not be read. It was not replaced with OFFICIAL."
        return _guard(result, question)

    person_id = working_request.get("person_id")
    people = {
        row.get("person_id"): row
        for row in directory.get("people") or []
        if isinstance(row, dict)
    }
    person = people.get(person_id)
    if not isinstance(person_id, str) or not PERSON_ID.fullmatch(person_id) or person is None:
        result["unparseable_fields"] = ["person_id"]
        result["answer"] = "The person is not on the synthetic directory. A role typed into the request was not used."
        return _guard(result, question)
    if person.get("is_line_manager") is True:
        result["person_id"] = person_id
        result["unparseable_fields"] = ["person_id"]
        result["answer"] = "That directory row is a line manager, not a new starter. No checklist was drafted."
        return _guard(result, question)

    start = handbook.parse_day(person.get("start_date"))
    if start is None:
        result["person_id"] = person_id
        result["unparseable_fields"] = ["start_date"]
        result["answer"] = "The start date on the directory could not be read. It was not replaced with the as-of date."
        return _guard(result, question)

    claimed = working_request.get("claimed_role")
    role_claim = _ROLE_CLAIM.search(question) is not None or isinstance(claimed, str)
    directory_role = person.get("role_id")
    if role_claim and claimed != person.get("role_title") and claimed != directory_role:
        result["self_declared_role_ignored"] = True
    elif role_claim:
        result["self_declared_role_ignored"] = True

    result["person_id"] = person_id
    result["role_id"] = directory_role
    result["role_title"] = person.get("role_title")
    result["role_source"] = "directory"
    result["line_manager_id"] = person.get("line_manager_id")
    result["start_date"] = start.isoformat()
    result["experiment_21"] = _desk(day.isoformat())

    approved_ids = set(scope.get("approved_document_ids") or [])
    quantity, quantity_problem = _quantity(working_request, question)
    result["quantity_applied"] = quantity
    result["quantity_problem"] = quantity_problem

    admitted = []
    injected_docs = []
    documents = [row for row in pack.get("documents") or [] if isinstance(row, dict)]
    in_force_ids = {}
    prepared = []
    for document in documents:
        text = _combined(document)
        labels = _labels(handbook, document, text)
        document_id = document.get("document_id")
        prepared.append((document, text, labels, document_id))
        if document.get("status") == "in_force" and handbook.in_force_on(document, day) is True:
            family = document.get("family")
            if isinstance(family, str):
                in_force_ids[family] = document_id

    for document, text, labels, document_id in prepared:
        row = {
            "document_id": document_id,
            "marking": labels["marking"],
            "legal_hold": labels["legal_hold"],
            "retention_labels": labels["retention_labels"],
            "body_copied": False,
        }
        if document_id not in approved_ids:
            row["reason"] = "not_in_scope"
            result["not_selected"].append(row)
            continue
        if labels["marking"] is None or handbook.above_ceiling(labels["marking"], ceiling):
            row["reason"] = "above_ceiling" if labels["marking"] else "unparseable_marking"
            result["withheld"].append(row)
            continue
        in_force = handbook.in_force_on(document, day)
        if in_force is None:
            row["reason"] = "unparseable_date"
            result["withheld"].append(row)
            continue
        if document.get("status") != "in_force" or in_force is not True:
            row["reason"] = "not_in_force"
            family = document.get("family")
            if isinstance(family, str) and in_force_ids.get(family) not in (None, document_id):
                row["later_document_id"] = in_force_ids[family]
            result["not_selected"].append(row)
            continue
        roles = document.get("role_ids") if isinstance(document.get("role_ids"), list) else []
        if "all" not in roles and directory_role not in roles:
            row["reason"] = "role_mismatch"
            result["not_selected"].append(row)
            continue
        scan = scan_text(text)
        if scan["detected"]:
            injected_docs.append(document_id)
        admitted.append((document, labels))

    result["document_injection"] = {
        "detected": bool(injected_docs) or result["prompt_injection"]["detected"],
        "followed": False,
        "document_ids": injected_docs,
    }

    items = []
    quotations = []
    for document, labels in admitted:
        for section in document.get("sections") or []:
            if not isinstance(section, dict):
                continue
            raw = section.get("text") if isinstance(section.get("text"), str) else ""
            cleaned = without_instruction_sentences(raw)
            if cleaned:
                quotations.append(cleaned)
                result["citations"].append(
                    {
                        "document_id": document.get("document_id"),
                        "section_id": section.get("section_id"),
                        "effective_from": document.get("effective_from"),
                        "quotation": cleaned,
                        "marking": labels["marking"],
                        "legal_hold": labels["legal_hold"],
                        "retention_labels": list(labels["retention_labels"]),
                        "body_copied": True,
                    }
                )
            step = section.get("step")
            if not isinstance(step, dict):
                continue
            step_text = without_instruction_sentences(step.get("text") if isinstance(step.get("text"), str) else "")
            if not step_text or not isinstance(step.get("item_id"), str):
                continue
            items.append(
                {
                    "item_id": step["item_id"],
                    "document_id": document.get("document_id"),
                    "section_id": section.get("section_id"),
                    "text": step_text,
                    "effective_from": document.get("effective_from"),
                    "proposal_type": step.get("proposal_type") if isinstance(step.get("proposal_type"), str) else "none",
                    "owner": step.get("owner") if isinstance(step.get("owner"), str) else "Line manager",
                    "status": "proposal" if step.get("proposal_type") not in (None, "none") else "read",
                    "executed": False,
                    "quantity_applied": None,
                    "marking": labels["marking"],
                    "legal_hold": labels["legal_hold"],
                    "retention_labels": list(labels["retention_labels"]),
                }
            )

    items.sort(key=lambda item: item["item_id"])
    result["checklist"] = items
    result["checklist_id"] = f"SYN-CHK-{person_id[-4:]}-{day.isoformat()}"
    result["item_digest"] = _digest(items) if items else None
    result["proposals"] = [
        {
            "item_id": item["item_id"],
            "proposal_type": item["proposal_type"],
            "owner": item["owner"],
            "executed": False,
        }
        for item in items
        if item["proposal_type"] != "none"
    ]

    quoted = "\n".join(quotations)
    result["claims"] = [
        {
            "phrase": phrase,
            "included": handbook.source_includes(quoted, phrase),
            "denied": handbook.source_denies(quoted, phrase),
        }
        for phrase in _CLAIM_PHRASES
        if phrase.casefold() in quoted.casefold()
    ]

    categories = result["experiment_15"]["categories"]
    local_distress = _DISTRESS.search(question) is not None
    routed = _route(question, categories, local_distress)
    reason = routed[1] if routed else None
    result["statutory"] = pins_for(_topics(question, items, reason), day)
    stale = day > STALE_AFTER
    result["stale"] = {
        "rules_current": not stale,
        "opened_on": "2026-11-17",
        "stale_after": STALE_AFTER.isoformat(),
    }
    if re.search(r"\bleave\b|\bholiday\b", question, re.I) and routed is None:
        result["experiment_58"] = _handbook(day.isoformat())
    if any(item["item_id"] == "ITEM-SPACE" for item in items):
        result["experiment_57"] = _space(day.isoformat(), person_id)

    if routed:
        named, why = routed
        result["outcome"] = "routed_to_human"
        result["routine_processing"] = False
        result["human_route"] = {"named": named, "reason": why}
        result["answer"] = (
            f"This is not handled as a routine onboarding question. The route is {named}. "
            "The question has not been copied. Nothing has been requested, created, granted, "
            "enrolled, sent, or recorded."
        )
    elif quantity_problem:
        result["outcome"] = "needs_human"
        result["routine_processing"] = False
        result["answer"] = (
            "A quantity could not be read, or it is outside 1 to 5. "
            "It was not replaced with zero. The template still proposes one standard item and does not order it."
        )
    else:
        result["outcome"] = "draft"
        result["routine_processing"] = True
        result["question_covered"] = True
        result["answer"] = (
            f"Draft checklist for the {person.get('role_title')} role recorded on the directory. "
            "It is not shared until the line manager approves this checklist. "
            "Nothing has been requested, created, granted, enrolled, sent, or recorded."
        )
        included = {row["phrase"]: row["included"] for row in result["claims"]}
        if included.get("fire briefing") is True and included.get("client entertainment") is False:
            result["answer"] += " The induction text includes a fire briefing. A denial of client entertainment is not an inclusion."
        if re.search(r"written statement|particulars", question, re.I):
            result["answer"] += " The employer gives the written statement. This agent does not produce it and does not decide that section 1 was met."

    incomplete = any(row.get("may_be_relied_on") is not True for row in result["statutory"])
    result["may_be_relied_on"] = (
        result["outcome"] == "draft" and not stale and not incomplete and bool(items)
    )
    return _guard(result, question)


def _approval_key(approval: dict) -> tuple:
    return (
        approval.get("checklist_id"),
        approval.get("item_digest"),
        approval.get("actor_id"),
        approval.get("approval_reference"),
    )


def approve_checklist(result: dict, approval: object) -> dict:
    """Record the line manager's approval of this exact checklist.

    The approval argument is the only input that can count. Markers inside
    the draft, the question, or a document are ignored because they are not
    this argument and they are not added to the issued set.
    """

    updated = deepcopy(result)
    updated["human_approval"] = None
    updated["share_receipt"] = None
    updated["flags"]["shared_with_starter"] = False
    updated["flags"]["recorded_in_memory"] = False
    if not isinstance(approval, dict):
        updated["approval_rejection"] = "approval_not_an_object"
        return updated
    if updated.get("catalogue_id") != CATALOGUE_ID or not updated.get("checklist_id") or not updated.get("item_digest"):
        updated["approval_rejection"] = "nothing_to_approve"
        return updated
    actor = approval.get("actor_id")
    reference = approval.get("approval_reference")
    checks = [
        approval.get("decision") == "approve",
        approval.get("actor_role") == "Line manager",
        isinstance(actor, str) and MANAGER_ID.fullmatch(actor) is not None,
        actor == updated.get("line_manager_id"),
        approval.get("checklist_id") == updated.get("checklist_id"),
        approval.get("item_digest") == updated.get("item_digest"),
        isinstance(reference, str) and APPROVAL_REF.fullmatch(reference) is not None,
    ]
    if not all(checks):
        updated["approval_rejection"] = "not_the_line_manager_for_this_checklist"
        return updated
    issued = {
        "source": "deterministic_approval_step",
        "actor_id": actor,
        "actor_role": "Line manager",
        "checklist_id": updated["checklist_id"],
        "item_digest": updated["item_digest"],
        "approval_reference": reference,
        "decision": "approve",
    }
    _ISSUED.add(_approval_key(issued))
    updated["human_approval"] = issued
    updated.pop("approval_rejection", None)
    return updated


def share_checklist(result: dict) -> dict:
    """Share only an approval this process issued for this exact item list."""

    updated = deepcopy(result)
    approval = updated.get("human_approval")
    flags = updated["flags"]
    flags["shared_with_starter"] = False
    flags["recorded_in_memory"] = False
    flags["external_send"] = False
    flags["provisioned"] = False
    updated["share_receipt"] = None
    if not isinstance(approval, dict) or approval.get("source") != "deterministic_approval_step":
        updated["share_rejection"] = "no_deterministic_approval"
        return updated
    if _approval_key(approval) not in _ISSUED:
        updated["share_rejection"] = "approval_was_not_issued_by_the_approval_step"
        updated["human_approval"] = None
        return updated
    if approval.get("checklist_id") != updated.get("checklist_id") or approval.get("item_digest") != updated.get("item_digest"):
        updated["share_rejection"] = "approval_does_not_match_this_checklist"
        return updated
    if approval.get("actor_id") != updated.get("line_manager_id"):
        updated["share_rejection"] = "approver_is_not_the_line_manager"
        return updated
    flags["shared_with_starter"] = True
    flags["recorded_in_memory"] = True
    updated["share_receipt"] = {
        "checklist_id": updated["checklist_id"],
        "item_digest": updated["item_digest"],
        "approval_reference": approval.get("approval_reference"),
        "channel": "in_memory",
        "email_sent": False,
        "hr_system_written": False,
        "provisioned": False,
    }
    updated.pop("share_rejection", None)
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a new-starter checklist.")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--approval")
    parser.add_argument("--share", action="store_true")
    args = parser.parse_args(argv)
    pack = json.loads(Path(args.pack).read_text(encoding="utf-8"))
    directory = json.loads(Path(args.directory).read_text(encoding="utf-8"))
    scope = json.loads(Path(args.scope).read_text(encoding="utf-8"))
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    result = draft_guide(pack, directory, scope, request, args.as_of)
    if args.approval:
        approval = json.loads(Path(args.approval).read_text(encoding="utf-8"))
        approval["checklist_id"] = result.get("checklist_id")
        approval["item_digest"] = result.get("item_digest")
        result = approve_checklist(result, approval)
        if args.share:
            result = share_checklist(result)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
