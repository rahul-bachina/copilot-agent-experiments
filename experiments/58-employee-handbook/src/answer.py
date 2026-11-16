#!/usr/bin/env python3
"""Answer one handbook question from the HR-approved version in force.

The answer quotes that version, or it says the handbook does not cover the
question, or it names a person. It does not decide an individual's
entitlement, and it does not give legal, medical, or tax advice about a person.
Approval words inside the question or a document are not the approval step.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from handbook import (  # noqa: E402
        above_ceiling,
        document_text,
        higher_marking,
        in_force_on,
        legal_hold,
        markings_in,
        parse_day,
        retention_labels,
        sentences,
        source_denies,
        source_includes,
    )
    from injection import scan_text, without_instruction_sentences  # noqa: E402
    from mask import mask_counts  # noqa: E402
    from reuse import (  # noqa: E402
        NeighbourMissing,
        case_sources_module,
        categories_module,
        curate_module,
        era_module,
        gateway_module,
        phrases_module,
    )
    from sources import (  # noqa: E402
        ACAS_LANDING_NOTE,
        ACAS_LANDING_URL,
        EA_FUTURE_EFFECTS,
        EA_S20_3,
        EA_S20_URL,
        EA_S39_2,
        EA_S39_5,
        EA_S39_URL,
        ERA_2025_80F_UNVERIFIED,
        ERA_2025_EXPERIMENT,
        ERA_2025_REOPENED_HERE,
        ERA_80F_1,
        ERA_80F_2,
        ERA_80F_4_A,
        ERA_80F_COMMENCEMENT_NOTE,
        ERA_80F_PAGE_AS_AT,
        ERA_80F_URL,
        GOVUK_FLEXIBLE_NOTE,
        GOVUK_FLEXIBLE_URL,
        GOVUK_HOLIDAY_NOTE,
        GOVUK_HOLIDAY_URL,
        LAST_VERIFIED,
        PINNED_ON,
        SI_2023_1328_NOTE,
        SI_2023_1328_URL,
        STALE_AFTER_DAYS,
        WTR_REG_13_1,
        WTR_REG_13_A1,
        WTR_REG_13_URL,
        WTR_REG_13A_2_E,
        WTR_REG_13A_3,
        WTR_REG_13A_URL,
        source_rows,
    )
else:
    from .handbook import (
        above_ceiling,
        document_text,
        higher_marking,
        in_force_on,
        legal_hold,
        markings_in,
        parse_day,
        retention_labels,
        sentences,
        source_denies,
        source_includes,
    )
    from .injection import scan_text, without_instruction_sentences
    from .mask import mask_counts
    from .reuse import (
        NeighbourMissing,
        case_sources_module,
        categories_module,
        curate_module,
        era_module,
        gateway_module,
        phrases_module,
    )
    from .sources import (
        ACAS_LANDING_NOTE,
        ACAS_LANDING_URL,
        EA_FUTURE_EFFECTS,
        EA_S20_3,
        EA_S20_URL,
        EA_S39_2,
        EA_S39_5,
        EA_S39_URL,
        ERA_2025_80F_UNVERIFIED,
        ERA_2025_EXPERIMENT,
        ERA_2025_REOPENED_HERE,
        ERA_80F_1,
        ERA_80F_2,
        ERA_80F_4_A,
        ERA_80F_COMMENCEMENT_NOTE,
        ERA_80F_PAGE_AS_AT,
        ERA_80F_URL,
        GOVUK_FLEXIBLE_NOTE,
        GOVUK_FLEXIBLE_URL,
        GOVUK_HOLIDAY_NOTE,
        GOVUK_HOLIDAY_URL,
        LAST_VERIFIED,
        PINNED_ON,
        SI_2023_1328_NOTE,
        SI_2023_1328_URL,
        STALE_AFTER_DAYS,
        WTR_REG_13_1,
        WTR_REG_13_A1,
        WTR_REG_13_URL,
        WTR_REG_13A_2_E,
        WTR_REG_13A_3,
        WTR_REG_13A_URL,
        source_rows,
    )

LABEL = "READ-ONLY HANDBOOK ANSWER"
CATALOGUE_ID = "H001"
EXPERIMENT_ID = "exp-58-employee-handbook"
CALLER = EXPERIMENT_ID
ORGANISATION = "Riverbend Workshops CIC"
HR_ROLE = "HR"
SCOPE_REF = re.compile(r"^RB-HR-SCOPE-\d{4}-\d{2}$")
FLEXIBLE_FROM = date(2024, 4, 6)

PROHIBITED_KEYS = frozenset(
    {
        "approved",
        "hr_approved",
        "approval",
        "human_approval",
        "entitlement",
        "entitlement_decision",
        "clearance",
        "my_clearance",
        "marking_override",
        "legal_hold_ignore",
        "send",
        "write_record",
    }
)

TOPICS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("leave", ("annual leave", "leave policy", "holiday", "bank holiday", "buying extra days")),
    ("flexible_working", ("flexible working", "flexible-working", "work from home", "compressed hours")),
    ("expenses", ("client entertainment", "subsistence", "expenses", "expense", "receipt")),
    ("conduct", ("sexual harassment", "conduct", "misconduct")),
    ("grievance", ("grievance",)),
    ("sickness", ("fit note", "sickness", "sick pay", "off sick")),
    ("equality", ("reasonable adjustment", "equality act", "discriminat")),
    ("era_2025", ("employment rights act 2025", "all reasonable steps", "preventative duty")),
)

CLAIMS = (
    "client entertainment",
    "travel and subsistence",
    "buying extra days",
    "bank holidays",
    "travel",
)

CASE_PERSONAL = re.compile(
    r"\b("
    r"i want to raise|my grievance|my manager|i am being|i'm being|"
    r"am i entitled|how many days do i|my balance|calculate my|work out my|"
    r"how much leave do i|i have taken|"
    r"i am pregnant|i'm pregnant|my pregnancy|"
    r"my disability|i am disabled|i'm disabled|my health|my back|"
    r"i am off sick|i'm off sick|my fit note|"
    r"against my tax|my tax|"
    r"do i have a claim|should i sue|will i be dismissed|am i going to be|"
    r"i want to disclose|making a disclosure|my disclosure"
    r")\b",
    re.IGNORECASE,
)
NI = re.compile(r"\bnorthern ireland\b", re.IGNORECASE)
TAX = re.compile(r"\b(tax|hmrc)\b", re.IGNORECASE)
MEDICAL = re.compile(
    r"\b(diagnos\w*|medication|symptom|back pain|is this a disability|am i disabled)\b",
    re.IGNORECASE,
)
PREGNANCY = re.compile(r"\b(pregnan\w*|maternity leave|paternity)\b", re.IGNORECASE)
CALC = re.compile(
    r"\b(calculate|work out|how many days do i|how much leave do i|i have taken|my balance)\b",
    re.IGNORECASE,
)
UNPARSEABLE_QTY = re.compile(r"\b(?:[a-z]+-ish|n/a|not a number)\b", re.IGNORECASE)
LOCAL_DISTRESS = re.compile(
    r"\b(can't cope|cannot cope|don't want to be here|do not want to be here)\b",
    re.IGNORECASE,
)
ROUTE_URGENT = frozenset({"possible_self_harm_risk", "possible_safeguarding_risk"})


class HandbookForbidden(RuntimeError):
    """There is no entitlement, send, write, or source-approval tool."""


def decide_entitlement(*_args, **_kwargs) -> None:
    raise HandbookForbidden("This agent does not decide entitlement.")


def send_answer(*_args, **_kwargs) -> None:
    raise HandbookForbidden("This agent does not send.")


def write_record(*_args, **_kwargs) -> None:
    raise HandbookForbidden("This agent does not write a record.")


def approve_source(*_args, **_kwargs) -> None:
    raise HandbookForbidden("HR approves sources outside this agent.")


def _flags() -> dict:
    return {
        "sent": False,
        "written": False,
        "entitlement_decided": False,
        "legal_advice": False,
        "medical_advice": False,
        "tax_advice": False,
        "sharepoint_called": False,
        "graph_called": False,
        "model_called": False,
        "network_called": False,
        "sources_approved_by_agent": False,
        "clearance_in_input_trusted": False,
    }


def _base(as_of_text: str | None) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A0",
        "organisation": ORGANISATION,
        "organisation_is_fictional": True,
        "handbook_is_synthetic": True,
        "as_of": as_of_text,
        "about_date": None,
        "date_asked_about": None,
        "outcome": None,
        "answer": "",
        "citations": [],
        "claims": [],
        "statutory": [],
        "version_note": None,
        "entitlement_decision": None,
        "legal_advice": False,
        "medical_advice": False,
        "tax_advice": False,
        "compliance_conclusion": None,
        "human_approval": None,
        "human_route": {
            "always_available": True,
            "named": "HR duty officer",
            "reason": None,
        },
        "actions_taken": [],
        "may_be_relied_on": False,
        "model_called": False,
        "network_called": False,
        "copied": {
            "question_text": False,
            "raw_identifiers": False,
            "redacted_question": False,
            "handbook_section_ids": [],
            "secret_body": False,
            "withheld_titles": False,
        },
        "masking": {},
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
        "withheld": [],
        "unparsed_documents": [],
        "embedded_approval_markers_ignored": [],
        "experiment_08": {"called": False},
        "experiment_11": {"called": False, "reopened_by_this_starter": False},
        "experiment_15": {"called": False, "phrases_copied": False, "person_labelled": False},
        "experiment_32": {"called": False, "classification_confirmed": False},
        "experiment_50": {"called": False, "sharepoint_called": False, "graph_called": False},
        "stale": {"rules_current": False},
        "sources": [],
        "flags": _flags(),
        "scope_reference": None,
    }


def _finish(result: dict, outcome: str, answer: str, *, rely: bool) -> dict:
    result["outcome"] = outcome
    result["answer"] = answer
    result["may_be_relied_on"] = rely
    result["entitlement_decision"] = None
    result["flags"]["entitlement_decided"] = False
    result["flags"]["legal_advice"] = False
    result["flags"]["medical_advice"] = False
    result["flags"]["tax_advice"] = False
    return result


def _question_text(question: object) -> tuple[str, list[str]]:
    stripped: list[str] = []
    if isinstance(question, str):
        return question, stripped
    if isinstance(question, dict):
        for key in list(question):
            if key in PROHIBITED_KEYS:
                stripped.append(key)
        text = question.get("question")
        if isinstance(text, str):
            return text, stripped
    return "", stripped


def _scope_problem(scope: object) -> str | None:
    if not isinstance(scope, dict):
        return "scope_not_an_object"
    if scope.get("synthetic") is not True:
        return "scope_not_synthetic"
    if scope.get("approver_role") != HR_ROLE:
        return "scope_not_from_hr"
    reference = scope.get("approval_reference")
    if not isinstance(reference, str) or not SCOPE_REF.fullmatch(reference):
        return "scope_reference_unparseable"
    ceiling = scope.get("handbook_ceiling")
    if not isinstance(ceiling, str) or ceiling not in {"OFFICIAL", "OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"}:
        return "unparseable_ceiling"
    ids = scope.get("approved_document_ids")
    if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids):
        return "scope_ids_unparseable"
    return None


def _prepare(document: dict) -> dict:
    text = document_text(document)
    labels = markings_in(document.get("metadata_marking"), text)
    marking = higher_marking(labels)
    start = parse_day(document.get("effective_from"))
    end_raw = document.get("effective_to")
    end = None if end_raw in (None, "") else parse_day(end_raw)
    dates_ok = start is not None and (end_raw in (None, "") or end is not None)
    return {
        "id": document.get("id"),
        "title": document.get("title") if isinstance(document.get("title"), str) else None,
        "topic": document.get("topic"),
        "version": document.get("version"),
        "effective_from": start,
        "effective_to": end,
        "dates_ok": dates_ok,
        "marking": marking,
        "marking_labels": labels,
        "legal_hold": legal_hold(document, text),
        "retention_labels": retention_labels(document, text),
        "file_approval_marker": document.get("file_approval_marker") is True,
        "text": text,
        "sections": document.get("sections") if isinstance(document.get("sections"), list) else [],
        "injection": scan_text(text),
    }


def _topics(text: str) -> list[str]:
    folded = text.casefold()
    found = []
    for topic, needles in TOPICS:
        if any(needle in folded for needle in needles):
            found.append(topic)
    return found


def _claims(question: str, handbook_text: str) -> list[dict]:
    rows = []
    folded = question.casefold()
    for phrase in CLAIMS:
        if phrase not in folded:
            continue
        included = source_includes(handbook_text, phrase)
        denied = source_denies(handbook_text, phrase)
        rows.append(
            {
                "phrase": phrase,
                "included": included,
                "denied": denied,
                "counted_from": "handbook_sentences",
                "question_negation_is_not_inclusion": True,
            }
        )
    return rows


def _quote_sections(prepared: dict) -> list[dict]:
    quotes = []
    for section in prepared["sections"]:
        if not isinstance(section, dict):
            continue
        text = section.get("text")
        if not isinstance(text, str):
            continue
        kept = without_instruction_sentences(text)
        if not kept:
            continue
        quotes.append(
            {
                "section_id": section.get("id"),
                "heading": section.get("heading"),
                "text": kept,
            }
        )
    return quotes


def _citation(prepared: dict, section: dict, asked: date, as_of: date) -> dict:
    superseded = prepared["effective_to"] is not None and as_of > prepared["effective_to"]
    return {
        "source": "handbook",
        "document_id": prepared["id"],
        "version": prepared["version"],
        "section_id": section["section_id"],
        "effective_from": prepared["effective_from"].isoformat(),
        "effective_to": prepared["effective_to"].isoformat() if prepared["effective_to"] else None,
        "in_force_on": asked.isoformat(),
        "superseded_on_as_of": superseded,
        "marking": prepared["marking"],
        "legal_hold": prepared["legal_hold"],
        "retention_labels": list(prepared["retention_labels"]),
        "handbook_is_synthetic": True,
    }


def _withheld_row(prepared: dict, reason: str) -> dict:
    return {
        "document_id": prepared["id"],
        "reason": reason,
        "marking": prepared["marking"],
        "marking_labels": list(prepared["marking_labels"]),
        "legal_hold": prepared["legal_hold"],
        "retention_labels": list(prepared["retention_labels"]),
        "body_copied": False,
        "title_copied": False,
        "labels_preserved": True,
    }


def _statutory_for(topics: list[str], asked: date, point_in_time: bool) -> list[dict]:
    rows: list[dict] = []
    if "leave" in topics:
        rows.append(
            {
                "id": "wtr-reg-13",
                "pin": "Working Time Regulations 1998, regulation 13(1)",
                "url": WTR_REG_13_URL,
                "text": WTR_REG_13_1,
                "extent": "E+W+S",
                "note": WTR_REG_13_A1,
                "opened": LAST_VERIFIED,
                "point_in_time_text_verified": point_in_time,
                "individual_entitlement": False,
            }
        )
        rows.append(
            {
                "id": "wtr-reg-13a",
                "pin": "Working Time Regulations 1998, regulation 13A(2)(e) and (3)",
                "url": WTR_REG_13A_URL,
                "text": WTR_REG_13A_2_E + " " + WTR_REG_13A_3,
                "extent": "E+W+S",
                "note": GOVUK_HOLIDAY_NOTE,
                "govuk_url": GOVUK_HOLIDAY_URL,
                "opened": LAST_VERIFIED,
                "point_in_time_text_verified": point_in_time,
                "individual_entitlement": False,
            }
        )
    if "flexible_working" in topics:
        rows.append(
            {
                "id": "era-1996-s80f",
                "pin": "Employment Rights Act 1996, section 80F",
                "url": ERA_80F_URL,
                "text": ERA_80F_4_A,
                "also": [ERA_80F_1, ERA_80F_2],
                "note": " ".join(
                    (
                        ERA_80F_PAGE_AS_AT,
                        ERA_80F_COMMENCEMENT_NOTE,
                        ERA_2025_80F_UNVERIFIED,
                        SI_2023_1328_NOTE,
                        GOVUK_FLEXIBLE_NOTE,
                    )
                ),
                "instrument_url": SI_2023_1328_URL,
                "govuk_url": GOVUK_FLEXIBLE_URL,
                "day_one_stated": asked >= FLEXIBLE_FROM,
                "earlier_regulation_text_opened": False,
                "era_2025_flexible_working_verified": False,
                "opened": LAST_VERIFIED,
                "point_in_time_text_verified": point_in_time,
                "individual_request_decided": False,
            }
        )
    if "equality" in topics or "conduct" in topics:
        rows.append(
            {
                "id": "ea-2010-s39",
                "pin": "Equality Act 2010, section 39(5) and section 39(2)",
                "url": EA_S39_URL,
                "text": EA_S39_5,
                "also": [EA_S39_2],
                "extent": "E+W+S",
                "note": EA_FUTURE_EFFECTS,
                "opened": LAST_VERIFIED,
                "applied_to_a_person": False,
            }
        )
        rows.append(
            {
                "id": "ea-2010-s20",
                "pin": "Equality Act 2010, section 20(3)",
                "url": EA_S20_URL,
                "text": EA_S20_3,
                "extent": "E+W+S",
                "note": "Sections 20(4) and 20(5) are the physical-feature and auxiliary-aid requirements. This starter does not decide that an adjustment is reasonable for a person.",
                "opened": LAST_VERIFIED,
                "applied_to_a_person": False,
            }
        )
    if "grievance" in topics or "conduct" in topics:
        rows.append(
            {
                "id": "acas-landing",
                "pin": "Acas Code of Practice on disciplinary and grievance procedures",
                "url": ACAS_LANDING_URL,
                "text": ACAS_LANDING_NOTE,
                "opened": LAST_VERIFIED,
                "numbered_paragraphs_reopened": False,
                "applied_to_a_person": False,
            }
        )
    return rows


def _acas_paragraphs(topics: list[str]) -> dict:
    if "grievance" not in topics and "conduct" not in topics:
        return {"called": False, "reason": "not_a_grievance_or_conduct_question", "quotes": []}
    try:
        module = case_sources_module()
    except NeighbourMissing:
        return {"called": False, "reason": "missing", "quotes": []}
    wanted = ("acas_para_1", "acas_para_32", "acas_para_40")
    quotes = []
    for key in wanted:
        row = module.QUOTES.get(key)
        if not isinstance(row, dict):
            continue
        quotes.append(
            {
                "id": row.get("id"),
                "pin": row.get("pin"),
                "text": row.get("text"),
                "url": row.get("url"),
                "last_verified_by": "exp-32-employee-case-intake",
                "last_verified": module.LAST_VERIFIED,
                "reopened_by_this_starter": False,
                "applied_as_a_decision": False,
            }
        )
    return {
        "called": True,
        "experiment_id": "exp-32-employee-case-intake",
        "quotes": quotes,
        "classification_confirmed": False,
    }


def _era(question: str, as_of: date) -> dict:
    if not re.search(
        r"employment rights act 2025|all reasonable steps|preventative duty|unfair dismissal qualifying|tribunal time limit",
        question,
        re.IGNORECASE,
    ):
        return {"called": False, "reason": "not_asked", "reopened_by_this_starter": False}
    try:
        module = era_module()
    except NeighbourMissing:
        return {
            "called": False,
            "reason": "missing",
            "reopened_by_this_starter": False,
            "note": "Employment Rights Act 2025 commencement was not restated.",
        }
    verified = date.fromisoformat(module.LAST_VERIFIED)
    age = (as_of - verified).days
    stale = age < 0 or age > module.DEFAULT_STALE_AFTER_DAYS
    return {
        "called": True,
        "experiment_id": "exp-11-era-2025-hr-assistant",
        "path": ERA_2025_EXPERIMENT,
        "reopened_by_this_starter": ERA_2025_REOPENED_HERE,
        "last_verified": module.LAST_VERIFIED,
        "stale": stale,
        "all_reasonable_steps_in_force_on_as_of": as_of >= module.ALL_REASONABLE_STEPS_IN_FORCE,
        "appointed_for": module.ALL_REASONABLE_STEPS_IN_FORCE.isoformat(),
        "third_party_harassment_in_force_on_as_of": as_of >= module.THIRD_PARTY_IN_FORCE,
        "unfair_dismissal_change_in_force_on_as_of": as_of >= module.UNFAIR_DISMISSAL_IN_FORCE,
        "unfair_dismissal_appointed_for": module.UNFAIR_DISMISSAL_IN_FORCE.isoformat(),
        "tribunal_limits_in_force_on_as_of": as_of >= module.TRIBUNAL_LIMITS_IN_FORCE,
        "specified_steps_regulations_made": module.SPECIFIED_STEPS_REGULATIONS_MADE,
        "compliance_conclusion": None,
        "applied_to_a_person": False,
        "note": (
            "These dates are Experiment 11's pin. This starter did not re-open "
            "the Employment Rights Act 2025 pages on 16 November 2026. It does "
            "not decide that an employer took reasonable steps or all reasonable steps."
        ),
    }


def _categories(text: str) -> dict:
    try:
        module = categories_module()
    except NeighbourMissing:
        return {"called": False, "hits": {}, "classification_confirmed": False}
    hits = module.keyword_hits(text)
    proposed = None
    route = None
    route_label = None
    if hits:
        proposed = next(iter(hits))
        for item in module.CATEGORIES:
            if item["id"] == proposed:
                route = item["route"]
                route_label = item["route_label"]
                break
    return {
        "called": True,
        "experiment_id": "exp-32-employee-case-intake",
        "hits": {key: list(values) for key, values in hits.items()},
        "proposed_category": proposed,
        "proposed_route": route,
        "proposed_route_label": route_label,
        "classification_confirmed": False,
        "used_as_a_decision": False,
    }


def _phrases(text: str) -> dict:
    try:
        module = phrases_module()
    except NeighbourMissing:
        return {"called": False, "categories": [], "phrases_copied": False, "person_labelled": False}
    categories: list[str] = []
    for row in module.find_phrases(text):
        category = row.get("category")
        if isinstance(category, str) and category not in categories:
            categories.append(category)
    return {
        "called": True,
        "experiment_id": "exp-15-vulnerability-urgency-scanner",
        "categories": categories,
        "local_distress": LOCAL_DISTRESS.search(text) is not None,
        "phrases_copied": False,
        "person_labelled": False,
    }


def _gateway(text: str) -> dict:
    try:
        module = gateway_module()
    except NeighbourMissing:
        return {"called": False, "reason": "missing", "redacted_text_copied": False}
    proposal = module.propose(text, caller=CALLER, apply_model_suggestions=False)
    audit = proposal["audit_log"]
    types: list[str] = []
    for finding in audit["findings"]:
        entity = finding.get("entity_type")
        if isinstance(entity, str) and entity not in types:
            types.append(entity)
    return {
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "finding_count": len(audit["findings"]),
        "entity_types": types,
        "raw_values_logged": audit["raw_values_logged"],
        "redacted_text_copied": False,
        "output_is_anonymised": False,
        "values_stored": False,
    }


def _stale(as_of: date) -> dict:
    age = (as_of - PINNED_ON).days
    current = 0 <= age <= STALE_AFTER_DAYS
    return {
        "rules_current": current,
        "pinned_on": PINNED_ON.isoformat(),
        "last_verified": LAST_VERIFIED,
        "age_days": age,
        "stale_after_days": STALE_AFTER_DAYS,
        "refreshed_from_the_web": False,
    }


def _curate(admitted: list[dict], as_of: date) -> dict:
    items = []
    omitted = 0
    for index, prepared in enumerate(admitted, start=1):
        kept_parts = []
        for section in prepared["sections"]:
            if not isinstance(section, dict) or not isinstance(section.get("text"), str):
                continue
            raw = section["text"]
            kept = without_instruction_sentences(raw)
            if kept != raw.strip():
                omitted += 1
            if kept:
                kept_parts.append(kept)
        text = "\n".join(kept_parts)[:500]
        items.append(
            {
                "item_id": f"SYN-SP-{5800 + index}",
                "kind": "page",
                "title": (prepared["title"] or "Handbook page")[:120],
                "url": f"/sites/handbook/{prepared['id']}",
                "content_type": "Guidance",
                "owner": "SYN-OWNER-HR",
                "review_date": "2027-04-01",
                "audience": "staff",
                "last_modified": prepared["effective_from"].isoformat() if prepared["effective_from"] else None,
                "published": True,
                "is_home": index == 1,
                "readers": ["SYN-PRIN-STAFF"],
                "sensitivity": prepared["marking"] if prepared["marking"] in {"OFFICIAL", "OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"} else "OFFICIAL",
                "personal_data_flag": False,
                "links": [],
                "text": text,
            }
        )
    if not items:
        return {
            "called": False,
            "reason": "nothing_admitted",
            "sharepoint_called": False,
            "graph_called": False,
            "human_approval": None,
        }
    snapshot = {
        "synthetic": True,
        "site_id": "SYN-SITE-0058",
        "organisation": ORGANISATION,
        "jurisdiction": "england",
        "sector": "public_service",
        "requesting_user": {"id": "SYN-USER-058", "principals": ["SYN-PRIN-STAFF"]},
        "items": items,
    }
    try:
        module = curate_module()
        draft = module.curate_site(snapshot, as_of)
    except (NeighbourMissing, Exception) as exc:  # noqa: BLE001 — a failed neighbour is not a curation result
        return {
            "called": False,
            "reason": type(exc).__name__,
            "sharepoint_called": False,
            "graph_called": False,
            "human_approval": None,
            "proposals_invented": False,
        }
    types = []
    for proposal in draft.get("proposals") or []:
        kind = proposal.get("type")
        if isinstance(kind, str) and kind not in types:
            types.append(kind)
    return {
        "called": True,
        "experiment_id": draft.get("experiment_id"),
        "outcome": draft.get("outcome"),
        "human_approval": draft.get("human_approval"),
        "sharepoint_called": draft.get("sharepoint_called"),
        "graph_called": draft.get("graph_called"),
        "network_called": draft.get("network_called"),
        "executed": draft.get("executed"),
        "proposal_count": len(draft.get("proposals") or []),
        "proposal_types": types,
        "text_recorded_by_curator": draft.get("text_recorded"),
        "injection_sentences_omitted": omitted,
        "secret_bodies_sent": False,
        "proposals_copied": False,
    }


def _route(result: dict, named: str, reason: str, answer: str) -> dict:
    result["human_route"] = {"always_available": True, "named": named, "reason": reason}
    return _finish(result, "routed_to_human", answer, rely=False)


def _quantity_problem(text: str) -> str | None:
    if CALC.search(text) is None:
        return None
    if UNPARSEABLE_QTY.search(text):
        return "unparseable_quantity"
    for match in re.finditer(r"\b(\d+)\b", text):
        if int(match.group(1)) > 366:
            return "out_of_range_quantity"
    return None


def answer_handbook(
    question: object,
    handbook: dict,
    scope: dict,
    as_of: object,
    about_date: object = None,
    *,
    include_curation: bool = False,
) -> dict:
    """Return one JSON answer. ``human_approval`` stays null."""

    result = _base(None)
    if not isinstance(handbook, dict) or handbook.get("synthetic") is not True:
        return _finish(
            result,
            "refused",
            "The handbook is not marked synthetic. Nothing was copied.",
            rely=False,
        )
    if handbook.get("organisation") != ORGANISATION:
        result["organisation"] = handbook.get("organisation") if isinstance(handbook.get("organisation"), str) else ORGANISATION
        result["organisation_is_fictional"] = handbook.get("organisation_is_fictional") is True

    text, stripped_keys = _question_text(question)
    result["prompt_injection"] = scan_text(text)
    if stripped_keys:
        result["prompt_injection"]["detected"] = True
        result["prompt_injection"]["signals"] = result["prompt_injection"]["signals"] + [
            f"prohibited_key:{key}" for key in stripped_keys
        ]
    result["masking"] = {
        "local": mask_counts(text),
        "described_as_anonymised": False,
    }
    result["experiment_08"] = _gateway(text)
    result["experiment_15"] = _phrases(text)
    cleaned = without_instruction_sentences(text)

    scope_problem = _scope_problem(scope)
    if scope_problem:
        result["human_route"]["reason"] = scope_problem
        return _finish(
            result,
            "needs_human",
            "The HR scope could not be read. It was not replaced with a default ceiling or an empty approval. A person needs to confirm the scope.",
            rely=False,
        )
    result["scope_reference"] = scope["approval_reference"]

    as_of_day = parse_day(as_of)
    if as_of_day is None:
        result["human_route"]["reason"] = "unparseable_as_of"
        return _finish(
            result,
            "needs_human",
            "The as-of date could not be read. It has not been replaced with today or with zero.",
            rely=False,
        )
    result["as_of"] = as_of_day.isoformat()
    if about_date not in (None, ""):
        asked = parse_day(about_date)
        if asked is None:
            result["human_route"]["reason"] = "unparseable_about_date"
            return _finish(
                result,
                "needs_human",
                "The date the question is about could not be read. It has not been replaced with the as-of date or with zero.",
                rely=False,
            )
    else:
        asked = as_of_day
    result["about_date"] = None if about_date in (None, "") else asked.isoformat()
    result["date_asked_about"] = asked.isoformat()
    result["stale"] = _stale(as_of_day)
    result["sources"] = source_rows(result["stale"]["rules_current"])

    if not cleaned.strip():
        if result["prompt_injection"]["detected"]:
            result["human_route"]["reason"] = "instruction_not_followed"
            return _finish(
                result,
                "refused_injection",
                "The instruction was not followed. No source was approved, no marking or legal hold was removed, and no entitlement was granted.",
                rely=False,
            )
        result["human_route"]["reason"] = "empty_question"
        return _finish(
            result,
            "needs_human",
            "There is no question to answer once instructions are set aside.",
            rely=False,
        )

    categories = result["experiment_15"]["categories"] if result["experiment_15"].get("called") else []
    urgent = LOCAL_DISTRESS.search(text) is not None or bool(ROUTE_URGENT.intersection(categories))
    if urgent:
        result["experiment_32"] = _categories(cleaned)
        return _route(
            result,
            "HR duty officer, and the organisation's safeguarding route",
            "distress_or_safeguarding",
            "This is for a person, not a routine handbook answer. The route is the HR duty officer and the organisation's safeguarding route. Nothing in the question has been decided.",
        )

    personal = CASE_PERSONAL.search(cleaned) is not None
    quantity = _quantity_problem(cleaned)
    if quantity:
        result["human_route"]["reason"] = quantity
        result["computed_balance"] = None
        return _finish(
            result,
            "needs_human",
            "A figure in this question is out of range or cannot be read. It has not been replaced with zero, and no balance was calculated.",
            rely=False,
        )

    if NI.search(cleaned):
        return _finish(
            result,
            "refused_jurisdiction",
            "This starter does not state Northern Ireland employment law. The Working Time Regulations 1998 and Equality Act 2010 provisions opened here are marked England and Wales and Scotland. The flexible-working instrument extends to England and Wales and Scotland. GOV.UK says flexible-working rules are different in Northern Ireland.",
            rely=False,
        )

    case = _categories(cleaned)
    result["experiment_32"] = case
    if personal and (PREGNANCY.search(cleaned) or MEDICAL.search(cleaned) or re.search(r"\b(my health|off sick|fit note|disability)\b", cleaned, re.I)):
        return _route(
            result,
            "HR adviser",
            "personal_health_pregnancy_or_disability",
            "This is a personal question. The route is an HR adviser. This assistant does not give medical advice or individual legal advice, and it does not decide an adjustment, sick pay, or maternity entitlement.",
        )
    if personal and TAX.search(cleaned):
        return _route(
            result,
            "A tax adviser, or HMRC. Not this assistant",
            "tax",
            "This assistant does not give tax advice. The route is a tax adviser or HMRC, and HR if the question is also about the handbook.",
        )
    if personal or (case.get("proposed_category") in {"grievance", "harassment", "protected_disclosure"} and personal):
        named = case.get("proposed_route_label") or "HR duty officer"
        if case.get("proposed_category") == "protected_disclosure":
            named = "Designated whistleblowing officer"
        return _route(
            result,
            named,
            "personal_or_sensitive_case",
            "This is a personal or sensitive case. The named route has it. The category is a proposal from Experiment 32 and is not confirmed. This assistant does not decide the case or an entitlement, and the question text is not copied.",
        )
    if case.get("proposed_category") in {"grievance", "harassment", "protected_disclosure"} and re.search(
        r"\b(i|my|me)\b", cleaned, re.IGNORECASE
    ):
        named = case.get("proposed_route_label") or "HR duty officer"
        return _route(
            result,
            named,
            "personal_or_sensitive_case",
            "This is a personal or sensitive case. The named route has it. This assistant does not decide it.",
        )

    if not isinstance(handbook.get("documents"), list):
        return _finish(result, "refused", "The handbook has no document list.", rely=False)

    approved = set(scope["approved_document_ids"])
    ceiling = scope["handbook_ceiling"]
    prepared = [_prepare(document) for document in handbook["documents"] if isinstance(document, dict)]
    result["embedded_approval_markers_ignored"] = [
        item["id"] for item in prepared if item["file_approval_marker"]
    ]
    withheld = []
    admitted = []
    for item in prepared:
        if item["id"] not in approved:
            continue
        if not item["dates_ok"]:
            result["unparsed_documents"].append(
                {"document_id": item["id"], "reason": "unparseable_effective_date", "used": False}
            )
            continue
        if item["marking"] is None or above_ceiling(item["marking"], ceiling):
            withheld.append(_withheld_row(item, "marking_above_ceiling_or_missing"))
            continue
        admitted.append(item)
    result["withheld"] = withheld

    topics = _topics(cleaned)
    in_force = []
    conflicts = []
    for item in admitted:
        if item["topic"] not in topics and not (item["topic"] == "conduct" and "era_2025" in topics):
            continue
        state = in_force_on(
            {"effective_from": item["effective_from"].isoformat(), "effective_to": item["effective_to"].isoformat() if item["effective_to"] else None},
            asked,
        )
        if state is True:
            in_force.append(item)
    by_topic: dict[str, list[dict]] = {}
    for item in in_force:
        by_topic.setdefault(item["topic"], []).append(item)
    chosen: list[dict] = []
    for topic, group in by_topic.items():
        if len(group) > 1:
            conflicts.append(topic)
            continue
        chosen.append(group[0])
    if conflicts:
        result["human_route"]["reason"] = "overlapping_versions"
        return _finish(
            result,
            "needs_human",
            "More than one approved version is in force on the date asked about. Neither was chosen.",
            rely=False,
        )

    point_in_time = asked >= PINNED_ON
    result["statutory"] = _statutory_for(topics, asked, point_in_time)
    result["experiment_11"] = _era(cleaned, as_of_day)
    if "grievance" in topics or "conduct" in topics:
        acas = _acas_paragraphs(topics)
        result["experiment_32"]["acas"] = {
            "called": acas["called"],
            "reopened_by_this_starter": False,
            "quote_ids": [row["id"] for row in acas.get("quotes") or []],
        }
        for row in acas.get("quotes") or []:
            result["statutory"].append(
                {
                    "id": row["id"],
                    "pin": row["pin"],
                    "url": row["url"],
                    "text": row["text"],
                    "source": "experiment_32_pin",
                    "last_verified": row["last_verified"],
                    "reopened_by_this_starter": False,
                    "applied_as_a_decision": False,
                }
            )

    if not chosen:
        if include_curation:
            result["experiment_50"] = _curate(admitted, as_of_day)
        rely = result["stale"]["rules_current"] and not result["statutory"]
        gap = "The approved handbook does not cover this question."
        if result["statutory"]:
            gap += " Statutory pins that were opened are listed separately. They are not advice about a person, and they are not the handbook."
            rely = False
        return _finish(result, "not_covered", gap, rely=rely)

    handbook_parts = []
    version_bits = []
    document_signals: list[str] = []
    for item in chosen:
        if item["injection"]["detected"]:
            for signal in item["injection"]["signals"]:
                if signal not in document_signals:
                    document_signals.append(signal)
        sections = _quote_sections(item)
        if not sections:
            continue
        handbook_parts.append(" ".join(section["text"] for section in sections))
        for section in sections:
            result["citations"].append(_citation(item, section, asked, as_of_day))
            if section["section_id"] not in result["copied"]["handbook_section_ids"]:
                result["copied"]["handbook_section_ids"].append(section["section_id"])
        later = [
            other
            for other in admitted
            if other["topic"] == item["topic"] and other["id"] != item["id"] and other["effective_from"] and as_of_day >= other["effective_from"] and (other["effective_to"] is None or as_of_day <= other["effective_to"])
        ]
        if item["effective_to"] is not None and as_of_day > item["effective_to"]:
            later_name = later[0]["id"] if later else "none in the approved set"
            version_bits.append(
                f"The version in force on {asked.isoformat()} is {item['id']} version {item['version']}, "
                f"effective from {item['effective_from'].isoformat()} to {item['effective_to'].isoformat()}. "
                f"It is not the version in force on {as_of_day.isoformat()}. "
                f"The version in force on that later date is {later_name}."
            )
        else:
            version_bits.append(
                f"The version in force on {asked.isoformat()} is {item['id']} version {item['version']}, "
                f"effective from {item['effective_from'].isoformat()}."
            )
    quoted_blob = " ".join(handbook_parts)
    quoted_injection = scan_text(quoted_blob)
    result["document_injection"] = {
        "detected": bool(document_signals),
        "followed": False,
        "signals": document_signals,
        "sentences_quoted": quoted_injection["detected"],
    }
    result["version_note"] = " ".join(version_bits)
    combined = "\n".join(handbook_parts)
    result["claims"] = _claims(cleaned, combined)
    claim_sentences = []
    for claim in result["claims"]:
        if claim["included"]:
            claim_sentences.append(f"The handbook includes {claim['phrase']}.")
        elif claim["denied"]:
            claim_sentences.append(
                f"The handbook says it is not true that this includes {claim['phrase']}. That denial is not an inclusion."
            )
        else:
            claim_sentences.append(f"The handbook does not include {claim['phrase']}.")

    statutory_line = ""
    if result["statutory"]:
        statutory_line = " Statutory pins are cited separately and are not the handbook."
    era_line = ""
    if result["experiment_11"].get("called"):
        in_force_flag = result["experiment_11"]["all_reasonable_steps_in_force_on_as_of"]
        era_line = (
            " Experiment 11's pin, not re-opened here, "
            + ("treats the 'all reasonable steps' wording as in force on this as-of date." if in_force_flag else "does not treat the 'all reasonable steps' wording as in force on this as-of date.")
            + " This assistant does not decide compliance."
        )
    stale_line = ""
    rely = result["stale"]["rules_current"]
    if not rely:
        stale_line = " The statutory pin is stale and has not been refreshed. Do not rely on it until a person checks the source."
    answer = (
        result["version_note"]
        + " "
        + combined
        + (" " + " ".join(claim_sentences) if claim_sentences else "")
        + statutory_line
        + era_line
        + stale_line
        + " The handbook is synthetic. This is not a decision on an individual's entitlement, and it is not legal, medical, or tax advice."
    )
    if include_curation:
        result["experiment_50"] = _curate([item for item in admitted if item["marking"] == "OFFICIAL"], as_of_day)
    return _finish(result, "answered", answer, rely=rely and bool(result["citations"]))


def acknowledge(result: dict, review: object) -> dict:
    """Record that HR has seen the answer. Markers inside the question do not call this."""

    updated = deepcopy(result)
    updated["entitlement_decision"] = None
    updated["flags"]["entitlement_decided"] = False
    updated["flags"]["sent"] = False
    updated["flags"]["written"] = False
    if not isinstance(review, dict):
        updated["human_approval"] = None
        updated["acknowledgement"] = {"recorded": False, "reason": "not_a_review_object"}
        return updated
    if review.get("actor_role") != HR_ROLE or review.get("seen") is not True:
        updated["human_approval"] = None
        updated["acknowledgement"] = {"recorded": False, "reason": "not_the_hr_step"}
        return updated
    if review.get("approval_reference") != result.get("scope_reference"):
        updated["human_approval"] = None
        updated["acknowledgement"] = {"recorded": False, "reason": "reference_mismatch"}
        return updated
    updated["human_approval"] = {
        "recorded": True,
        "actor_role": HR_ROLE,
        "effect": "seen",
        "sources_changed": False,
        "sent": False,
        "written": False,
        "entitlement_decision": None,
    }
    updated["acknowledgement"] = {"recorded": True, "reason": "hr_has_seen_the_answer"}
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Answer one synthetic handbook question.")
    parser.add_argument("--handbook", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--about", default=None)
    parser.add_argument("--curate", action="store_true")
    args = parser.parse_args(argv)
    handbook = json.loads(Path(args.handbook).read_text(encoding="utf-8"))
    scope = json.loads(Path(args.scope).read_text(encoding="utf-8"))
    question = json.loads(Path(args.question).read_text(encoding="utf-8"))
    result = answer_handbook(
        question,
        handbook,
        scope,
        args.as_of,
        args.about,
        include_curation=args.curate,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if result["outcome"] in {"answered", "not_covered", "routed_to_human", "needs_human", "refused_jurisdiction"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
