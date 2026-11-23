"""Prepare a control test. Do not pass or fail the control.

The named tester approves the exact working-paper hash before a copy is
written to the synthetic staging store. The tester decides the result.
The agent does not pass or fail a control, close a finding, or send.
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
    from cues import carve_out, category_hit, distress_hit, hits
    from dates import as_date, parse_date
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from reuse import NeighbourMissing, identifier_counts, intake_evidence, policy_mapping
    from sample import rationale, sample_size, select
    from sources import uk_context
else:
    from .cues import carve_out, category_hit, distress_hit, hits
    from .dates import as_date, parse_date
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .reuse import NeighbourMissing, identifier_counts, intake_evidence, policy_mapping
    from .sample import rationale, sample_size, select
    from .sources import uk_context

LABEL = "CONTROL TEST DRAFT FOR THE NAMED TESTER"
CATALOGUE_ID = "L009"
EXPERIMENT_ID = "exp-73-control-testing-assistant"
ROOT = Path(__file__).resolve().parents[1]
_STORE: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "approved",
    "approval",
    "control_passed",
    "control_failed",
    "finding_closed",
    "sent",
    "role",
    "clearance",
    "marked_acceptable",
    "staged",
    "result",
    "sample_size",
)
_DATE_FIELDS = ("prepared_on", "approved_on", "event_on", "original_approved_on")
_TEXT_CODES = {
    "self_approval": "self_approval",
    "back_dated": "back_dated",
    "out_of_period": "out_of_period",
    "altered": "altered",
    "missing_evidence": "missing_evidence",
    "embedded_instruction": "embedded_instruction",
    "approval_marker": "approval_marker_in_text",
    "biased_criteria": "biased_criteria",
    "sod_breach": "sod_breach",
    "carve_out": "carve_out",
}


class TestingForbidden(RuntimeError):
    """The agent does not pass, fail, close, or send."""

    __test__ = False


class NotSynthetic(ValueError):
    """The record is not marked synthetic."""


def pass_control(*_args, **_kwargs) -> None:
    raise TestingForbidden("The agent does not pass a control.")


def fail_control(*_args, **_kwargs) -> None:
    raise TestingForbidden("The agent does not fail a control.")


def close_finding(*_args, **_kwargs) -> None:
    raise TestingForbidden("The agent does not close a finding.")


def send(*_args, **_kwargs) -> None:
    raise TestingForbidden("The agent does not send.")


def write_production(*_args, **_kwargs) -> None:
    raise TestingForbidden("The agent does not write a production record.")


def reset_staging() -> None:
    _STORE.clear()


def _load_json(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    return {
        "library": _load_json("library.json"),
        "population": _load_json("population.json"),
        "directory": _load_json("directory.json"),
        "criteria": _load_json("criteria.json"),
    }


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


def _controls(library: dict) -> list[dict]:
    rows = library.get("controls") if isinstance(library, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _control(library: dict, control_id: object) -> dict | None:
    if not isinstance(control_id, str) or not control_id:
        return None
    for row in _controls(library):
        if row.get("control_id") == control_id:
            return row
    return None


def _items(population: dict, control_id: str) -> list[dict]:
    rows = population.get("items") if isinstance(population, dict) else None
    if not isinstance(rows, list):
        return []
    found = []
    for row in rows:
        if isinstance(row, dict) and row.get("control_id") == control_id:
            found.append(row)
    return found


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in _PROHIBITED:
        if key in working:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


def _force(result: dict) -> None:
    result["control_passed"] = None
    result["control_failed"] = None
    result["finding_closed"] = False
    result["marked_acceptable"] = False
    result["sent"] = False
    result["production_written"] = False
    result["coerced"] = False
    result["instructions_followed"] = False
    result["described_as_anonymised"] = False
    result["criteria_applied"] = False
    result["caller_library_applied"] = False
    result["caller_population_applied"] = False
    result["caller_directory_applied"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["body_copied"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False


def _projection(result: dict) -> dict:
    paper = result.get("working_paper") or {}
    plan = result.get("plan") or {}
    return {
        "engagement_id": result.get("engagement_id"),
        "control_id": result.get("control_id"),
        "tester_ref": result.get("tester_ref"),
        "as_of": result.get("as_of"),
        "period_start": (result.get("period") or {}).get("start"),
        "period_end": (result.get("period") or {}).get("end"),
        "outcome": result.get("outcome"),
        "sample_evidence_ids": list(plan.get("sample_evidence_ids") or []),
        "exception_refs": list(paper.get("exception_refs") or []),
        "exceptions": [
            {
                "evidence_id": row.get("evidence_id"),
                "code": row.get("code"),
                "step_id": row.get("step_id"),
                "field": row.get("field"),
                "source": row.get("source"),
            }
            for row in result.get("exceptions") or []
        ],
        "library_id": plan.get("library_id"),
        "detail_withheld": result.get("detail_withheld"),
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _library_diff(caller: object, pinned: dict) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": "caller_library_not_object", "applied": False}]
    diffs = []
    caller_rows = {row.get("control_id"): row for row in _controls(caller)}
    pinned_rows = {row.get("control_id"): row for row in _controls(pinned)}
    for control_id in sorted(set(caller_rows) | set(pinned_rows), key=lambda item: str(item)):
        if control_id not in pinned_rows:
            diffs.append({"control_id": control_id, "kind": "not_in_pinned", "applied": False})
            continue
        if control_id not in caller_rows:
            diffs.append({"control_id": control_id, "kind": "missing_from_caller", "applied": False})
            continue
        for field in ("objective", "frequency", "owner_ref", "minimum_sample", "required_fields", "policy_clause"):
            if caller_rows[control_id].get(field) != pinned_rows[control_id].get(field):
                diffs.append(
                    {
                        "control_id": control_id,
                        "kind": "field_differs",
                        "field": field,
                        "applied": False,
                    }
                )
    return diffs


def _population_diff(caller: object, pinned: dict) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": "caller_population_not_object", "applied": False}]
    diffs = []
    caller_rows = {
        row.get("evidence_id"): row
        for row in caller.get("items") or []
        if isinstance(row, dict)
    }
    pinned_rows = {
        row.get("evidence_id"): row
        for row in pinned.get("items") or []
        if isinstance(row, dict)
    }
    fields = ("control_id", "preparer_ref", "approver_ref", "prepared_on", "approved_on", "content_hash", "recorded_hash")
    for evidence_id in sorted(set(caller_rows) | set(pinned_rows), key=lambda item: str(item)):
        if evidence_id not in pinned_rows:
            diffs.append({"evidence_id": evidence_id, "kind": "not_in_pinned", "applied": False})
        elif evidence_id not in caller_rows:
            diffs.append({"evidence_id": evidence_id, "kind": "missing_from_caller", "applied": False})
        else:
            for field in fields:
                if caller_rows[evidence_id].get(field) != pinned_rows[evidence_id].get(field):
                    diffs.append(
                        {
                            "evidence_id": evidence_id,
                            "kind": "field_differs",
                            "field": field,
                            "applied": False,
                        }
                    )
    return diffs


def _id_diff(caller: object, pinned: dict, id_field: str, kind: str) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": f"caller_{kind}_not_object", "applied": False}]
    caller_ids = {
        row.get(id_field)
        for row in caller.get("people") or caller.get("controls") or []
        if isinstance(row, dict)
    }
    if kind == "directory":
        caller_ids = {row.get("employee_ref") for row in _people(caller)}
        pinned_ids = {row.get("employee_ref") for row in _people(pinned)}
    else:
        pinned_ids = caller_ids
    if caller != pinned:
        return [{"kind": "differs_from_pinned", "applied": False}]
    return []


def _review(document: dict, on: date) -> dict:
    parsed = parse_date(document.get("review_due") if isinstance(document, dict) else None)
    if parsed["unparseable"] or parsed["ambiguous"]:
        return {"review_due": None, "stale": None, "unreadable": True, "coerced": False}
    day = as_date(parsed)
    return {
        "review_due": day.isoformat() if day else None,
        "stale": bool(day and day <= on),
        "unreadable": False,
        "coerced": False,
    }


def _blank(as_of: str, outcome: str) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "as_of": as_of,
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "may_be_relied_on": False,
        "sources_current": False,
        "detail_withheld": False,
        "engagement_id": None,
        "control_id": None,
        "tester_ref": None,
        "period": {"start": None, "end": None, "unparseable": True, "ambiguous": False},
        "plan": {},
        "checks": [],
        "exceptions": [],
        "working_paper": {"result": None, "tester_decides_the_result": True, "exception_refs": []},
        "prompt_injection": {"followed": False, "signals": []},
        "distress": {"routed": False, "cue_copied": False},
        "marking": {"applied": None, "from_metadata": [], "from_content": []},
        "legal_hold": False,
        "retention": [],
        "uk_context": uk_context(),
        "required_acknowledgements": ["pins_seen"],
    }
    _force(result)
    result["content_hash"] = _hash(result)
    return result


def _exception(evidence_id: object, code: str, step_id: str | None, source: str, field: str | None = None) -> dict:
    return {
        "evidence_id": evidence_id if isinstance(evidence_id, str) else None,
        "code": code,
        "step_id": step_id,
        "field": field,
        "source": source,
    }


def _check_item(item: dict, control: dict, period: tuple[date | None, date | None], directory: dict, roles: list[str] | None) -> list[dict]:
    evidence_id = item.get("evidence_id")
    found: list[dict] = []
    required = control.get("required_fields")
    if not isinstance(required, list):
        found.append(_exception(evidence_id, "required_fields_unreadable", "S1", "structured"))
        required = []
    for field in required:
        if not isinstance(field, str):
            found.append(_exception(evidence_id, "required_fields_unreadable", "S1", "structured"))
            continue
        value = item.get(field)
        if value is None or value == "":
            found.append(_exception(evidence_id, "missing_field", "S1", "structured", field))
    parsed: dict[str, dict] = {}
    start, end = period
    for field in _DATE_FIELDS:
        if field not in item and field not in required:
            continue
        if field not in item:
            continue
        reading = parse_date(item.get(field))
        parsed[field] = reading
        if reading["ambiguous"]:
            found.append(_exception(evidence_id, "ambiguous_date", "S2", "structured", field))
        elif reading["unparseable"]:
            found.append(_exception(evidence_id, "unparseable_date", "S2", "structured", field))
        elif start is not None and end is not None and field != "original_approved_on":
            day = as_date(reading)
            if day is not None and (day < start or day > end):
                found.append(_exception(evidence_id, "out_of_period", "S2", "structured", field))
    prepared = as_date(parsed.get("prepared_on") or {})
    approved = as_date(parsed.get("approved_on") or {})
    original = as_date(parsed.get("original_approved_on") or {})
    if prepared is not None and approved is not None and approved < prepared:
        found.append(_exception(evidence_id, "back_dated", "S7", "structured", "approved_on"))
    if original is not None and approved is not None and approved < original:
        found.append(_exception(evidence_id, "back_dated", "S7", "structured", "original_approved_on"))
    if "altered" in item and type(item.get("altered")) is not bool:
        found.append(_exception(evidence_id, "altered_flag_unreadable", "S8", "structured", "altered"))
    elif item.get("altered") is True:
        found.append(_exception(evidence_id, "altered", "S8", "structured", "altered"))
    content_hash = item.get("content_hash")
    recorded_hash = item.get("recorded_hash")
    if isinstance(content_hash, str) and isinstance(recorded_hash, str) and content_hash != recorded_hash:
        found.append(_exception(evidence_id, "altered", "S8", "structured", "content_hash"))
    approver_ref = item.get("approver_ref")
    preparer_ref = item.get("preparer_ref")
    if isinstance(approver_ref, str) and approver_ref:
        approver = _person(directory, approver_ref)
        if approver is None:
            found.append(_exception(evidence_id, "approver_not_in_directory", "S3", "structured", "approver_ref"))
        else:
            if roles is None:
                found.append(_exception(evidence_id, "approver_role_unreadable", "S4", "structured"))
            elif approver.get("guest") is True or approver.get("role") not in roles:
                found.append(_exception(evidence_id, "approver_role", "S4", "structured", "approver_ref"))
            if isinstance(preparer_ref, str) and approver_ref == preparer_ref:
                found.append(_exception(evidence_id, "self_approval", "S5", "structured", "approver_ref"))
            elif approver.get("reports_to") == preparer_ref:
                found.append(_exception(evidence_id, "sod_breach", "S6", "structured", "approver_ref"))
    text = item.get("text") if isinstance(item.get("text"), str) else ""
    codes_present = {row["code"] for row in found}
    for name in hits(text):
        if name == "distress":
            continue
        code = _TEXT_CODES[name]
        if code in codes_present and code in {"self_approval", "back_dated", "out_of_period", "altered", "sod_breach"}:
            continue
        found.append(_exception(evidence_id, code, None, "text"))
        codes_present.add(code)
    if category_hit(text, "approval_marker"):
        pass
    return found


def _people_count(exceptions: list[dict], items: list[dict], threshold: object) -> dict:
    refs: set[str] = set()
    flagged = {row.get("evidence_id") for row in exceptions}
    for item in items:
        if item.get("evidence_id") not in flagged:
            continue
        for field in ("preparer_ref", "approver_ref"):
            value = item.get(field)
            if isinstance(value, str) and value:
                refs.add(value)
    unreadable = type(threshold) is not int or threshold < 2
    suppressed = unreadable or len(refs) < (threshold if not unreadable else 5)
    return {
        "published": None if suppressed else len(refs),
        "suppressed": suppressed,
        "threshold": None if unreadable else threshold,
        "threshold_unreadable": unreadable,
        "names_published": False,
        "identifies_a_person": False,
        "coerced": False,
    }


def _intake_files(items: list[dict]) -> list[dict]:
    files = []
    for item in sorted(items, key=lambda row: str(row.get("evidence_id"))):
        evidence_id = item.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            continue
        text = item.get("text") if isinstance(item.get("text"), str) else ""
        document_date = item.get("prepared_on")
        reading = parse_date(document_date)
        files.append(
            {
                "file_id": evidence_id,
                "filename": f"{evidence_id}.txt",
                "media_type": "text/plain",
                "document_date": reading["iso"] or "",
                "content": text,
            }
        )
    return files


def prepare_test(
    request: dict,
    library: dict | None = None,
    population: dict | None = None,
    directory: dict | None = None,
    criteria: dict | None = None,
    as_of: str = "",
) -> dict:
    """Return a draft working paper. human_approval stays null. Nothing is staged."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    question = parse_date(as_of)
    if question["unparseable"] or question["ambiguous"]:
        result = _blank(as_of if isinstance(as_of, str) else "", "unreadable_date")
        result["date_reading"] = {"reason": question["reason"], "coerced": False}
        result["content_hash"] = _hash(result)
        return result
    on = as_date(question)
    assert on is not None
    pinned = pinned_sources()
    working, ignored_keys = _strip(request)
    caller_library = library if library is not None else working.get("supplied_library")
    caller_population = population if population is not None else working.get("supplied_population")
    caller_directory = directory if directory is not None else working.get("supplied_directory")
    caller_criteria = criteria if criteria is not None else working.get("supplied_criteria")
    library_diff = _library_diff(caller_library, pinned["library"])
    population_diff = _population_diff(caller_population, pinned["population"])
    directory_diff = [] if caller_directory is None or caller_directory == pinned["directory"] else [
        {"kind": "differs_from_pinned", "applied": False}
    ]
    criteria_diff = [] if caller_criteria is None or caller_criteria == pinned["criteria"] else [
        {"kind": "differs_from_pinned", "applied": False}
    ]
    control_id = working.get("control_id")
    control = _control(pinned["library"], control_id)
    engagement_id = working.get("engagement_id") if isinstance(working.get("engagement_id"), str) else None
    tester_ref = working.get("tester_ref") if isinstance(working.get("tester_ref"), str) else None
    if control is None:
        result = _blank(on.isoformat(), "control_not_in_library")
        result["engagement_id"] = engagement_id
        result["control_id"] = control_id if isinstance(control_id, str) else None
        result["tester_ref"] = tester_ref
        result["ignored_request_keys"] = ignored_keys
        result["library_diff"] = library_diff
        result["content_hash"] = _hash(result)
        return result

    start_reading = parse_date(working.get("period_start"))
    end_reading = parse_date(working.get("period_end"))
    period_unreadable = start_reading["unparseable"] or end_reading["unparseable"]
    period_ambiguous = start_reading["ambiguous"] or end_reading["ambiguous"]
    start = as_date(start_reading)
    end = as_date(end_reading)
    period_order_bad = bool(start and end and start > end)
    period_pair = (start, end) if not period_unreadable and not period_ambiguous and not period_order_bad else (None, None)

    items = _items(pinned["population"], control["control_id"])
    roles = pinned["criteria"].get("approval_roles")
    if not isinstance(roles, list) or not roles or not all(isinstance(role, str) for role in roles):
        roles = None
    reading = sample_size(len(items), control.get("minimum_sample"))
    seed = working.get("sample_seed")
    chosen = select([str(item.get("evidence_id")) for item in items if isinstance(item.get("evidence_id"), str)], seed, reading["size"])
    sample_ids = set(chosen["ids"])
    exceptions: list[dict] = []
    checks = []
    if not items:
        exceptions.append(_exception(None, "missing_evidence", "S1", "structured"))
    for item in items:
        rows = _check_item(item, control, period_pair, pinned["directory"], roles)
        evidence_id = item.get("evidence_id") if isinstance(item.get("evidence_id"), str) else None
        exceptions.extend(rows)
        checks.append(
            {
                "evidence_id": evidence_id,
                "in_sample": evidence_id in sample_ids,
                "exception_codes": [row["code"] for row in rows],
                "step_met": None,
            }
        )
    cover = working.get("cover_note") if isinstance(working.get("cover_note"), str) else ""
    texts = [cover]
    meta_labels: list[str] = []
    content_labels: list[str] = []
    retention: list[str] = []
    held = False
    hold_unparseable = False
    retention_unparseable = False
    for source in (working, control):
        labels, _bad = metadata_markings(source.get("marking") if isinstance(source, dict) else None)
        for label in labels:
            if label not in meta_labels:
                meta_labels.append(label)
        kept, bad_ret = retention_labels(source.get("retention") if isinstance(source, dict) else None, "")
        retention_unparseable = retention_unparseable or bad_ret
        for label in kept:
            if label not in retention:
                retention.append(label)
        source_held, bad_hold = legal_hold(source.get("legal_hold") if isinstance(source, dict) else None, "")
        hold_unparseable = hold_unparseable or bad_hold
        held = held or source_held
    for item in items:
        text = item.get("text") if isinstance(item.get("text"), str) else ""
        texts.append(text)
        labels, _bad = metadata_markings(item.get("marking"))
        for label in labels:
            if label not in meta_labels:
                meta_labels.append(label)
        for label in content_markings(text):
            if label not in content_labels:
                content_labels.append(label)
        kept, bad_ret = retention_labels(item.get("retention"), text)
        retention_unparseable = retention_unparseable or bad_ret
        for label in kept:
            if label not in retention:
                retention.append(label)
        item_held, bad_hold = legal_hold(item.get("legal_hold"), text)
        hold_unparseable = hold_unparseable or bad_hold
        held = held or item_held
    for label in content_markings(cover):
        if label not in content_labels:
            content_labels.append(label)
    applied = higher_marking(meta_labels + content_labels)
    tester = _person(pinned["directory"], tester_ref)
    ceiling = tester.get("clearance") if tester else None
    guest = bool(tester and tester.get("guest") is True)
    withheld = guest or tester is None or above_ceiling(applied, ceiling if isinstance(ceiling, str) else None)
    distress = distress_hit(cover) or any(
        distress_hit(item.get("text") if isinstance(item.get("text"), str) else "") for item in items
    )
    criteria_blob = json.dumps(caller_criteria) if caller_criteria is not None else ""
    library_blob = json.dumps(caller_library) if caller_library is not None else ""
    biased = (
        category_hit(criteria_blob, "biased_criteria")
        or category_hit(library_blob, "biased_criteria")
        or category_hit(cover, "biased_criteria")
    )
    if biased:
        exceptions.append(_exception(None, "biased_criteria", None, "caller"))
    signals = []
    for name in hits("\n".join(texts)):
        signals.append({"code": name, "followed": False})
    if carve_out("\n".join(texts)) and not any(row["code"] == "carve_out" for row in signals):
        signals.append({"code": "carve_out", "followed": False})
    library_review = _review(pinned["library"], on)
    directory_review = _review(pinned["directory"], on)
    stale = library_review["stale"] is True or directory_review["stale"] is True
    date_problem = any(row["code"] in {"unparseable_date", "ambiguous_date"} for row in exceptions) or period_unreadable or period_ambiguous or period_order_bad
    acknowledgements = ["pins_seen"]
    if library_diff or population_diff or directory_diff or criteria_diff:
        acknowledgements.append("sources_seen")
    if stale or library_review["unreadable"] or directory_review["unreadable"]:
        acknowledgements.append("stale_seen")
    if date_problem:
        acknowledgements.append("dates_seen")
    if biased:
        acknowledgements.append("criteria_seen")
    if withheld:
        outcome = "withheld"
    elif distress:
        outcome = "route_to_human"
    elif period_unreadable or period_ambiguous or period_order_bad or reading["unreadable_minimum"] or chosen["unreadable_seed"]:
        outcome = "needs_human"
    else:
        outcome = "draft"
    visible_exceptions = [] if withheld else exceptions
    visible_checks = [] if withheld else checks
    visible_sample = [] if withheld else list(chosen["ids"])
    exception_refs = []
    for row in visible_exceptions:
        if row["evidence_id"] and row["evidence_id"] not in exception_refs:
            exception_refs.append(row["evidence_id"])
    mask_counts = {"phone": 0, "email": 0, "date_of_birth": 0, "postal_address": 0, "personal_name": 0}
    for text in texts:
        _masked, report = mask_text(text)
        for kind, count in report["counts"].items():
            mask_counts[kind] += count
    joined = "\n".join(texts)[:8000]
    try:
        identifiers = identifier_counts(joined, on=on)
    except NeighbourMissing:
        identifiers = {"called": False, "reason": "neighbour_missing", "output_is_anonymised": False, "values_stored": False}
    try:
        intake = intake_evidence(_intake_files(items), on=on)
    except (NeighbourMissing, ValueError, TypeError):
        intake = {
            "called": False,
            "reason": "intake_not_used",
            "files_confirmed": False,
            "purpose_confirmed": False,
        }
    try:
        mapping = policy_mapping(control.get("policy_clause"), on=on.isoformat())
    except NeighbourMissing:
        mapping = {
            "called": False,
            "reason": "neighbour_missing",
            "is_a_test_result": False,
            "control_met_by_mapping": False,
        }
    threshold = pinned["criteria"].get("small_number_threshold")
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "engagement_id": engagement_id,
        "control_id": control["control_id"],
        "tester_ref": tester_ref,
        "tester_on_directory": bool(tester and tester.get("role") == pinned["criteria"].get("tester_role") and not guest),
        "as_of": on.isoformat(),
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "may_be_relied_on": False,
        "sources_current": not stale and not library_review["unreadable"] and not directory_review["unreadable"],
        "detail_withheld": withheld,
        "withheld_reason": "guest" if guest else ("clearance" if withheld else None),
        "period": {
            "start": start.isoformat() if start and not period_ambiguous and not period_unreadable else None,
            "end": end.isoformat() if end and not period_ambiguous and not period_unreadable else None,
            "unparseable": period_unreadable,
            "ambiguous": period_ambiguous,
            "order_invalid": period_order_bad,
            "coerced": False,
        },
        "plan": {
            "library_id": pinned["library"].get("library_id"),
            "objective": control.get("objective"),
            "frequency": control.get("frequency"),
            "owner_ref": control.get("owner_ref"),
            "test_steps": control.get("test_steps"),
            "method": "seeded_systematic",
            "seed": chosen.get("seed"),
            "population_size": len(items),
            "sample_size": None if withheld else reading.get("size"),
            "size_rationale": rationale(len(items), reading, chosen),
            "sample_evidence_ids": visible_sample,
            "minimum_unreadable": reading["unreadable_minimum"],
            "seed_unreadable": chosen["unreadable_seed"],
        },
        "checks": visible_checks,
        "exceptions": visible_exceptions,
        "working_paper": {
            "title": "Draft working paper for the named tester",
            "control_id": control["control_id"],
            "period_start": start.isoformat() if period_pair[0] else None,
            "period_end": end.isoformat() if period_pair[1] else None,
            "sample_evidence_ids": visible_sample,
            "exception_refs": exception_refs,
            "tester_decides_the_result": True,
            "result": None,
        },
        "people_count": _people_count(visible_exceptions, items, threshold),
        "library_diff": library_diff,
        "population_diff": population_diff,
        "directory_diff": directory_diff,
        "criteria_diff": criteria_diff,
        "biased_criteria": biased,
        "ignored_request_keys": ignored_keys,
        "library_review": library_review,
        "directory_review": directory_review,
        "prompt_injection": {"followed": False, "signals": signals},
        "distress": {"routed": distress, "cue_copied": False},
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
        "masking": {
            "counts": mask_counts,
            "values_stored": False,
            "values_copied": False,
            "body_copied": False,
            "described_as_anonymised": False,
            "output_contains_masked_placeholders": False,
        },
        "uk_identifiers": identifiers,
        "intake": intake,
        "mapping": mapping,
        "uk_context": uk_context(),
        "required_acknowledgements": acknowledgements,
        "step_met": None,
    }
    _force(result)
    result["content_hash"] = _hash(result)
    return result


