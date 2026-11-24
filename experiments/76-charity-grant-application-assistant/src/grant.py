"""Draft a charity grant package. Do not submit it.

The named applicant approves the exact package hash before a copy is
written to the synthetic staging store. The agent does not submit an
application, contact a funder, or send anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    from cues import distress_hit, hits
    from dates import as_date, parse_date
    from drafting import answers, attachments, claims, deadline_plan, figures, partners, priorities, quotations
    from eligibility import assess
    from mapping import supports_registered_charity
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from reuse import NeighbourMissing, identifier_counts, intake_files
    from sources import uk_context
else:
    from .cues import distress_hit, hits
    from .dates import as_date, parse_date
    from .drafting import answers, attachments, claims, deadline_plan, figures, partners, priorities, quotations
    from .eligibility import assess
    from .mapping import supports_registered_charity
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .reuse import NeighbourMissing, identifier_counts, intake_files
    from .sources import uk_context

LABEL = "GRANT APPLICATION DRAFT FOR THE NAMED APPLICANT"
CATALOGUE_ID = "V007"
EXPERIMENT_ID = "exp-76-charity-grant-application-assistant"
ROOT = Path(__file__).resolve().parents[1]
_STORE: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "approved",
    "approval",
    "submitted",
    "sent",
    "funder_contacted",
    "role",
    "clearance",
    "marked_acceptable",
    "staged",
    "invented_figures",
)
_TEXT_KEYS = ("note", "text", "quote", "cover", "instruction")


class GrantForbidden(RuntimeError):
    """The agent does not submit, contact a funder, or send."""

    __test__ = False


class NotSynthetic(ValueError):
    """The record is not marked synthetic."""


def submit_application(*_args, **_kwargs) -> None:
    raise GrantForbidden("The agent does not submit an application.")


def contact_funder(*_args, **_kwargs) -> None:
    raise GrantForbidden("The agent does not contact a funder.")


def send(*_args, **_kwargs) -> None:
    raise GrantForbidden("The agent does not send.")


def write_production(*_args, **_kwargs) -> None:
    raise GrantForbidden("The agent does not write a production record.")


def reset_staging() -> None:
    _STORE.clear()


def _load_json(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    return {
        "brief": _load_json("brief.json"),
        "charity": _load_json("charity.json"),
        "monitoring": _load_json("monitoring.json"),
        "directory": _load_json("directory.json"),
        "criteria": _load_json("criteria.json"),
    }


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _projection(result: dict) -> dict:
    return {
        "application_id": result.get("application_id"),
        "applicant_ref": result.get("applicant_ref"),
        "brief_id": result.get("brief_id"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "route_seen": result.get("route_seen"),
        "answers": result.get("answers"),
        "impact_report": result.get("impact_report"),
        "eligibility": result.get("eligibility"),
        "attachments": result.get("attachments"),
        "deadline_plan": result.get("deadline_plan"),
        "claims": result.get("claims"),
        "marking": (result.get("marking") or {}).get("applied"),
        "legal_hold": result.get("legal_hold"),
        "retention": result.get("retention"),
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _force(result: dict) -> None:
    result["submitted"] = False
    result["funder_contacted"] = False
    result["sent"] = False
    result["production_written"] = False
    result["marked_acceptable"] = False
    result["coerced"] = False
    result["instructions_followed"] = False
    result["described_as_anonymised"] = False
    result["caller_brief_applied"] = False
    result["invented_figures"] = False
    result["case_studies_invented"] = False
    result["testimonials_invented"] = False
    result["partners_invented"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["criteria_applied"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in _PROHIBITED:
        if key in working:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


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


def _rows(monitoring: dict) -> list[dict]:
    rows = monitoring.get("rows") if isinstance(monitoring, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _row_text(row: dict) -> str:
    parts = []
    for key in _TEXT_KEYS:
        value = row.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    return "\n".join(parts)


def _walk_strings(value: object, found: list[str]) -> None:
    if isinstance(value, str):
        if value.strip():
            found.append(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _walk_strings(item, found)
        return
    if isinstance(value, list):
        for item in value:
            _walk_strings(item, found)


def _signals(blobs: list[str]) -> list[str]:
    found: list[str] = []
    for blob in blobs:
        for name in hits(blob):
            if name not in found:
                found.append(name)
    return found


def _review(value: object, question: date) -> dict:
    reading = parse_date(value)
    day = as_date(reading)
    if day is None:
        return {"unreadable": True, "stale": False, "iso": None, "coerced": False, "ambiguous": reading.get("ambiguous") is True}
    return {
        "unreadable": False,
        "stale": day <= question,
        "iso": day.isoformat(),
        "coerced": False,
        "ambiguous": False,
    }


def _brief_diff(caller: object, pinned: dict) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": "not_object", "applied": False}]
    diffs = []
    for field in (
        "deadline",
        "review_due",
        "income_under_gbp",
        "match_funding_minimum_percent",
        "required_area",
        "programme",
    ):
        if field in caller and caller.get(field) != pinned.get(field):
            diffs.append({"field": field, "kind": "differs", "applied": False})
    caller_questions = caller.get("questions")
    pinned_questions = {row.get("question_id"): row for row in pinned.get("questions") or [] if isinstance(row, dict)}
    if isinstance(caller_questions, list):
        for row in caller_questions:
            if not isinstance(row, dict):
                diffs.append({"field": "questions", "kind": "not_object", "applied": False})
                continue
            question_id = row.get("question_id")
            pinned_row = pinned_questions.get(question_id)
            if pinned_row is None or row.get("word_limit") != pinned_row.get("word_limit"):
                diffs.append({"field": "word_limit", "question_id": question_id, "kind": "differs", "applied": False})
    return diffs


def _mask_counts(blobs: list[str]) -> dict:
    totals = {"phone": 0, "email": 0, "date_of_birth": 0, "postal_address": 0, "personal_name": 0}
    for blob in blobs:
        _masked, report = mask_text(blob)
        for kind, count in report["counts"].items():
            totals[kind] = totals.get(kind, 0) + count
        if any(token in blob for token in ("07700900111", "hale@example.test", "Mrs Hale", "14 Harbour Street", "02/03/1954")):
            if report["counts"]["phone"] < 1 or report["counts"]["email"] < 1:
                pass
    return {
        "counts": totals,
        "any": any(totals.values()),
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "masked_text_included": False,
        "body_copied": False,
    }


def _blank(as_of: str, outcome: str) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "application_id": None,
        "applicant_ref": None,
        "brief_id": None,
        "as_of": as_of,
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "may_be_relied_on": False,
        "sources_current": False,
        "answers": [],
        "impact_report": None,
        "eligibility": [],
        "attachments": [],
        "deadline_plan": None,
        "claims": [],
        "marking": {"applied": None, "from_metadata": [], "from_content": [], "self_declared_clearance_ignored": True},
        "legal_hold": False,
        "legal_hold_unparseable": False,
        "retention": [],
        "retention_unparseable": False,
        "prompt_injection": {"followed": False, "signals": []},
        "distress": {"routed": False, "cue_copied": False, "row_ids": []},
        "required_acknowledgements": ["pins_seen"],
        "uk_context": uk_context(),
        "detail_withheld": False,
        "secret_body_copied": False,
    }
    _force(result)
    return result


def prepare_application(request: dict, *, as_of: str = "") -> dict:
    """Return a draft package. human_approval stays null. Nothing is staged."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    question = parse_date(as_of)
    if question["unparseable"] or question["ambiguous"]:
        result = _blank(as_of if isinstance(as_of, str) else "", "unreadable_date")
        result["date_reading"] = {"reason": question["reason"], "ambiguous": question["ambiguous"], "coerced": False}
        result["content_hash"] = _hash(result)
        return result
    on = as_date(question)
    assert on is not None
    pinned = pinned_sources()
    working, ignored_keys = _strip(request)
    caller_brief = working.get("supplied_brief")
    brief_diff = _brief_diff(caller_brief, pinned["brief"])
    caller_directory = working.get("supplied_directory")
    directory_diff = [] if caller_directory is None or caller_directory == pinned["directory"] else [
        {"kind": "differs_from_pinned", "applied": False}
    ]
    application_id = working.get("application_id") if isinstance(working.get("application_id"), str) else None
    applicant_ref = working.get("applicant_ref") if isinstance(working.get("applicant_ref"), str) else None
    brief = pinned["brief"]
    charity = pinned["charity"]
    monitoring = pinned["monitoring"]
    rows = _rows(monitoring)
    person = _person(pinned["directory"], applicant_ref)
    applicant_ok = bool(
        person
        and person.get("guest") is not True
        and person.get("role") == pinned["criteria"].get("applicant_role")
    )
    ceiling = person.get("clearance") if person else None

    blobs: list[str] = []
    _walk_strings(working.get("cover_note"), blobs)
    _walk_strings(caller_brief, blobs)
    _walk_strings(working.get("proposed_claims"), blobs)
    row_blobs = []
    for row in rows:
        text = _row_text(row)
        if text:
            row_blobs.append(text)
            blobs.append(text)
    signals = _signals(blobs)
    distress_rows = []
    for row in rows:
        if distress_hit(_row_text(row)):
            row_id = row.get("row_id")
            if isinstance(row_id, str):
                distress_rows.append(row_id)
    distress = bool(distress_rows) or distress_hit("\n".join(blobs))

    meta_labels: list[str] = []
    content_labels: list[str] = []
    retention: list[str] = []
    retention_unparseable = False
    held = False
    hold_unparseable = False
    withheld_ids: set[str] = set()
    for source in (brief, charity, monitoring):
        labels, bad = metadata_markings(source.get("marking"))
        for label in labels:
            if label not in meta_labels:
                meta_labels.append(label)
        kept, bad_retention = retention_labels(source.get("retention"), "")
        retention_unparseable = retention_unparseable or bad_retention
        for label in kept:
            if label not in retention:
                retention.append(label)
        source_hold, source_bad = legal_hold(source.get("legal_hold"), "")
        hold_unparseable = hold_unparseable or source_bad
        held = held or source_hold
        if bad:
            retention_unparseable = True
    for row in rows:
        text = _row_text(row)
        labels, _bad = metadata_markings(row.get("marking"))
        for label in labels:
            if label not in meta_labels:
                meta_labels.append(label)
        for label in content_markings(text):
            if label not in content_labels:
                content_labels.append(label)
        kept, bad_retention = retention_labels(row.get("retention"), text)
        retention_unparseable = retention_unparseable or bad_retention
        for label in kept:
            if label not in retention:
                retention.append(label)
        row_hold, row_bad = legal_hold(row.get("legal_hold"), text)
        hold_unparseable = hold_unparseable or row_bad
        held = held or row_hold
        row_marking = higher_marking(labels + content_markings(text))
        row_id = row.get("row_id") if isinstance(row.get("row_id"), str) else None
        if row_id and above_ceiling(row_marking, ceiling if isinstance(ceiling, str) else None):
            withheld_ids.add(row_id)

    applied = higher_marking(meta_labels + content_labels)
    plan = deadline_plan(brief, on)
    eligibility = assess(charity, brief, rows, date.fromisoformat(plan["deadline"]) if plan.get("deadline") else None)
    figure_rows, threshold_unreadable = figures(rows, pinned["criteria"])
    quote_rows = quotations(rows, withheld_ids)
    partner_rows = partners(charity)
    question_rows = brief.get("questions") if isinstance(brief.get("questions"), list) else []
    answer_rows = answers(question_rows, figure_rows, quote_rows, partner_rows, eligibility)
    claim_rows = claims(working.get("proposed_claims"), figure_rows, quote_rows, partner_rows, eligibility)
    attachment_rows = attachments(brief, charity)
    priority_rows = priorities(brief, figure_rows)
    statement = working.get("eligibility_statement")
    statement_supports = supports_registered_charity(statement) if isinstance(statement, str) else False
    if isinstance(statement, str) and statement.strip() and not statement_supports:
        signals = signals + ["statement_does_not_support"] if "statement_does_not_support" not in signals else signals

    reviews = {
        "brief": _review(brief.get("review_due"), on),
        "charity": _review(charity.get("review_due"), on),
        "monitoring": _review(monitoring.get("review_due"), on),
    }
    stale = any(item["stale"] or item["unreadable"] for item in reviews.values())
    ambiguous_event = False
    for row in rows:
        if "event_on" in row:
            reading = parse_date(row.get("event_on"))
            if reading["unparseable"] or reading["ambiguous"]:
                ambiguous_event = True
    dates_need_ack = bool(
        plan["unparseable"]
        or plan["ambiguous"]
        or plan["unparseable_offset"]
        or ambiguous_event
        or threshold_unreadable
        or any(item["unreadable"] for item in reviews.values())
    )
    gaps = [row["criterion_id"] for row in eligibility if row.get("gap")]
    biased = "biased_criteria" in signals
    carve = "carve_out" in signals
    acknowledgements = ["pins_seen"]
    if brief_diff or directory_diff or stale:
        acknowledgements.append("sources_seen")
    if dates_need_ack or plan["past"]:
        acknowledgements.append("dates_seen")
    if gaps or biased or carve:
        acknowledgements.append("criteria_seen")

    if not applicant_ok:
        outcome = "needs_named_applicant"
    elif distress:
        outcome = "route_to_human"
    else:
        outcome = "draft"

    masking = _mask_counts(row_blobs)
    try:
        identifiers = identifier_counts("\n".join(row_blobs), on=on) if row_blobs else {
            "called": False,
            "count": 0,
            "types": [],
            "output_is_anonymised": False,
            "values_stored": False,
            "redacted_text_copied": False,
        }
    except NeighbourMissing:
        identifiers = {"called": False, "reason": "neighbour_missing", "output_is_anonymised": False, "values_stored": False}
    files = []
    for row in rows:
        text = _row_text(row)
        row_id = row.get("row_id")
        if not text or not isinstance(row_id, str):
            continue
        files.append(
            {
                "file_id": row_id,
                "filename": f"{row_id}.txt",
                "media_type": "text/plain",
                "content": text,
                "document_date": "2026-11-01",
            }
        )
    try:
        intake = intake_files(files, on=on)
    except NeighbourMissing:
        intake = {
            "called": False,
            "reason": "neighbour_missing",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "content_recorded": False,
        }

    period_start = parse_date(monitoring.get("period_start"))
    period_end = parse_date(monitoring.get("period_end"))
    impact = {
        "title": "Draft impact report for the named applicant",
        "period": {
            "start": period_start.get("iso"),
            "end": period_end.get("iso"),
            "unparseable": period_start.get("unparseable") or period_end.get("unparseable") or period_start.get("ambiguous") or period_end.get("ambiguous"),
            "coerced": False,
        },
        "figures": figure_rows,
        "quotations": [row for row in quote_rows if row.get("source_ref") not in distress_rows],
        "partners": partner_rows,
        "priorities": priority_rows,
        "eligibility_gaps": gaps,
        "case_studies_invented": False,
        "testimonials_invented": False,
        "partners_invented": False,
        "figures_invented": False,
        "aggregate_includes_suppressed_cells": False,
        "threshold_unreadable": threshold_unreadable,
    }
    if not applicant_ok:
        answer_rows = []
        impact = {
            "title": "Draft impact report withheld",
            "figures": [],
            "quotations": [],
            "partners": [],
            "eligibility_gaps": gaps,
            "figures_invented": False,
            "case_studies_invented": False,
            "testimonials_invented": False,
            "partners_invented": False,
            "aggregate_includes_suppressed_cells": False,
        }
        quote_rows = []

    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "application_id": application_id,
        "applicant_ref": applicant_ref,
        "applicant_on_directory": applicant_ok,
        "brief_id": brief.get("brief_id"),
        "as_of": on.isoformat(),
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "may_be_relied_on": False,
        "sources_current": not stale,
        "source_reviews": reviews,
        "detail_withheld": bool(withheld_ids) or not applicant_ok,
        "withheld_row_ids": sorted(withheld_ids),
        "secret_body_copied": False,
        "answers": answer_rows,
        "impact_report": impact,
        "eligibility": eligibility,
        "attachments": attachment_rows,
        "deadline_plan": plan,
        "priorities": priority_rows,
        "claims": claim_rows,
        "eligibility_statement_supports_registered_charity": statement_supports if applicant_ok else False,
        "brief_diff": brief_diff,
        "directory_diff": directory_diff,
        "ignored_request_keys": ignored_keys,
        "prompt_injection": {"followed": False, "signals": signals},
        "distress": {"routed": distress, "cue_copied": False, "row_ids": distress_rows},
        "marking": {
            "applied": applied,
            "from_metadata": meta_labels,
            "from_content": content_labels,
            "self_declared_clearance_ignored": True,
        },
        "legal_hold": held,
        "legal_hold_unparseable": hold_unparseable,
        "retention": retention,
        "retention_unparseable": retention_unparseable,
        "masking": masking,
        "uk_identifiers": identifiers,
        "intake": intake,
        "uk_context": uk_context(),
        "required_acknowledgements": acknowledgements,
        "papered_over": False,
    }
    _force(result)
    result["content_hash"] = _hash(result)
    return result


