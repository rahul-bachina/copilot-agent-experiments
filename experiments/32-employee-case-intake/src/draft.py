#!/usr/bin/env python3
"""Draft an HR case intake for one synthetic narrative.

The draft proposes a category, an urgency flag, a statutory or Acas time
reference, and a route. An HR officer confirms classification and routing.
This module does not decide an outcome, advise on merits, contact the
employee or a manager, or write to an HR system.

UK identifiers go through Experiment 08. Urgency indicators go through
Experiment 15, which itself calls Experiment 08 before any model. Optional
attachments go through Experiment 12. None of those detectors is copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from case_categories import (
        CATEGORIES,
        CATEGORY_IDS,
        ROUTES,
        UNRESOLVED_ROUTE,
        keyword_hits,
        special_category_indicators,
    )
    from case_injection import blank_instruction_lines, scan_narrative
    from case_sources import (
        DATA_PROTECTION_IDS,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        GATEWAY_CALLER,
        GATEWAY_CATALOGUE_ID,
        GATEWAY_EXPERIMENT_ID,
        GB_JURISDICTIONS,
        INTAKE_CATALOGUE_ID,
        INTAKE_EXPERIMENT_ID,
        LAST_VERIFIED,
        PART_IVA_HEADINGS,
        QUOTES,
        SCANNER_CATALOGUE_ID,
        SCANNER_EXPERIMENT_ID,
        SOURCES_PINNED_ON,
        CATALOGUE_ID,
    )
else:
    from .case_categories import (
        CATEGORIES,
        CATEGORY_IDS,
        ROUTES,
        UNRESOLVED_ROUTE,
        keyword_hits,
        special_category_indicators,
    )
    from .case_injection import blank_instruction_lines, scan_narrative
    from .case_sources import (
        DATA_PROTECTION_IDS,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        GATEWAY_CALLER,
        GATEWAY_CATALOGUE_ID,
        GATEWAY_EXPERIMENT_ID,
        GB_JURISDICTIONS,
        INTAKE_CATALOGUE_ID,
        INTAKE_EXPERIMENT_ID,
        LAST_VERIFIED,
        PART_IVA_HEADINGS,
        QUOTES,
        SCANNER_CATALOGUE_ID,
        SCANNER_EXPERIMENT_ID,
        SOURCES_PINNED_ON,
        CATALOGUE_ID,
    )

LABEL = "DRAFT FOR HR CONFIRMATION"
HR_ROLE = "HR officer"
CONFIRM = "confirm_classification_and_routing"
RETURN = "return_for_edit"
DECISIONS = frozenset({CONFIRM, RETURN})
MAX_CHARS = 20_000
CASE_ID = __import__("re").compile(r"^[A-Za-z0-9_-]{1,40}$")

PROHIBITED_KEYS = frozenset(
    {
        "proposed_category",
        "category",
        "urgency",
        "routing",
        "classification_confirmed",
        "routing_confirmed",
        "outcome",
        "hr_decision",
        "merits",
        "contact_employee",
        "contact_manager",
        "write_hr_system",
        "approved",
        "anonymised",
        "anonymized",
        "article_9_condition",
        "protected_disclosure_decided",
    }
)

BY_ID = {item["id"]: item for item in CATEGORIES}

URGENCY_SAME_DAY = frozenset(
    {"possible_self_harm_risk", "possible_safeguarding_risk"}
)
URGENCY_TIME = frozenset(
    {"possible_deadline_or_time_limit", "possible_financial_hardship"}
)


class CaseForbidden(RuntimeError):
    """The intake has no outcome, contact, or HR-system path."""


class NotSynthetic(ValueError):
    """The case was not marked synthetic. The message does not include the narrative."""


def _load_scan():
    scanner_src = (
        Path(__file__).resolve().parents[2]
        / "15-vulnerability-urgency-scanner"
        / "src"
    )
    if not scanner_src.is_dir():
        raise CaseForbidden(
            "Experiment 15 is not beside this experiment. Urgency will not be reinvented."
        )
    inserted = str(scanner_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import scan as scan_module

    if scan_module.CALLER != SCANNER_EXPERIMENT_ID:
        raise CaseForbidden("the scanner module is not Experiment 15")
    return scan_module


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise CaseForbidden(
            "Experiment 12 is not beside this experiment. Attachments will not be reinvented."
        )
    inserted = str(intake_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import intake as intake_module

    if intake_module.EXPERIMENT_ID != INTAKE_EXPERIMENT_ID:
        raise CaseForbidden("the intake module is not Experiment 12")
    return intake_module


def _load_propose():
    gateway_src = (
        Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    )
    if not gateway_src.is_dir():
        raise CaseForbidden(
            "Experiment 08 is not beside this experiment. This draft will not invent a redactor."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def decide_outcome(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not decide an outcome")


def advise_on_merits(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not advise on merits")


def contact_employee(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not contact the employee")


def contact_manager(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not contact a manager")


def write_hr_system(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not write to an HR system")


def send_external(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not send anything")


def approve_case(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not approve a case")


def reject_case(*_args, **_kwargs) -> None:
    raise CaseForbidden("the agent does not reject a case")


def _strip_prohibited(mapping: dict) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            found.append(key)
            del mapping[key]
    return found


def _quote(quote_id: str, *, conditional: bool = False) -> dict:
    row = dict(QUOTES[quote_id])
    row["retrieved"] = LAST_VERIFIED
    row["conditional"] = conditional
    row["decides_the_case"] = False
    return row


def _jurisdiction(value) -> dict:
    if value is None or value == "":
        return {
            "supplied": False,
            "value": None,
            "recognised": False,
            "gb_sources_applied": True,
            "note": (
                "Jurisdiction was not supplied. Great Britain sources are quoted "
                "for the HR officer to confirm. That is not a finding that the "
                "employment is in England, Wales, or Scotland."
            ),
        }
    if not isinstance(value, str):
        return {
            "supplied": True,
            "value": None,
            "recognised": False,
            "gb_sources_applied": False,
            "note": "Jurisdiction was not a string. Statutory references are not applied.",
        }
    token = value.strip().lower().replace(" ", "_")
    if token == "northern_ireland":
        return {
            "supplied": True,
            "value": token,
            "recognised": True,
            "gb_sources_applied": False,
            "note": QUOTES["ni_not_applied"]["text"],
        }
    if token in GB_JURISDICTIONS:
        return {
            "supplied": True,
            "value": token,
            "recognised": True,
            "gb_sources_applied": True,
            "note": "Sources marked E+W+S on the pages opened are quoted. This is not a finding about the contract.",
        }
    return {
        "supplied": True,
        "value": token,
        "recognised": False,
        "gb_sources_applied": False,
        "note": "Jurisdiction was not recognised. Statutory references are not applied.",
    }


def _classification(hits: dict[str, list[str]]) -> dict:
    matched = [item["id"] for item in CATEGORIES if item["id"] in hits]
    tie = len(matched) > 1
    if len(matched) == 1:
        proposed = matched[0]
    else:
        proposed = "unresolved"
    return {
        "proposed_category": proposed,
        "matched_categories": matched,
        "tie": tie,
        "keyword_hits": hits,
        "decided": False,
        "method": "closed_keyword_list",
    }


def _route(classification: dict) -> str:
    matched = classification["matched_categories"]
    if "protected_disclosure" in matched:
        return "designated_whistleblowing_officer"
    if len(matched) == 1:
        return BY_ID[matched[0]]["route"]
    return UNRESOLVED_ROUTE


def _summary(route: str, category: str, urgency: str, *, confidential: bool) -> str:
    if confidential:
        return (
            f"Proposed category: {category}. Proposed route: {route}. "
            f"Urgency proposal: {urgency}. "
            "Identity and the substance of the narrative are not in this summary. "
            "Do not notify the employee, a line manager, or the subject of the "
            "disclosure from this draft. An HR officer confirms classification and routing."
        )
    return (
        f"Proposed category: {category}. Proposed route: {route}. "
        f"Urgency proposal: {urgency}. "
        "The narrative is not in this summary. "
        "An HR officer confirms classification and routing. "
        "The agent does not contact the employee or a manager."
    )


def _time_references(matched: list[str], *, apply_gb: bool, application_made_on) -> list[dict]:
    if not apply_gb:
        return [_quote("ni_not_applied")]
    if not matched:
        return [
            {
                "id": "no_category_keyword",
                "instrument": None,
                "pin": None,
                "text": "No category keyword matched. No statutory or Acas time reference is attached.",
                "applied_as_deadline": False,
                "days_encoded": None,
                "conditional": False,
                "decides_the_case": False,
                "retrieved": LAST_VERIFIED,
            }
        ]
    rows: list[dict] = []
    seen: set[str] = set()
    for category_id in matched:
        for quote_id in BY_ID[category_id]["time_reference_ids"]:
            if quote_id in seen:
                continue
            seen.add(quote_id)
            conditional = category_id == "harassment" and quote_id == "acas_para_33"
            row = _quote(quote_id, conditional=conditional)
            if quote_id == "era_80g_1b":
                row["application_made_on_supplied"] = (
                    application_made_on.isoformat() if application_made_on else None
                )
                row["last_day_calculated"] = False
                row["narrative_date_ignored"] = True
            if conditional:
                row["note"] = (
                    "Paragraph 33 is quoted only if the employer is handling the "
                    "matter as a grievance. This starter does not decide that. "
                    "Section 26 does not state a meeting period."
                )
            rows.append(row)
    return rows


def _urgency(categories: list[str], *, scanned: bool) -> dict:
    if not scanned:
        flag = "not_scanned"
        source = "not_called"
    elif any(item in URGENCY_SAME_DAY for item in categories):
        flag = "same_day_officer_review"
        source = "experiment_15"
    elif any(item in URGENCY_TIME for item in categories):
        flag = "time_sensitive_officer_review"
        source = "experiment_15"
    else:
        flag = "routine_officer_review"
        source = "experiment_15"
    return {
        "proposed_flag": flag,
        "source": source,
        "indicator_categories": categories,
        "indicator_count": 0,
        "person_labelled_vulnerable": False,
        "queue_priority_changed": False,
        "certified_safe": False,
        "statement": (
            "Possible indicator from Experiment 15, or no indicator. "
            "Not a finding that a person is vulnerable, and not a change to a queue."
        ),
    }


def _gateway_view(proposal: dict | None, *, called: bool, reason: str | None) -> dict:
    if not called or proposal is None:
        return {
            "called": False,
            "reason": reason,
            "caller": GATEWAY_CALLER,
            "experiment_id": GATEWAY_EXPERIMENT_ID,
            "catalogue_id": GATEWAY_CATALOGUE_ID,
            "finding_count": 0,
            "entity_types": [],
            "output_is_anonymised": False,
            "agent_may_release": False,
            "raw_values_logged": False,
            "called_before_any_model": True,
            "redacted_text_stored": False,
        }
    audit = proposal["audit_log"]
    entity_types: list[str] = []
    for finding in audit["findings"]:
        if finding.get("applied") and finding["entity_type"] not in entity_types:
            entity_types.append(finding["entity_type"])
    return {
        "called": True,
        "reason": None,
        "caller": audit["caller"],
        "experiment_id": GATEWAY_EXPERIMENT_ID,
        "catalogue_id": GATEWAY_CATALOGUE_ID,
        "finding_count": len(audit["findings"]),
        "entity_types": entity_types,
        "input_sha256": audit["input_sha256"],
        "rules_pinned_on": audit["rules_pinned_on"],
        "rules_stale": bool(audit["rules_stale"]),
        "output_is_anonymised": False,
        "agent_may_release": False,
        "raw_values_logged": False,
        "called_before_any_model": True,
        "redacted_text_stored": False,
    }


def _scanner_view(result: dict | None, *, called: bool) -> dict:
    if not called or result is None:
        return {
            "called": False,
            "experiment_id": SCANNER_EXPERIMENT_ID,
            "catalogue_id": SCANNER_CATALOGUE_ID,
            "flag_count": 0,
            "categories": [],
            "redacted_text_stored": False,
            "injection_followed": False,
            "person_labelled_vulnerable": False,
        }
    categories = []
    for flag in result["flags"]:
        if flag["category"] not in categories:
            categories.append(flag["category"])
    return {
        "called": True,
        "experiment_id": result["scanner"],
        "catalogue_id": result["catalogue_id"],
        "flag_count": len(result["flags"]),
        "categories": categories,
        "redacted_text_stored": False,
        "injection_followed": False,
        "person_labelled_vulnerable": False,
    }


def _slim_intake(draft: dict) -> dict:
    files = []
    for row in draft["files"]:
        files.append(
            {
                "file_id": row["file_id"],
                "read_status": row["read_status"],
                "date_status": row["date_status"],
                "suggested_class": row["suggested_class"],
                "pii_finding_count": row["pii"]["finding_count"],
                "content_recorded": False,
            }
        )
    return {
        "called": True,
        "experiment_id": draft["experiment_id"],
        "catalogue_id": draft["catalogue_id"],
        "files_confirmed": False,
        "purpose_confirmed": False,
        "requested_purpose": "general_records",
        "injection_detected": draft["prompt_injection"]["detected"],
        "injection_followed": False,
        "gateway_output_is_anonymised": False,
        "files": files,
        "narrative_not_copied": True,
    }


def _parse_application_date(raw) -> date | None:
    if raw is None or raw == "":
        return None
    if not isinstance(raw, str):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _received(raw, as_of: date) -> dict:
    if raw is None or raw == "":
        return {"status": "missing", "value": None}
    if not isinstance(raw, str):
        return {"status": "invalid", "value": None}
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        return {"status": "invalid", "value": None}
    if parsed > as_of:
        return {"status": "future", "value": parsed.isoformat()}
    age = (as_of - parsed).days
    status = "outside_window" if age > DEFAULT_STALE_AFTER_DAYS else "within_window"
    return {"status": status, "value": parsed.isoformat(), "age_days": age}


def draft_case(
    case: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    rules_as_of: date | None = None,
) -> dict:
    """Return one intake draft. Confirmation flags stay false."""

    if not isinstance(case, dict):
        raise TypeError("case must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if rules_as_of is not None and (
        not isinstance(rules_as_of, date) or isinstance(rules_as_of, datetime)
    ):
        raise TypeError("rules_as_of must be a date")
    if case.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")

    working = dict(case)
    prohibited = _strip_prohibited(working)
    case_id = working.get("case_id")
    if not isinstance(case_id, str) or not CASE_ID.fullmatch(case_id):
        raise ValueError("case_id must be 1 to 40 letters, digits, hyphens, or underscores")
    narrative = working.get("narrative", "")
    if not isinstance(narrative, str):
        raise TypeError("narrative must be a string")

    oversized = len(narrative) > MAX_CHARS
    narrative_hash = hashlib.sha256(narrative.encode("utf-8")).hexdigest()
    age_days = (as_of - SOURCES_PINNED_ON).days
    sources_stale = age_days > stale_after_days

    injection = scan_narrative(narrative) if not oversized else {
        "detected": False,
        "followed": False,
        "zero_width_characters_removed": 0,
        "signals": [],
        "not_scanned": True,
    }
    blanked = "" if oversized else blank_instruction_lines(narrative)
    hits = {} if oversized else keyword_hits(blanked)
    classification = _classification(hits)
    if oversized:
        classification["proposed_category"] = "unresolved"
        classification["not_scanned_reason"] = "narrative_over_character_cap"

    jurisdiction = _jurisdiction(working.get("jurisdiction"))
    confidential = "protected_disclosure" in classification["matched_categories"]
    route = _route(classification)
    application_made_on = _parse_application_date(working.get("application_made_on"))

    gateway_proposal = None
    scan_result = None
    if not oversized:
        propose = _load_propose()
        gateway_proposal = propose(
            narrative,
            caller=GATEWAY_CALLER,
            rules_as_of=rules_as_of,
            apply_model_suggestions=False,
            reversible=False,
        )
        scan_result = _load_scan().scan(narrative, synthetic=True)

    scanner = _scanner_view(scan_result, called=scan_result is not None)
    urgency = _urgency(scanner["categories"], scanned=scanner["called"])
    urgency["indicator_count"] = scanner["flag_count"]
    summary = _summary(
        route,
        classification["proposed_category"],
        urgency["proposed_flag"],
        confidential=confidential,
    )

    document_intake = None
    attachments = working.get("attachments")
    if attachments is not None:
        if not isinstance(attachments, list) or not attachments:
            raise ValueError("attachments must be a non-empty list of files or omitted")
        batch = {
            "synthetic": True,
            "batch_id": case_id,
            "requested_purpose": "general_records",
            "files": attachments,
        }
        intake_draft = _load_intake().intake(
            batch,
            as_of=as_of,
            stale_after_days=stale_after_days,
            rules_as_of=rules_as_of,
        )
        document_intake = _slim_intake(intake_draft)

    indicators = [] if oversized else special_category_indicators(blanked)
    time_references = _time_references(
        classification["matched_categories"],
        apply_gb=jurisdiction["gb_sources_applied"] and not oversized,
        application_made_on=application_made_on,
    )
    if oversized:
        time_references = [
            {
                "id": "narrative_not_scanned",
                "instrument": None,
                "pin": None,
                "text": (
                    "The narrative is over 20,000 characters. It was not classified "
                    "and it was not scanned. A safeguarding phrase in it is not detected."
                ),
                "applied_as_deadline": False,
                "days_encoded": None,
                "conditional": False,
                "decides_the_case": False,
                "retrieved": LAST_VERIFIED,
            }
        ]

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "case_id": case_id,
        "as_of": as_of.isoformat(),
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_age_days": age_days,
        "sources_stale": sources_stale,
        "rules_current": not sources_stale,
        "stale_after_days": stale_after_days,
        "narrative_stored": False,
        "narrative_sha256": narrative_hash,
        "narrative_char_count": len(narrative),
        "narrative_over_cap": oversized,
        "classification": classification,
        "routing": {
            "proposed_route": route,
            "proposed_route_label": ROUTES[route],
            "confirmed": False,
            "queue_priority_changed": False,
            "handed_off": False,
            "channel_used_for_routing": False,
        },
        "routing_summary": summary,
        "urgency": urgency,
        "time_references": time_references,
        "data_protection_references": [_quote(item) for item in DATA_PROTECTION_IDS],
        "part_iva_headings_verified": [
            {"section": section, "heading": heading} for section, heading in PART_IVA_HEADINGS
        ],
        "section_43i_on_contents_page": False,
        "special_category": {
            "article_9_1_quoted": True,
            "indicators": indicators,
            "may_be_present": bool(indicators),
            "sexual_harassment_may_engage_article_9": (
                "sexual harassment" in hits.get("harassment", [])
            ),
            "article_9_condition_asserted": False,
            "schedule_1_paragraph_1_met": None,
            "appropriate_policy_document_checked": False,
            "routing_summary_omits_narrative": True,
            "note": (
                "UK GDPR Article 9(1) prohibits the listed processing unless a "
                "condition applies. Data Protection Act 2018 section 10(2) requires "
                "a condition in Part 1 of Schedule 1 before Article 9(2)(b) is met. "
                "Schedule 1 paragraph 1(1) also requires an appropriate policy document. "
                "This draft decides none of that. A sexual-harassment keyword is not "
                "a finding that data concerning sex life is present."
            ),
        },
        "whistleblowing_confidentiality": {
            "applies": confidential,
            "identity_in_routing_summary": False,
            "narrative_in_routing_summary": False,
            "do_not_notify": [
                "the employee",
                "a line manager",
                "the subject of the disclosure",
            ],
            "proposed_route_when_language_present": (
                "designated_whistleblowing_officer" if confidential else None
            ),
            "section_43j_quoted": confidential and jurisdiction["gb_sources_applied"],
            "section_43j_applied_as_a_finding": False,
            "protected_disclosure_decided": False,
            "agent_contacted_anyone": False,
        },
        "automated_decision": {
            "uk_gdpr_article_22_status": "substituted",
            "substituted_by": "Data (Use and Access) Act 2025 section 80",
            "in_force_note": (
                "Section 80 is in force at 5 February 2026 in so far as not already "
                "in force, by SI 2026/82 regulation 2(j)."
            ),
            "solely_automated_decision": False,
            "significant_decision": False,
            "meaningful_human_involvement_on_confirmation": True,
            "note": (
                "Article 22A(1) defines a decision based solely on automated "
                "processing as one with no meaningful human involvement, and a "
                "significant decision as one with a legal effect or a similarly "
                "significant effect. This output is a proposal. The HR officer "
                "confirms classification and routing."
            ),
        },
        "jurisdiction": jurisdiction,
        "received_on": _received(working.get("received_on"), as_of),
        "received_on_overrides_narrative": False,
        "application_made_on": (
            application_made_on.isoformat() if application_made_on else None
        ),
        "prompt_injection": injection,
        "pii_gateway": _gateway_view(
            gateway_proposal,
            called=gateway_proposal is not None,
            reason="narrative_over_character_cap" if oversized else None,
        ),
        "vulnerability_scanner": scanner,
        "document_intake": document_intake,
        "hr_confirmation": {
            "classification_confirmed": False,
            "routing_confirmed": False,
            "approver": HR_ROLE,
            "decision": None,
            "category_recorded": None,
            "route_recorded": None,
        },
        "outcome": None,
        "merits_advice": None,
        "contacted_employee": False,
        "contacted_manager": False,
        "hr_system_written": False,
        "external_sent": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "prohibited_payload_keys": prohibited,
        "flags": {
            "outcome_decided": False,
            "merits_advised": False,
            "employee_contacted": False,
            "manager_contacted": False,
            "hr_system_written": False,
            "external_sent": False,
            "classification_confirmed_by_narrative": False,
            "routing_confirmed_by_narrative": False,
            "article_9_condition_asserted": False,
            "protected_disclosure_decided": False,
            "harassment_decided": False,
        },
        "human_approval": [
            {
                "action": "Confirm the classification",
                "approver": HR_ROLE,
                "mandatory": True,
                "done_by_agent": False,
            },
            {
                "action": "Confirm the routing",
                "approver": HR_ROLE,
                "mandatory": True,
                "done_by_agent": False,
            },
        ],
        "limitations": _limitations(oversized=oversized, sources_stale=sources_stale),
    }
    _force(draft)
    if len(narrative) > 80:
        echoed = json.dumps(
            {key: value for key, value in draft.items() if key != "narrative_sha256"}
        )
        if narrative in echoed:
            raise CaseForbidden("the draft echoed the narrative")
    return draft


def _limitations(*, oversized: bool, sources_stale: bool) -> list[str]:
    notes = [
        "A keyword is not a decision that the statutory definition is met.",
        "The Acas Code says 'without unreasonable delay'. This starter does not turn that into a number of days.",
        "Section 80G(1B)(a) is quoted. The last day of the two-month period is not calculated.",
        "No tribunal time limit is calculated.",
        "Experiment 08 does not redact names, email addresses, or telephone numbers. This draft does not store the narrative. It is not anonymised.",
        "A narrative over 20,000 characters is not scanned.",
        "An instruction phrase that is not on the list is not detected.",
        "Experiment 11 is the Employment Rights Act 2025 harassment-duty checklist. It is not called. This draft does not decide reasonable steps.",
    ]
    if oversized:
        notes.append("This narrative was over the cap and was not classified.")
    if sources_stale:
        notes.append(
            "The pinned sources are older than the stale window. They were still quoted. "
            "Confirmation of a stale draft requires the HR officer to acknowledge that."
        )
    return notes


def _force(draft: dict) -> None:
    draft["narrative_stored"] = False
    draft["classification"]["decided"] = False
    draft["routing"]["confirmed"] = False
    draft["routing"]["queue_priority_changed"] = False
    draft["routing"]["handed_off"] = False
    draft["urgency"]["person_labelled_vulnerable"] = False
    draft["urgency"]["queue_priority_changed"] = False
    draft["urgency"]["certified_safe"] = False
    draft["special_category"]["article_9_condition_asserted"] = False
    draft["special_category"]["schedule_1_paragraph_1_met"] = None
    draft["special_category"]["appropriate_policy_document_checked"] = False
    draft["whistleblowing_confidentiality"]["identity_in_routing_summary"] = False
    draft["whistleblowing_confidentiality"]["narrative_in_routing_summary"] = False
    draft["whistleblowing_confidentiality"]["section_43j_applied_as_a_finding"] = False
    draft["whistleblowing_confidentiality"]["protected_disclosure_decided"] = False
    draft["whistleblowing_confidentiality"]["agent_contacted_anyone"] = False
    draft["automated_decision"]["solely_automated_decision"] = False
    draft["automated_decision"]["significant_decision"] = False
    draft["prompt_injection"]["followed"] = False
    draft["pii_gateway"]["output_is_anonymised"] = False
    draft["pii_gateway"]["agent_may_release"] = False
    draft["pii_gateway"]["redacted_text_stored"] = False
    draft["vulnerability_scanner"]["redacted_text_stored"] = False
    draft["vulnerability_scanner"]["injection_followed"] = False
    draft["vulnerability_scanner"]["person_labelled_vulnerable"] = False
    draft["outcome"] = None
    draft["merits_advice"] = None
    draft["contacted_employee"] = False
    draft["contacted_manager"] = False
    draft["hr_system_written"] = False
    draft["external_sent"] = False
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    for key, value in (
        ("outcome_decided", False),
        ("merits_advised", False),
        ("employee_contacted", False),
        ("manager_contacted", False),
        ("hr_system_written", False),
        ("external_sent", False),
        ("classification_confirmed_by_narrative", False),
        ("routing_confirmed_by_narrative", False),
        ("article_9_condition_asserted", False),
        ("protected_disclosure_decided", False),
        ("harassment_decided", False),
    ):
        draft["flags"][key] = value
    if draft["hr_confirmation"]["decision"] is None:
        draft["hr_confirmation"]["classification_confirmed"] = False
        draft["hr_confirmation"]["routing_confirmed"] = False
    if draft["document_intake"] is not None:
        draft["document_intake"]["files_confirmed"] = False
        draft["document_intake"]["purpose_confirmed"] = False
        draft["document_intake"]["injection_followed"] = False
        draft["document_intake"]["gateway_output_is_anonymised"] = False


def _require_draft(draft: dict) -> dict:
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not an employee-case intake result")
    if draft.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("draft is not an employee-case intake result")
    return deepcopy(draft)


def record_hr_confirmation(
    draft: dict,
    *,
    role: str,
    decision: str,
    confirmed_category: str | None = None,
    confirmed_route: str | None = None,
    acknowledge_stale: bool = False,
) -> dict:
    """Record an HR officer's confirmation. Does not write an HR system.

    The agent must not call this. The skills say so. A matching role still
    does not decide an outcome, contact anyone, or write a record.
    """

    if role != HR_ROLE:
        raise ValueError("only an HR officer can confirm classification and routing")
    if decision not in DECISIONS:
        raise ValueError(
            "decision must be confirm_classification_and_routing or return_for_edit"
        )
    updated = _require_draft(draft)
    if updated["sources_stale"] and decision == CONFIRM and acknowledge_stale is not True:
        raise ValueError(
            "sources are stale; the HR officer must acknowledge that before confirmation"
        )
    if decision == RETURN:
        updated["hr_confirmation"]["decision"] = RETURN
        updated["hr_confirmation"]["classification_confirmed"] = False
        updated["hr_confirmation"]["routing_confirmed"] = False
        _force(updated)
        updated["hr_confirmation"]["decision"] = RETURN
        return updated

    category = confirmed_category or updated["classification"]["proposed_category"]
    if category not in CATEGORY_IDS and category != "unresolved":
        raise ValueError("confirmed_category is not in the closed list")
    route = confirmed_route or updated["routing"]["proposed_route"]
    if route not in ROUTES:
        raise ValueError("confirmed_route is not in the closed list")
    updated["hr_confirmation"]["decision"] = CONFIRM
    updated["hr_confirmation"]["classification_confirmed"] = True
    updated["hr_confirmation"]["routing_confirmed"] = True
    updated["hr_confirmation"]["category_recorded"] = category
    updated["hr_confirmation"]["route_recorded"] = route
    updated["hr_confirmation"]["stale_acknowledged"] = bool(acknowledge_stale)
    _force(updated)
    updated["hr_confirmation"]["decision"] = CONFIRM
    updated["hr_confirmation"]["classification_confirmed"] = True
    updated["hr_confirmation"]["routing_confirmed"] = True
    updated["hr_confirmation"]["category_recorded"] = category
    updated["hr_confirmation"]["route_recorded"] = route
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft an HR case intake. Does not decide, contact, or write."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    args = parser.parse_args(argv)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    try:
        result = draft_case(
            payload,
            as_of=date.fromisoformat(args.as_of),
            stale_after_days=args.stale_after_days,
        )
    except NotSynthetic as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