def _named_tester(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_sources()["directory"]
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("tester_ref"):
        return None, "not_the_named_tester"
    person = _person(pinned, approver_ref)
    if person is None or person.get("guest") is True or person.get("role") != "tester":
        return None, "approver_not_directory_tester"
    return person, None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named tester has seen a human route. Nothing is staged."""

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
    _person_row, reason = _named_tester(result, directory, approval.get("approver_ref"))
    if reason:
        updated["blocked_reason"] = reason
        updated["content_hash"] = _hash(updated)
        return updated
    updated["route_seen"] = True
    updated["distress"] = {"routed": True, "cue_copied": False, "seen": True}
    updated["content_hash"] = _hash(updated)
    return updated


def record_tester_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Stage the draft only when the named tester approves this content hash."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        return updated
    if approval.get("decision") in {"pass", "fail"} or "control_passed" in approval or "control_failed" in approval:
        updated["blocked_reason"] = "tester_result_is_not_this_step"
        return updated
    if approval.get("item") != "working-paper" or approval.get("decision") != "approve-draft":
        updated["blocked_reason"] = "wrong_item"
        return updated
    if result.get("outcome") == "withheld" or result.get("detail_withheld") is True:
        updated["blocked_reason"] = "withheld"
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        return updated
    if approval.get("content_hash") != result.get("content_hash") or approval.get("content_hash") != _hash(result):
        updated["blocked_reason"] = "content_hash_mismatch"
        return updated
    if approval.get("engagement_id") != result.get("engagement_id"):
        updated["blocked_reason"] = "engagement_mismatch"
        return updated
    reason = _ack(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        return updated
    person, role_reason = _named_tester(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        return updated
    updated["human_approval"] = {
        "item": "working-paper",
        "approver_ref": person["employee_ref"],
        "content_hash": result["content_hash"],
        "recorded": True,
        "decides_the_result": False,
    }
    updated["staged"] = True
    updated["route_seen"] = result.get("route_seen") is True
    _force(updated)
    row = {
        "engagement_id": result.get("engagement_id"),
        "content_hash": result["content_hash"],
        "control_id": result.get("control_id"),
        "tester_ref": person["employee_ref"],
        "working_paper": deepcopy(result.get("working_paper")),
        "exceptions": deepcopy(result.get("exceptions")),
        "marking": deepcopy(result.get("marking")),
        "legal_hold": result.get("legal_hold"),
        "retention": list(result.get("retention") or []),
        "control_passed": None,
        "control_failed": None,
        "finding_closed": False,
        "sent": False,
        "production_written": False,
        "store": "synthetic",
    }
    _STORE[f"{result.get('engagement_id')}:{result['content_hash']}"] = row
    updated["staging_store"] = "synthetic"
    updated["content_hash"] = result["content_hash"]
    return updated


def record_tester_result(result: dict, directory: dict, approval: dict) -> dict:
    """Store the tester's own words. Do not read them as a pass, a fail, or a closure."""

    updated = deepcopy(result)
    _force(updated)
    updated["staged"] = False
    updated["agent_interpreted_result"] = False
    updated["tester_words"] = None
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        return updated
    if approval.get("item") != "tester-result":
        updated["blocked_reason"] = "wrong_item"
        return updated
    words = approval.get("words")
    if not isinstance(words, str) or not words.strip():
        updated["blocked_reason"] = "words_unreadable"
        return updated
    if len(words) > 2000:
        updated["blocked_reason"] = "words_too_long"
        return updated
    current = _hash(result)
    if approval.get("content_hash") != result.get("content_hash") or approval.get("content_hash") != current:
        updated["blocked_reason"] = "content_hash_mismatch"
        return updated
    person, role_reason = _named_tester(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        return updated
    key = f"{result.get('engagement_id')}:{result.get('content_hash')}"
    row = _STORE.get(key)
    if not isinstance(row, dict):
        updated["blocked_reason"] = "not_staged"
        return updated
    row["tester_words"] = words
    row["agent_interpreted_result"] = False
    row["control_passed"] = None
    row["control_failed"] = None
    row["finding_closed"] = False
    row["legal_hold"] = result.get("legal_hold")
    row["retention"] = list(result.get("retention") or [])
    updated["staged"] = True
    updated["human_approval"] = result.get("human_approval")
    updated["tester_words"] = words
    updated["agent_interpreted_result"] = False
    updated["staging_store"] = "synthetic"
    _force(updated)
    updated["content_hash"] = result["content_hash"]
    return updated


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a synthetic control test draft.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = prepare_test(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
