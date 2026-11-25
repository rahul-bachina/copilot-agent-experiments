"""Extract a synthetic form into a draft record.

The named reviewer approves the exact record hash before a copy is written
to the synthetic staging store. The agent does not decide an application,
write to a production system, perform a call-back, or send anything.

The approved bytes are the copy held when the draft was built. A caller who
edits the package and hashes it again is refused.
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
    from cues import category_hit, hits, route_categories
    from dates import as_date
    from fields import extract_fields, withhold
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from reuse import identifier_counts, intake_files
    from sources import uk_context
else:
    from .cues import category_hit, hits, route_categories
    from .dates import as_date
    from .fields import extract_fields, withhold
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .reuse import identifier_counts, intake_files
    from .sources import uk_context

LABEL = "FORM EXTRACTION DRAFT FOR THE NAMED REVIEWER"
CATALOGUE_ID = "O002"
EXPERIMENT_ID = "exp-77-form-extraction-assistant"
ROOT = Path(__file__).resolve().parents[1]
_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
_HELD: dict[str, dict] = {}
_STORE: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "approved",
    "approval",
    "staged",
    "decided",
    "application_decided",
    "sent",
    "production_written",
    "verified",
    "call_back_performed",
    "callback_completed",
    "role",
    "clearance",
    "instructions_followed",
)
_FLAG_ACK = {
    "blank",
    "missing",
    "illegible",
    "contradictory_duplicate",
    "duplicated",
    "ticked_and_crossed",
    "unparseable",
    "ambiguous",
    "impossible",
    "out_of_range",
    "negated",
    "verification_claim_ignored",
    "future",
    "blank_box",
}


class FormForbidden(RuntimeError):
    """The agent does not decide, write production, call back, or send."""

    __test__ = False


class NotSynthetic(ValueError):
    """The record is not marked synthetic."""


def decide_application(*_args, **_kwargs) -> None:
    raise FormForbidden("The agent does not decide an application.")


def write_production(*_args, **_kwargs) -> None:
    raise FormForbidden("The agent does not write to a production system.")


def send(*_args, **_kwargs) -> None:
    raise FormForbidden("The agent does not send.")


def perform_callback(*_args, **_kwargs) -> None:
    raise FormForbidden("The agent does not perform a call-back check.")


def reset_staging() -> None:
    _HELD.clear()
    _STORE.clear()


def _load_json(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    return {"schemas": _load_json("schemas.json"), "directory": _load_json("directory.json")}


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _projection(result: dict) -> dict:
    return {
        "extraction_id": result.get("extraction_id"),
        "form_type": result.get("form_type"),
        "form_id": result.get("form_id"),
        "reviewer_ref": result.get("reviewer_ref"),
        "reviewer_on_directory": result.get("reviewer_on_directory"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "route_seen": result.get("route_seen"),
        "fields": result.get("fields"),
        "unexpected_fields": result.get("unexpected_fields"),
        "review_sheet": result.get("review_sheet"),
        "bank": result.get("bank"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "legal_hold_unparseable": result.get("legal_hold_unparseable"),
        "retention": result.get("retention"),
        "retention_unparseable": result.get("retention_unparseable"),
        "prompt_injection": result.get("prompt_injection"),
        "suppression": result.get("suppression"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "distress": result.get("distress"),
        "schema_check": result.get("schema_check"),
        "detail_withheld": result.get("detail_withheld"),
        "masking": result.get("masking"),
        "audit_log": result.get("audit_log"),
        "uk_identifiers": result.get("uk_identifiers"),
        "intake": result.get("intake"),
        "sources_current": result.get("sources_current"),
        "date_arithmetic": result.get("date_arithmetic"),
        "locks": result.get("locks"),
        "uk_context": result.get("uk_context"),
        "ignored_request_keys": result.get("ignored_request_keys"),
    }


def content_hash(result: dict) -> str:
    return _digest(_projection(result))


def _locks() -> dict:
    return {
        "instructions_followed": False,
        "approval_marker_trusted": False,
        "caller_schema_applied": False,
        "decided": False,
        "application_decided": False,
        "sent": False,
        "production_written": False,
        "call_back_performed": False,
        "signature_verified": False,
        "coerced": False,
        "described_as_anonymised": False,
        "values_invented": False,
    }


def _force(result: dict) -> None:
    result["locks"] = _locks()
    result["decided"] = False
    result["application_decided"] = False
    result["sent"] = False
    result["production_written"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["caller_schema_applied"] = False
    result["coerced"] = False
    result["described_as_anonymised"] = False
    result["values_invented"] = False
    result["may_be_relied_on"] = False
    bank = result.get("bank")
    if isinstance(bank, dict):
        bank["call_back_performed"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
    for row in result.get("fields") or []:
        if isinstance(row, dict):
            row["verified"] = False
            row["coerced"] = False


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


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in _PROHIBITED:
        if key in working:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


def _form_schema(catalogue: dict, form_type: object) -> dict | None:
    forms = catalogue.get("forms") if isinstance(catalogue, dict) else None
    if not isinstance(form_type, str) or not isinstance(forms, dict):
        return None
    found = forms.get(form_type)
    return found if isinstance(found, dict) else None


def _field_ids(schema: object) -> list[str]:
    if not isinstance(schema, dict):
        return []
    rows = schema.get("fields")
    if not isinstance(rows, list):
        return []
    found = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("field_id"), str):
            found.append(row["field_id"])
    return sorted(set(found))


def _schema_check(caller: object, pinned: dict | None, form_type: object) -> dict:
    pinned_ids = _field_ids(pinned) if pinned else []
    if caller is None:
        return {
            "supplied": False,
            "differs": False,
            "applied": False,
            "pinned_form_type": form_type if pinned else None,
            "caller_field_ids": [],
            "pinned_field_ids": pinned_ids,
        }
    caller_ids = _field_ids(caller) if isinstance(caller, dict) else []
    differs = caller_ids != pinned_ids or not isinstance(caller, dict)
    if isinstance(caller, dict) and pinned:
        differs = differs or caller.get("bank_details_change") != pinned.get("bank_details_change")
    return {
        "supplied": True,
        "differs": differs,
        "applied": False,
        "pinned_form_type": form_type if pinned else None,
        "caller_field_ids": caller_ids,
        "pinned_field_ids": pinned_ids,
    }


def _review_sheet(rows: list[dict]) -> dict:
    material = []
    for row in rows:
        if not row.get("material"):
            continue
        material.append(
            {
                "field_id": row["field_id"],
                "material_class": row.get("material_class"),
                "status": row["status"],
                "value": row["value"],
                "flags": list(row["flags"]),
                "locations": row["locations"],
                "confidence": row["confidence"],
                "verified": False,
            }
        )
    return {"material_fields": material}


def _date_rows(rows: list[dict]) -> list[dict]:
    found = []
    for row in rows:
        if row["kind"] != "date":
            continue
        found.append(
            {
                "field_id": row["field_id"],
                "iso": row["value"] if row["status"] == "extracted" else None,
                "days_from_as_of": row["days_from_as_of"],
                "flags": list(row["flags"]),
                "coerced": False,
            }
        )
    return found


def _acks(result_bits: dict) -> list[str]:
    required = ["material_fields_seen", "pins_seen"]
    if result_bits["stale"]:
        required.append("sources_seen")
    if result_bits["date_flags"]:
        required.append("dates_seen")
    if result_bits["schema_differs"] or result_bits["unknown_form"]:
        required.append("schema_seen")
    if result_bits["bank"]:
        required.append("bank_callback_seen")
    if result_bits["field_flags"]:
        required.append("flags_seen")
    if result_bits["suppressed"]:
        required.append("suppression_seen")
    if result_bits["marked"]:
        required.append("marking_seen")
    if result_bits["injection"]:
        required.append("injection_seen")
    return required


def _store_held(result: dict) -> None:
    _HELD[result["extraction_id"]] = deepcopy(result)


def extract_form(request: dict, *, as_of: date | str) -> dict:
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    on = as_date(as_of)
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    working, ignored = _strip(request)
    extraction_id = working.get("extraction_id")
    form_id = working.get("form_id")
    if not isinstance(extraction_id, str) or not _ID.fullmatch(extraction_id):
        raise ValueError("extraction_id must be 1 to 40 letters, digits, hyphens, or underscores")
    if not isinstance(form_id, str) or not _ID.fullmatch(form_id):
        raise ValueError("form_id must be 1 to 40 letters, digits, hyphens, or underscores")
    text = working.get("text", "")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    reviewer_ref = working.get("reviewer_ref")
    if reviewer_ref is not None and not isinstance(reviewer_ref, str):
        raise ValueError("reviewer_ref must be a string")

    catalogue = pinned_sources()["schemas"]
    directory = pinned_sources()["directory"]
    form_type = working.get("form_type")
    pinned = _form_schema(catalogue, form_type)
    review_due = as_date(catalogue["review_due"])
    stale = on >= review_due
    metadata = working.get("metadata") if isinstance(working.get("metadata"), dict) else {}
    meta_labels, meta_bad = metadata_markings(metadata.get("marking"))
    content_labels = content_markings(text)
    applied = higher_marking(meta_labels + content_labels)
    held, hold_unparseable = legal_hold(metadata.get("legal_hold"), text)
    retention, retention_unparseable = retention_labels(metadata.get("retention"), text)
    role = directory.get("reviewer_role")
    person = _person(directory, reviewer_ref)
    reviewer_ok = (
        person is not None
        and person.get("guest") is not True
        and person.get("role") == role
    )
    ceiling = person.get("clearance") if reviewer_ok else None
    detail_withheld = above_ceiling(applied, ceiling if reviewer_ok else None)

    threshold = int(catalogue.get("small_number_threshold") or 5)
    if pinned:
        extracted = extract_fields(text, list(pinned.get("fields") or []), on=on, threshold=threshold)
    else:
        extracted = {"fields": [], "unexpected_fields": [], "suppression": {
            "threshold": threshold,
            "small_count_field_ids": [],
            "count_field_ids": [],
            "percent_field_ids": [],
            "difference_field_ids": [],
            "values_copied": False,
            "rule": "No pinned schema, so no count was read.",
        }}
    fields = extracted["fields"]
    bank_form = bool(pinned and pinned.get("bank_details_change"))
    bank_ticked = any(
        row["field_id"] == "bank_details_change" and row.get("value") == "ticked" for row in fields
    )
    high_risk = bank_form or bank_ticked
    if detail_withheld:
        withhold(fields)
    categories = route_categories(text)
    routed = bool(categories)
    if routed:
        outcome = "route_to_human"
    elif pinned is None:
        outcome = "unknown_form_type"
    elif not reviewer_ok:
        outcome = "needs_named_reviewer"
    else:
        outcome = "draft_for_review"

    cue_names = [name for name in hits(text) if name in {"embedded_instruction", "approval_marker", "callback_claim"}]
    _masked, mask_counts = mask_text(text)
    schema_check = _schema_check(working.get("schema"), pinned, form_type)
    field_flags = any(set(row["flags"]) & _FLAG_ACK for row in fields)
    date_flags = any(row["kind"] == "date" and set(row["flags"]) & _FLAG_ACK for row in fields)
    suppressed = bool(extracted["suppression"]["small_count_field_ids"])
    marked = applied is not None or held or bool(retention)
    injection = "embedded_instruction" in cue_names
    acks = _acks(
        {
            "stale": stale,
            "date_flags": date_flags,
            "schema_differs": schema_check["differs"],
            "unknown_form": pinned is None,
            "bank": high_risk,
            "field_flags": field_flags,
            "suppressed": suppressed,
            "marked": marked,
            "injection": injection,
        }
    )
    identifiers = identifier_counts(text, on=on) if text else {
        "called": False,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "count": 0,
        "types": [],
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
    }
    intake = intake_files(
        [
            {
                "file_id": "form-text",
                "filename": "form.txt",
                "media_type": "text/plain",
                "content": text,
                "document_date": on.isoformat(),
            }
        ],
        on=on,
    ) if text else {
        "called": False,
        "reason": "no_files",
        "experiment_id": "exp-12-document-intake",
        "files_confirmed": False,
        "purpose_confirmed": False,
        "content_recorded": False,
        "body_copied": False,
    }
    values_retained = any(row.get("value") not in (None, "") for row in fields) and not detail_withheld
    masking = {
        "counts": mask_counts["counts"],
        "any": mask_counts["any"],
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "masked_text_included": False,
        "form_text_copied": False,
        "audit_log_contains_raw_values": False,
        "schema_field_values_retained_for_review": values_retained,
    }
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "extraction_id": extraction_id,
        "form_id": form_id,
        "form_type": form_type if isinstance(form_type, str) else None,
        "reviewer_ref": reviewer_ref,
        "reviewer_on_directory": reviewer_ok,
        "as_of": on.isoformat(),
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "may_be_relied_on": False,
        "sources_current": not stale,
        "source_review_due": review_due.isoformat(),
        "detail_withheld": detail_withheld,
        "fields": fields,
        "unexpected_fields": extracted["unexpected_fields"],
        "review_sheet": _review_sheet(fields),
        "date_arithmetic": _date_rows(fields),
        "bank": {
            "high_risk": high_risk,
            "reason": "supplier_bank_change" if bank_form else ("bank_details_change_ticked" if bank_ticked else None),
            "call_back_required": high_risk,
            "call_back_performed": False,
            "claim_in_text_ignored": "callback_claim" in cue_names,
        },
        "marking": {
            "applied": applied,
            "from_metadata": meta_labels,
            "from_content": content_labels,
            "metadata_unreadable": meta_bad,
            "self_declared_clearance_ignored": True,
        },
        "legal_hold": held,
        "legal_hold_unparseable": hold_unparseable,
        "retention": retention,
        "retention_unparseable": retention_unparseable,
        "prompt_injection": {
            "followed": False,
            "categories": cue_names,
            "approval_marker_in_text": "approval_marker" in cue_names,
            "callback_claim_in_text": "callback_claim" in cue_names,
        },
        "suppression": extracted["suppression"],
        "distress": {"routed": routed, "categories": categories, "cue_copied": False},
        "schema_check": schema_check,
        "ignored_request_keys": ignored,
        "required_acknowledgements": acks,
        "masking": masking,
        "audit_log": {
            "extraction_id": extraction_id,
            "outcome": outcome,
            "form_text_copied": False,
            "personal_data_copied": False,
            "described_as_anonymised": False,
            "mask_counts": mask_counts["counts"],
        },
        "uk_identifiers": identifiers,
        "intake": intake,
        "uk_context": uk_context(),
        "reused": {
            "document_intake": "exp-12-document-intake",
            "redaction": "exp-08-uk-pii-redaction-gateway",
            "duplicated": False,
        },
        "network_called": False,
        "model_called": False,
    }
    _force(result)
    result["content_hash"] = content_hash(result)
    _store_held(result)
    return deepcopy(result)


def _matches_held(caller: dict) -> tuple[dict | None, str | None]:
    if not isinstance(caller, dict):
        return None, "caller_not_object"
    extraction_id = caller.get("extraction_id")
    held = _HELD.get(extraction_id) if isinstance(extraction_id, str) else None
    if not isinstance(held, dict):
        return None, "no_agent_held_copy"
    if _projection(caller) != _projection(held) or caller.get("content_hash") != held.get("content_hash"):
        return None, "caller_copy_differs_from_agent_held"
    return held, None


def _named_reviewer(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_sources()["directory"]
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("reviewer_ref"):
        return None, "not_the_named_reviewer"
    person = _person(pinned, approver_ref)
    role = pinned.get("reviewer_role")
    if person is None or person.get("guest") is True or person.get("role") != role:
        return None, "approver_not_directory_reviewer"
    return person, None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def _refused(result: dict, reason: str) -> dict:
    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    updated["blocked_reason"] = reason
    updated["content_hash"] = content_hash(updated)
    return updated


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named reviewer has seen a human route. Nothing is staged."""

    if not isinstance(approval, dict):
        return _refused(result, "approval_not_object")
    if approval.get("item") != "route-seen" or approval.get("decision") != "seen":
        return _refused(result, "wrong_item")
    held, reason = _matches_held(result)
    if reason or held is None:
        return _refused(result, reason or "no_agent_held_copy")
    if approval.get("content_hash") != held.get("content_hash"):
        return _refused(result, "content_hash_mismatch")
    _person_row, role_reason = _named_reviewer(held, directory, approval.get("approver_ref"))
    if role_reason:
        return _refused(result, role_reason)
    updated = deepcopy(held)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    updated["route_seen"] = True
    updated["distress"] = {
        "routed": True,
        "categories": list((held.get("distress") or {}).get("categories") or []),
        "cue_copied": False,
        "seen": True,
    }
    updated["content_hash"] = content_hash(updated)
    _store_held(updated)
    return deepcopy(updated)


