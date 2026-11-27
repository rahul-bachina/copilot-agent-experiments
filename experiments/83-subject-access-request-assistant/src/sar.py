"""Scope a synthetic subject access request. Do not disclose it.

The named information governance officer approves every redaction, every
exemption candidate, and the disclosure bundle. The approval is bound to the
agent-held copy and its hash. The agent does not send a response, delete or
edit a record, or decide an exemption.

Autonomy is A1. Instructions, approval markers, and a directory inside the
request are not authoritative.
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
    from cues import (
        authority_claim,
        carve_out_affirmed,
        category_hit,
        role_claim,
        sensitive_categories,
    )
    from dates import as_date, parse_date, with_question_date
    from deadline import illustrate, read_structured_date
    from exemptions import phrase_hits, third_party_candidate
    from foi import classify as classify_foi
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from negate import affirmed
    from redact import propose as propose_redactions
    from siblings import intake_summary
    from sources import uk_context
else:
    from .cues import (
        authority_claim,
        carve_out_affirmed,
        category_hit,
        role_claim,
        sensitive_categories,
    )
    from .dates import as_date, parse_date, with_question_date
    from .deadline import illustrate, read_structured_date
    from .exemptions import phrase_hits, third_party_candidate
    from .foi import classify as classify_foi
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .negate import affirmed
    from .redact import propose as propose_redactions
    from .siblings import intake_summary
    from .sources import uk_context

LABEL = (
    "DRAFT SUBJECT ACCESS SCOPING FOR THE NAMED INFORMATION GOVERNANCE OFFICER. "
    "THE AGENT DOES NOT SEND A RESPONSE, DELETE OR EDIT A RECORD, OR DECIDE AN EXEMPTION."
)
CATALOGUE_ID = "UK11"
EXPERIMENT_ID = "exp-83-subject-access-request-assistant"
ROOT = Path(__file__).resolve().parents[1]
CASE_ID = re.compile(r"^SAR-\d{4}$")
DOC_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
CHANNELS = frozenset({"letter", "email", "web_form", "foi"})
# A starter rule for an export that is too old to treat as the current file. Not a statutory period.
STALE_AFTER_DAYS = 30
COMPLEX = (
    "complex request",
    "this request is complex",
    "several requests",
    "a number of requests",
    "request for erasure",
    "request erasure",
    "data portability",
)
SYSTEM_PHRASES = {
    "email": ("email", "emails", "mailbox"),
    "casework": ("case note", "case file", "casework"),
    "hr": ("personnel file", "hr file", "human resources"),
    "finance": ("invoice", "payment record", "finance system"),
    "housing": ("tenancy", "housing file"),
    "health": ("medical record", "health record"),
}
BROAD = ("all information you hold", "all personal data", "everything you hold", "all data you hold")
_DOB_IN_TEXT = re.compile(
    r"\b(?:date of birth|d\.?o\.?b\.?|born on)\b[:\s-]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.IGNORECASE,
)
_SENT_ON = re.compile(r"\bsent this on\s+(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})", re.IGNORECASE)
_HELD: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "disclosure_approved",
    "approved",
    "response_sent",
    "records_deleted",
    "records_edited",
    "exemption_applied",
    "exemption_decided",
    "role",
    "clearance",
    "route_seen",
)


class SarForbidden(RuntimeError):
    """The agent does not send, delete, edit, or decide an exemption."""

    __test__ = False


class NotSynthetic(ValueError):
    """The request was not marked synthetic."""


def send_response(*_args, **_kwargs) -> None:
    raise SarForbidden("The agent does not send a response to the requester.")


def delete_record(*_args, **_kwargs) -> None:
    raise SarForbidden("The agent does not delete a record.")


def edit_record(*_args, **_kwargs) -> None:
    raise SarForbidden("The agent does not edit a record.")


def decide_exemption(*_args, **_kwargs) -> None:
    raise SarForbidden("The agent does not decide an exemption.")


def reset_held() -> None:
    _HELD.clear()


def held_record(case_id: object) -> dict | None:
    if not isinstance(case_id, str):
        return None
    row = _HELD.get(case_id)
    if not isinstance(row, dict):
        return None
    return {"case_id": case_id, "content_hash": row.get("content_hash")}


def pinned_directory() -> dict:
    return json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))


def pinned_systems() -> list[str]:
    raw = json.loads((ROOT / "fixtures" / "systems.json").read_text(encoding="utf-8"))
    rows = raw.get("systems") if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        return []
    return [item for item in rows if isinstance(item, str)]


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _question_date(value: object) -> date:
    if isinstance(value, date):
        reading = parse_date(value.isoformat())
    elif isinstance(value, str):
        reading = parse_date(value)
    else:
        raise ValueError("as_of must be a calendar date.")
    parsed = as_date(reading)
    if parsed is None or reading.get("ambiguous") or reading.get("unparseable"):
        raise ValueError("as_of must be an unambiguous calendar date.")
    return parsed


def _people(directory: dict) -> list[dict]:
    rows = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str) or not ref:
        return None
    for row in _people(directory):
        if row.get("employee_ref") == ref:
            return row
    return None


def _officers(directory: dict) -> list[str]:
    refs = []
    for row in _people(directory):
        if row.get("active") is True and row.get("role") == "information_governance_officer":
            if isinstance(row.get("employee_ref"), str):
                refs.append(row["employee_ref"])
    return refs


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in _PROHIBITED:
        if key in working:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


def _requester(raw: object) -> dict:
    if not isinstance(raw, dict):
        return {}
    kept = {}
    for key in ("name", "email", "date_of_birth", "address", "postcode", "staff_id", "reference", "phone", "nino"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            kept[key] = value.strip()
    return kept


def _matches(document: dict, requester: dict) -> bool:
    reference = requester.get("reference") or ""
    name = requester.get("name") or ""
    email = requester.get("email") or ""
    about = document.get("about_ref")
    if isinstance(about, str) and reference and about == reference:
        return True
    abouts = document.get("about_refs")
    if isinstance(abouts, list) and reference and reference in abouts:
        return True
    text = document.get("content") if isinstance(document.get("content"), str) else ""
    if reference and reference in text:
        return True
    if email and email.casefold() in text.casefold():
        return True
    if name and len(name.split()) >= 2 and name.casefold() in text.casefold():
        return True
    return False


def _directory_diff(caller: object, pinned: dict) -> dict:
    if not isinstance(caller, dict):
        return {"present": False, "differs": False, "applied": False}
    caller_refs = {row.get("employee_ref"): row for row in _people(caller)}
    pinned_refs = {row.get("employee_ref"): row for row in _people(pinned)}
    differs = caller_refs.keys() != pinned_refs.keys()
    for ref, row in caller_refs.items():
        pinned_row = pinned_refs.get(ref)
        if not isinstance(pinned_row, dict):
            differs = True
            continue
        for field in ("role", "clearance", "active"):
            if row.get(field) != pinned_row.get(field):
                differs = True
    return {"present": True, "differs": differs, "applied": False}


def _schedule_diff(caller: object) -> dict:
    present = caller is not None
    return {"present": present, "applied": False, "authoritative": False}


def _systems_named(text: str, allowed: list[str]) -> list[str]:
    named = []
    for system, phrases in SYSTEM_PHRASES.items():
        if system not in allowed:
            continue
        if any(affirmed(text, phrase) for phrase in phrases):
            named.append(system)
    return named


def _extension_candidate(text: str) -> bool:
    return any(affirmed(text, phrase) for phrase in COMPLEX)


def _dob_conflict(text: str, requester: dict) -> bool:
    profile = requester.get("date_of_birth")
    if not isinstance(profile, str):
        return False
    profile_day = as_date(parse_date(profile))
    if profile_day is None:
        return False
    for match in _DOB_IN_TEXT.finditer(text or ""):
        found = as_date(parse_date(match.group(1)))
        if found is not None and found != profile_day:
            return True
    return False


def _stated_sent(text: str, received_iso: str | None) -> bool:
    if not received_iso:
        return False
    match = _SENT_ON.search(text or "")
    if not match:
        return False
    found = as_date(parse_date(match.group(1)))
    return found is not None and found.isoformat() != received_iso


def _suppression(distinct: int) -> dict:
    small = 0 < distinct < 5
    published = None if small else distinct
    return {
        "applied": small,
        "threshold": 5,
        "threshold_is_starter_rule": True,
        "published_count": published,
        "published_difference": None,
        "published_percentage": None,
        "headcount": published,
        "n": published,
        "percentage": None,
        "difference": None,
        "people_affected": published,
        "described_as_anonymised": False,
    }


def _force(result: dict) -> None:
    result["response_sent"] = False
    result["records_deleted"] = False
    result["records_edited"] = False
    result["exemption_decided_by_agent"] = False
    result["deadline_decided"] = False
    result["search_reasonable_decided"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["caller_directory_applied"] = False
    result["caller_schedule_applied"] = False
    result["described_as_anonymised"] = False
    result["may_be_relied_on"] = False
    result["production_written"] = False
    result["request_logged_in_production"] = False
    result["experiment_01_called"] = False
    result["coerced"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
    deadline = result.get("deadline")
    if isinstance(deadline, dict):
        deadline["deadline_decided"] = False
        deadline["extension_applied"] = False
        deadline["extension_notice_sent"] = False
        deadline["pause_applied_as_a_decision"] = False
        deadline["fee_decided_by_agent"] = False
    for row in result.get("exemptions") or []:
        if isinstance(row, dict):
            row["applied"] = False
            row["decided_by_agent"] = False
    for row in result.get("redactions") or []:
        if isinstance(row, dict):
            row["applied_by_agent"] = False


def _projection(result: dict) -> dict:
    return {
        "case_id": result.get("case_id"),
        "requester_ref": result.get("requester_ref"),
        "officer_ref": result.get("officer_ref"),
        "channel": result.get("channel"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "route_seen": result.get("route_seen") is True,
        "deadline": result.get("deadline"),
        "search_scope": result.get("search_scope"),
        "foi": result.get("foi"),
        "document_ids": result.get("document_ids"),
        "copies": result.get("copies"),
        "redactions": result.get("redactions"),
        "exemptions": result.get("exemptions"),
        "identity_verification_needed": result.get("identity_verification_needed") is True,
        "third_party_authority_needed": result.get("third_party_authority_needed") is True,
        "sensitive": result.get("sensitive"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold") is True,
        "legal_hold_unparseable": result.get("legal_hold_unparseable") is True,
        "retention": result.get("retention"),
        "prompt_injection": result.get("prompt_injection"),
        "suppression": result.get("suppression"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "conflicts": result.get("conflicts"),
        "carve_out": result.get("carve_out") is True,
        "leading_criterion": result.get("leading_criterion") is True,
        "caller_directory_differs": (result.get("caller_directory") or {}).get("differs") is True,
        "caller_schedule_present": (result.get("caller_schedule") or {}).get("present") is True,
        "records_export": result.get("records_export"),
        "disclosure_approval_recorded": result.get("disclosure_approval_recorded") is True,
        "redaction_decisions": result.get("redaction_decisions"),
        "exemption_decisions": result.get("exemption_decisions"),
        "response_sent": False,
        "records_deleted": False,
        "records_edited": False,
        "exemption_decided_by_agent": False,
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _store(result: dict) -> None:
    case_id = result.get("case_id")
    if not isinstance(case_id, str):
        return
    projected = deepcopy(_projection(result))
    result["content_hash"] = _digest(projected)
    _HELD[case_id] = {"content_hash": result["content_hash"], "projection": projected}


def _remember(result: dict) -> None:
    case_id = result.get("case_id")
    projected = deepcopy(_projection(result))
    result["content_hash"] = _digest(projected)
    if result.get("blocked_reason") or not isinstance(case_id, str):
        return
    _HELD[case_id] = {"content_hash": result["content_hash"], "projection": projected}


def scope(request: dict, *, as_of: str | date) -> dict:
    """Return a draft scope. Nothing is sent, deleted, edited, or decided."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("request is not marked synthetic")
    question = _question_date(as_of)
    working, ignored = _strip(request)
    directory = pinned_directory()
    systems = pinned_systems()
    officers = _officers(directory)
    case_id = working.get("case_id")
    case_ok = isinstance(case_id, str) and CASE_ID.fullmatch(case_id) is not None
    channel = working.get("channel") if isinstance(working.get("channel"), str) else ""
    channel_known = channel in CHANNELS
    requester = _requester(working.get("requester"))
    officer_ref = working.get("officer_ref") if isinstance(working.get("officer_ref"), str) else ""
    officer = _person(directory, officer_ref)
    officer_ok = (
        officer is not None
        and officer.get("active") is True
        and officer.get("role") == "information_governance_officer"
    )
    ceiling = officer.get("clearance") if officer_ok else None
    text = working.get("text") if isinstance(working.get("text"), str) else ""
    records = working.get("records") if isinstance(working.get("records"), list) else []
    received = read_structured_date(working.get("received_on"), question)
    identity_date = read_structured_date(working.get("identity_information_received_on"), question)
    fee_date = read_structured_date(working.get("fee_paid_on"), question)
    asked = read_structured_date(working.get("clarification_requested_on"), question)
    got = read_structured_date(working.get("clarification_received_on"), question)
    regime = "law_enforcement" if (
        working.get("processing_regime") == "law_enforcement"
        or affirmed(text, "law enforcement processing")
        or affirmed(text, "part 3 of the data protection act")
    ) else "uk_gdpr"
    if working.get("processing_regime") not in (None, "uk_gdpr", "law_enforcement"):
        regime_flag = "unrecognised_regime"
    else:
        regime_flag = None
    if working.get("processing_regime") == "uk_gdpr" and regime == "law_enforcement":
        regime_flag = "caller_regime_did_not_drop_law_enforcement"

    made_by = working.get("made_by") if isinstance(working.get("made_by"), str) else ""
    authority = made_by in {"solicitor", "third_party"} or authority_claim(text)
    identity_needed = working.get("identity_evidence_supplied") is not True
    categories = sensitive_categories(text)
    injection_signals = [
        name for name in ("embedded_instruction", "forged_approval", "leading_criterion")
        if category_hit(text, name)
    ]
    leading = category_hit(text, "leading_criterion")
    carve = carve_out_affirmed(text)
    foi = classify_foi(text, channel if channel_known else "")
    extension = _extension_candidate(text)
    deadline = illustrate(
        received=received,
        identity=identity_date,
        fee=fee_date,
        clarification_asked=asked,
        clarification_received=got,
        regime=regime,
        extension_candidate=extension,
        question=question,
    )
    caller_directory = _directory_diff(working.get("directory") or working.get("staff_directory"), directory)
    caller_schedule = _schedule_diff(working.get("exemption_schedule") or working.get("exemptions"))
    conflicts = []
    if _stated_sent(text, received.get("iso")):
        conflicts.append({"kind": "stated_sent_date", "picked": False})
    if regime_flag:
        conflicts.append({"kind": regime_flag, "picked": False})

    copies = []
    redactions = []
    exemptions = []
    document_ids = []
    not_in_scope = []
    markings: list[str] = []
    marking_unparseable = False
    hold = False
    hold_unparseable = False
    retention: list[str] = []
    retention_unparseable = False
    intake_files = []
    unknown_systems = []
    malformed_amount = False
    called_08 = False
    document_dates = []
    for raw in records:
        if not isinstance(raw, dict):
            conflicts.append({"kind": "record_not_object", "picked": False})
            continue
        document_id = raw.get("document_id")
        if not isinstance(document_id, str) or not DOC_ID.fullmatch(document_id):
            conflicts.append({"kind": "document_id_unusable", "picked": False})
            continue
        content = raw.get("content") if isinstance(raw.get("content"), str) else ""
        system = raw.get("system") if isinstance(raw.get("system"), str) else ""
        if system and system not in systems:
            unknown_systems.append(system)
        if "document_date" in raw:
            reading = with_question_date(parse_date(raw.get("document_date")), question)
            document_dates.append({
                "document_id": document_id,
                "iso": reading.get("iso") if reading.get("unparseable") is not True and reading.get("ambiguous") is not True else None,
                "unparseable": reading.get("unparseable") is True,
                "ambiguous": reading.get("ambiguous") is True,
                "future": reading.get("future") is True,
                "coerced": False,
            })
            if reading.get("unparseable") is True or reading.get("ambiguous") is True:
                conflicts.append({"kind": "document_date_unusable", "document_id": document_id, "picked": False})
            elif reading.get("future") is True:
                conflicts.append({"kind": "document_date_future", "document_id": document_id, "picked": False})
        categories.extend(item for item in sensitive_categories(content) if item not in categories)
        for name in ("embedded_instruction", "forged_approval", "leading_criterion"):
            if category_hit(content, name) and name not in injection_signals:
                injection_signals.append(name)
        if category_hit(content, "leading_criterion"):
            leading = True
        if carve_out_affirmed(content):
            carve = True
        if authority_claim(content):
            authority = True
        meta_marks, meta_bad = metadata_markings(raw.get("protective_marking"))
        marking_unparseable = marking_unparseable or meta_bad
        labels = list(meta_marks)
        for label in content_markings(content):
            if label not in labels:
                labels.append(label)
        for label in labels:
            if label not in markings:
                markings.append(label)
        doc_hold, doc_hold_bad = legal_hold(raw.get("legal_hold"), content)
        hold = hold or doc_hold
        hold_unparseable = hold_unparseable or doc_hold_bad
        doc_retention, doc_ret_bad = retention_labels(raw.get("retention"), content)
        retention_unparseable = retention_unparseable or doc_ret_bad
        for label in doc_retention:
            if label not in retention:
                retention.append(label)
        if _dob_conflict(content, requester):
            conflicts.append({"kind": "date_of_birth", "document_id": document_id, "picked": False})
        in_scope = _matches(raw, requester) or foi.get("route") == "foi_not_own_data"
        if foi.get("route") == "foi_not_own_data":
            in_scope = False
        if not in_scope:
            not_in_scope.append(document_id)
            continue
        document_ids.append(document_id)
        proposal = propose_redactions(content, requester, on=question, document_id=document_id)
        called_08 = True
        malformed_amount = malformed_amount or proposal["malformed_amount"]
        redactions.extend(proposal["redactions"])
        for hit in phrase_hits(content):
            hit = dict(hit)
            hit["exemption_id"] = f"{document_id}-E{len(exemptions) + 1}"
            hit["document_id"] = document_id
            hit["reason"] = "An affirmed phrase for this exemption is in the document. The officer decides."
            exemptions.append(hit)
        withheld = above_ceiling(higher_marking(labels), ceiling if isinstance(ceiling, str) else None)
        copies.append({
            "document_id": document_id,
            "system": system if system in systems else None,
            "withheld": withheld,
            "masked_text": None if withheld else proposal["masked_text"],
            "values_stored": False,
        })
        if DOC_ID.fullmatch(document_id) and isinstance(raw.get("filename"), str):
            intake_files.append({
                "file_id": document_id,
                "filename": raw["filename"][:120],
                "media_type": "text/plain",
                "content": content,
                "document_date": raw.get("document_date") if isinstance(raw.get("document_date"), str) else None,
            })

    letter_hits = phrase_hits(text)
    if letter_hits:
        for hit in letter_hits:
            hit = dict(hit)
            hit["exemption_id"] = f"LETTER-E{len(exemptions) + 1}"
            hit["document_id"] = None
            hit["reason"] = "An affirmed phrase for this exemption is in the request. The officer decides."
            if not any(row["schedule"] == hit["schedule"] and row["paragraph"] == hit["paragraph"] and row["document_id"] is None for row in exemptions):
                exemptions.append(hit)
    if redactions and not any(row["paragraph"] == "16" for row in exemptions):
        row = third_party_candidate()
        row["exemption_id"] = "BUNDLE-E16"
        row["document_id"] = None
        exemptions.append(row)

    distinct_names = sum(1 for row in redactions if row["kind"] == "personal_name")
    if distinct_names == 0 and redactions:
        distinct_names = 1
    suppression = _suppression(distinct_names)
    applied_marking = higher_marking(markings)
    named_systems = _systems_named(text, systems)
    systems_with_hits = []
    for copy in copies:
        if copy.get("system") and copy["system"] not in systems_with_hits:
            systems_with_hits.append(copy["system"])
    broad = any(affirmed(text, phrase) for phrase in BROAD)
    scope_systems = []
    for system in systems:
        if system in named_systems or system in systems_with_hits or (broad and system in systems_with_hits):
            if system not in scope_systems:
                scope_systems.append(system)
    if broad:
        for system in systems_with_hits:
            if system not in scope_systems:
                scope_systems.append(system)
    for system in named_systems:
        if system not in scope_systems:
            scope_systems.append(system)
    search_scope = {
        "systems": scope_systems,
        "all_information_requested": broad,
        "unknown_systems_not_added": unknown_systems,
        "reasonable_and_proportionate_decided": False,
        "leading_criterion_applied": False,
        "reasoning": (
            "Article 15(1A) limits what must be provided to what a reasonable and proportionate "
            "search can produce. The systems listed are those named in the request or those that "
            "hold a matching document in this export. This is not a finding that the search is "
            "reasonable and proportionate."
        ),
    }
    if foi["route"] == "foi_not_own_data":
        search_scope["systems"] = []
        search_scope["reasoning"] = (
            "The text is an FOI request and does not ask for the applicant's own personal data. "
            "Section 40(1) is not applied. This agent does not answer an FOI request."
        )

    exported = read_structured_date(working.get("records_exported_on"), question)
    export_days = None
    exported_on = as_date(exported)
    if exported_on is not None and exported.get("future") is not True:
        export_days = (question - exported_on).days
    records_export = {
        "exported_on": exported.get("iso") if exported.get("usable") is True and exported.get("future") is not True else None,
        "age_days": export_days,
        "stale": export_days is not None and export_days > STALE_AFTER_DAYS,
        "stale_after_days": STALE_AFTER_DAYS,
        "starter_rule_not_a_statute": True,
        "unparseable": "records_exported_on" in working and exported.get("usable") is not True and exported.get("future") is not True,
        "future": exported.get("future") is True,
        "coerced": False,
        "document_dates": document_dates,
    }
    if records_export["unparseable"] or records_export["future"]:
        conflicts.append({"kind": "records_exported_on", "picked": False})

    route_reasons = list(categories)
    if hold:
        route_reasons.append("legal_hold")
    if applied_marking in {"SECRET", "TOP SECRET"}:
        route_reasons.append("high_marking")
    if foi["route"] in {"mixed", "foi_not_own_data"}:
        route_reasons.append(foi["route"])
    if authority:
        route_reasons.append("third_party_authority")
    if identity_needed:
        route_reasons.append("identity")
    if records_export["stale"] or records_export["unparseable"] or records_export["future"]:
        route_reasons.append("records_export")
    outcome = "route_to_human" if any(
        item in route_reasons
        for item in (
            "distress", "safeguarding", "whistleblowing", "complaint", "grievance",
            "litigation", "legal_hold", "high_marking", "mixed", "foi_not_own_data",
            "third_party_authority", "records_export",
        )
    ) else "draft_for_officer"

    acks = ["pins_seen", "dates_seen"]
    if identity_needed:
        acks.append("identity_seen")
    if authority:
        acks.append("authority_seen")
    if applied_marking or marking_unparseable:
        acks.append("markings_seen")
    if hold or hold_unparseable or retention or retention_unparseable:
        acks.append("holds_seen")
    if suppression["applied"]:
        acks.append("suppression_seen")
    if deadline["pause_is_illustrative"] or deadline["extension_candidate"]:
        acks.append("clarification_seen")
    if foi["route"] != "subject_access":
        acks.append("foi_seen")
    if exemptions:
        acks.append("exemptions_seen")
    if redactions:
        acks.append("redactions_seen")
    if caller_directory["present"] or caller_schedule["present"] or unknown_systems:
        acks.append("sources_seen")
    if conflicts or deadline["problems"]:
        acks.append("conflicts_seen")
    if carve:
        acks.append("carve_out_seen")
    if leading:
        acks.append("leading_seen")

    intake = intake_summary(
        [row for row in intake_files if isinstance(row.get("document_date"), str) or True],
        on=question,
    )
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "case_id": case_id if case_ok else None,
        "case_id_valid": case_ok,
        "channel": channel if channel_known else None,
        "channel_recognised": channel_known,
        "as_of": question.isoformat(),
        "officer_ref": officer_ref if officer_ok else None,
        "officer_refs": officers,
        "requester_ref": requester.get("reference"),
        "requester_values_copied_into_the_log": False,
        "outcome": outcome,
        "route_seen": False,
        "deadline": deadline,
        "search_scope": search_scope,
        "foi": foi,
        "document_ids": document_ids,
        "not_in_scope": not_in_scope,
        "copies": copies,
        "redactions": redactions,
        "exemptions": exemptions,
        "identity_verification_needed": identity_needed,
        "identity_in_text_trusted": False,
        "third_party_authority_needed": authority,
        "sensitive": {"categories": categories, "cue_copied": False},
        "marking": {
            "applied": applied_marking,
            "labels": markings,
            "unparseable": marking_unparseable,
            "ceiling": ceiling if isinstance(ceiling, str) else None,
            "self_declared_clearance_trusted": False,
        },
        "legal_hold": hold,
        "legal_hold_unparseable": hold_unparseable,
        "retention": retention,
        "retention_unparseable": retention_unparseable,
        "prompt_injection": {"signals": injection_signals, "followed": False},
        "suppression": suppression,
        "required_acknowledgements": acks,
        "conflicts": conflicts,
        "carve_out": carve,
        "leading_criterion": leading,
        "caller_directory": caller_directory,
        "caller_schedule": caller_schedule,
        "records_export": records_export,
        "malformed_amount": malformed_amount,
        "amount_coerced": False,
        "intake": intake,
        "experiment_08_called": called_08,
        "experiment_12_called": intake.get("called") is True,
        "experiment_01_called": False,
        "uk_context": {
            "opened_on": uk_context()["opened_on"],
            "not_legal_advice": True,
            "article_12a_quoted": True,
            "article_15_1a_quoted": True,
            "section_52_opened": False,
            "section_53_opened": False,
            "statutory_instrument_2026_82_opened": False,
            "public_holidays_applied": False,
        },
        "disclosure_approval_recorded": False,
        "redaction_decisions": None,
        "exemption_decisions": None,
        "human_approval": None,
        "blocked_reason": None,
        "ignored_request_keys": ignored,
        "role_in_text": role_claim(text),
        "logged": {
            "case_id": case_id if case_ok else None,
            "channel": channel if channel_known else None,
            "received_on": received.get("iso"),
            "question_date": question.isoformat(),
            "regime": regime,
            "production_written": False,
        },
    }
    _force(result)
    if case_ok:
        _store(result)
    else:
        result["content_hash"] = _hash(result)
        result["outcome"] = "route_to_human"
    return result