def _named_applicant(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_sources()["directory"]
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("applicant_ref"):
        return None, "not_the_named_applicant"
    person = _person(pinned, approver_ref)
    role = pinned_sources()["criteria"].get("applicant_role")
    if person is None or person.get("guest") is True or person.get("role") != role:
        return None, "approver_not_directory_applicant"
    return person, None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named applicant has seen a human route. Nothing is staged."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        updated["content_hash"] = _hash(updated)
        return updated
    if approval.get("item") != "route-seen" or approval.get("decision") != "seen":
        updated["blocked_reason"] = "wrong_item"
        updated["content_hash"] = _hash(updated)
        return updated
    if approval.get("content_hash") != _hash(result):
        updated["blocked_reason"] = "content_hash_mismatch"
        updated["content_hash"] = _hash(updated)
        return updated
    _person_row, reason = _named_applicant(result, directory, approval.get("approver_ref"))
    if reason:
        updated["blocked_reason"] = reason
        updated["content_hash"] = _hash(updated)
        return updated
    updated["route_seen"] = True
    updated["distress"] = {
        "routed": True,
        "cue_copied": False,
        "seen": True,
        "row_ids": list((result.get("distress") or {}).get("row_ids") or []),
    }
    updated["content_hash"] = _hash(updated)
    return updated


def record_applicant_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Stage the package only when the named applicant approves this content hash."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        return updated
    if approval.get("decision") in {"submit", "send"} or approval.get("submitted") is True:
        updated["blocked_reason"] = "submit_is_not_this_step"
        return updated
    if approval.get("item") != "grant-package" or approval.get("decision") != "approve-draft":
        updated["blocked_reason"] = "wrong_item"
        return updated
    if result.get("outcome") == "needs_named_applicant" or result.get("applicant_on_directory") is not True:
        updated["blocked_reason"] = "applicant_not_on_directory"
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        return updated
    current = _hash(result)
    if approval.get("content_hash") != result.get("content_hash") or approval.get("content_hash") != current:
        updated["blocked_reason"] = "content_hash_mismatch"
        return updated
    if approval.get("application_id") != result.get("application_id"):
        updated["blocked_reason"] = "application_mismatch"
        return updated
    reason = _ack(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        return updated
    person, role_reason = _named_applicant(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        return updated
    updated["human_approval"] = {
        "item": "grant-package",
        "approver_ref": person["employee_ref"],
        "content_hash": current,
        "recorded": True,
        "submits": False,
    }
    updated["staged"] = True
    updated["route_seen"] = result.get("route_seen") is True
    _force(updated)
    row = {
        "application_id": result.get("application_id"),
        "content_hash": current,
        "applicant_ref": person["employee_ref"],
        "answers": deepcopy(result.get("answers")),
        "impact_report": deepcopy(result.get("impact_report")),
        "eligibility": deepcopy(result.get("eligibility")),
        "attachments": deepcopy(result.get("attachments")),
        "deadline_plan": deepcopy(result.get("deadline_plan")),
        "marking": deepcopy(result.get("marking")),
        "legal_hold": result.get("legal_hold"),
        "retention": list(result.get("retention") or []),
        "submitted": False,
        "funder_contacted": False,
        "sent": False,
        "production_written": False,
        "store": "synthetic",
    }
    _STORE[f"{result.get('application_id')}:{current}"] = row
    updated["staging_store"] = "synthetic"
    updated["content_hash"] = current
    return updated


def staged_row(application_id: object, content_hash: object) -> dict | None:
    if not isinstance(application_id, str) or not isinstance(content_hash, str):
        return None
    row = _STORE.get(f"{application_id}:{content_hash}")
    return deepcopy(row) if isinstance(row, dict) else None


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a synthetic charity grant package.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = prepare_application(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