def record_reviewer_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Stage the record only when the named reviewer approves the held copy."""

    if not isinstance(approval, dict):
        return _refused(result if isinstance(result, dict) else {}, "approval_not_object")
    if approval.get("decision") in {"decide", "send", "approve-application"} or approval.get("decided") is True:
        return _refused(result, "decide_is_not_this_step")
    if approval.get("item") != "form-record" or approval.get("decision") != "approve-draft":
        return _refused(result, "wrong_item")
    held, reason = _matches_held(result)
    if reason or held is None:
        return _refused(result, reason or "no_agent_held_copy")
    if approval.get("content_hash") != held.get("content_hash"):
        return _refused(result, "content_hash_mismatch")
    if approval.get("extraction_id") != held.get("extraction_id"):
        return _refused(result, "extraction_mismatch")
    if held.get("outcome") == "unknown_form_type":
        return _refused(result, "unknown_form_type")
    if held.get("outcome") == "needs_named_reviewer" or held.get("reviewer_on_directory") is not True:
        return _refused(result, "reviewer_not_on_directory")
    if held.get("detail_withheld") is True:
        return _refused(result, "clearance_below_marking")
    if held.get("outcome") == "route_to_human" and held.get("route_seen") is not True:
        return _refused(result, "route_not_seen")
    ack_reason = _ack(held, approval)
    if ack_reason:
        return _refused(result, ack_reason)
    person, role_reason = _named_reviewer(held, directory, approval.get("approver_ref"))
    if role_reason:
        return _refused(result, role_reason)
    current = held["content_hash"]
    key = f"{held['extraction_id']}:{current}"
    if key in _STORE:
        refused = _refused(held, "already_staged")
        refused["content_hash"] = current
        return refused
    updated = deepcopy(held)
    _force(updated)
    updated["human_approval"] = {
        "item": "form-record",
        "approver_ref": person["employee_ref"],
        "content_hash": current,
        "recorded": True,
        "decides": False,
    }
    updated["staged"] = True
    updated["route_seen"] = held.get("route_seen") is True
    updated["content_hash"] = current
    row = {
        "extraction_id": held.get("extraction_id"),
        "form_id": held.get("form_id"),
        "form_type": held.get("form_type"),
        "content_hash": current,
        "reviewer_ref": person["employee_ref"],
        "fields": deepcopy(held.get("fields")),
        "review_sheet": deepcopy(held.get("review_sheet")),
        "bank": deepcopy(held.get("bank")),
        "marking": deepcopy(held.get("marking")),
        "legal_hold": held.get("legal_hold"),
        "retention": list(held.get("retention") or []),
        "prompt_injection": deepcopy(held.get("prompt_injection")),
        "suppression": deepcopy(held.get("suppression")),
        "distress": deepcopy(held.get("distress")),
        "required_acknowledgements": list(held.get("required_acknowledgements") or []),
        "route_seen": held.get("route_seen") is True,
        "detail_withheld": held.get("detail_withheld"),
        "schema_check": deepcopy(held.get("schema_check")),
        "decided": False,
        "sent": False,
        "production_written": False,
        "call_back_performed": False,
        "store": "synthetic",
    }
    _STORE[key] = row
    updated["staging_store"] = "synthetic"
    return updated


def staged_row(extraction_id: object, content_hash_value: object) -> dict | None:
    if not isinstance(extraction_id, str) or not isinstance(content_hash_value, str):
        return None
    row = _STORE.get(f"{extraction_id}:{content_hash_value}")
    return deepcopy(row) if isinstance(row, dict) else None


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract a synthetic form into a draft record.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = extract_form(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