def _bound(result: dict, approval: dict) -> str | None:
    case_id = result.get("case_id")
    held = _HELD.get(case_id) if isinstance(case_id, str) else None
    if not isinstance(held, dict):
        return "no_agent_held_copy"
    current = _hash(result)
    if approval.get("content_hash") != held.get("content_hash"):
        return "caller_rehash_rejected"
    if result.get("content_hash") != held.get("content_hash") or current != held.get("content_hash"):
        return "content_tampered"
    if _projection(result) != held.get("projection"):
        return "content_tampered"
    return None


def _named_officer(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_directory()
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref not in set(result.get("officer_refs") or []):
        return None, "not_the_named_officer"
    person = _person(pinned, approver_ref)
    if person is None or person.get("active") is not True or person.get("role") != "information_governance_officer":
        return None, "approver_not_information_governance_officer"
    return person, None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def _decision_map(approval: dict, key: str, expected: list[str]) -> tuple[dict | None, str | None]:
    raw = approval.get(key)
    if not isinstance(raw, dict):
        return None, f"{key}_missing"
    if set(raw) != set(expected):
        return None, f"{key}_do_not_match_the_bundle"
    cleaned = {}
    for item_id in expected:
        choice = raw.get(item_id)
        if choice not in {"accept", "reject"}:
            return None, f"{key}_not_accept_or_reject"
        cleaned[item_id] = choice
    return cleaned, None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named officer has seen a human route. Nothing is sent."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        updated["route_seen"] = False
        _remember(updated)
        return updated
    if approval.get("item") != "route-seen" or approval.get("decision") != "seen":
        updated["blocked_reason"] = "wrong_item"
        updated["route_seen"] = False
        _remember(updated)
        return updated
    reason = _bound(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        updated["route_seen"] = False
        _remember(updated)
        return updated
    _person_row, role_reason = _named_officer(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        updated["route_seen"] = False
        _remember(updated)
        return updated
    if approval.get("case_id") != result.get("case_id"):
        updated["blocked_reason"] = "case_mismatch"
        updated["route_seen"] = False
        _remember(updated)
        return updated
    updated["route_seen"] = True
    updated["sensitive"] = {
        "categories": list((result.get("sensitive") or {}).get("categories") or []),
        "cue_copied": False,
        "seen": True,
    }
    updated["blocked_reason"] = None
    _force(updated)
    _remember(updated)
    return updated


def record_disclosure_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Record the officer's decisions. Do not send, delete, edit, or decide."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["disclosure_approval_recorded"] = False
    updated["redaction_decisions"] = None
    updated["exemption_decisions"] = None
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if approval.get("item") != "disclosure-approval" or approval.get("decision") != "approve_disclosure":
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    reason = _bound(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        _remember(updated)
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        _remember(updated)
        return updated
    if result.get("disclosure_approval_recorded") is True:
        updated["blocked_reason"] = "already_recorded"
        _remember(updated)
        return updated
    if approval.get("case_id") != result.get("case_id"):
        updated["blocked_reason"] = "case_mismatch"
        _remember(updated)
        return updated
    person, role_reason = _named_officer(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    ack_reason = _ack(result, approval)
    if ack_reason:
        updated["blocked_reason"] = ack_reason
        _remember(updated)
        return updated
    redaction_ids = [row["redaction_id"] for row in result.get("redactions") or [] if isinstance(row, dict)]
    exemption_ids = [row["exemption_id"] for row in result.get("exemptions") or [] if isinstance(row, dict)]
    redaction_decisions, redaction_reason = _decision_map(approval, "redaction_decisions", redaction_ids)
    if redaction_reason:
        updated["blocked_reason"] = redaction_reason
        _remember(updated)
        return updated
    exemption_decisions, exemption_reason = _decision_map(approval, "exemption_decisions", exemption_ids)
    if exemption_reason:
        updated["blocked_reason"] = exemption_reason
        _remember(updated)
        return updated
    if "records" in approval or "directory" in approval or "text" in approval:
        updated["blocked_reason"] = "caller_rehash_rejected"
        _remember(updated)
        return updated
    held = _HELD[result["case_id"]]
    updated["disclosure_approval_recorded"] = True
    updated["redaction_decisions"] = redaction_decisions
    updated["exemption_decisions"] = exemption_decisions
    updated["human_approval"] = {
        "item": "disclosure-approval",
        "approver_ref": person["employee_ref"],
        "content_hash": held["content_hash"],
        "recorded": True,
        "executes_disclosure": False,
        "bound_to_held_copy": True,
        "redaction_count": len(redaction_decisions or {}),
        "exemption_count": len(exemption_decisions or {}),
    }
    updated["blocked_reason"] = None
    updated["outcome"] = "disclosure_approval_recorded"
    _force(updated)
    _remember(updated)
    return updated


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scope a synthetic subject access request.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = scope(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
