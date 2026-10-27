#!/usr/bin/env python3
"""Inventory one synthetic document batch.

``intake`` returns a draft. It does not confirm the files, set the permitted
purpose, accept the batch into a queue, write a record, send a message, or
release redacted text. The two record functions check a role. They still do
not do those things. The forbid functions always raise.

UK identifier spans come from Experiment 08. This module does not copy the
detectors and does not ask for a reversible token map.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from catalogue import (
        CATALOGUE_ID,
        CATALOGUE_PINNED_ON,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        GATEWAY_CALLER,
        GATEWAY_CATALOGUE_ID,
        GATEWAY_EXPERIMENT_ID,
        PURPOSES,
        build_checklist,
        markers_in,
        suggest_class,
    )
    from injection import merge_scans, scan_text
else:
    from .catalogue import (
        CATALOGUE_ID,
        CATALOGUE_PINNED_ON,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        GATEWAY_CALLER,
        GATEWAY_CATALOGUE_ID,
        GATEWAY_EXPERIMENT_ID,
        PURPOSES,
        build_checklist,
        markers_in,
        suggest_class,
    )
    from .injection import merge_scans, scan_text

LABEL = "DRAFT FOR INTAKE REVIEW"
USER_ROLE = "Intake user"
REVIEWER_ROLE = "Intake reviewer"
DECISIONS = frozenset({"accept_routing", "return_for_edit", "reject_routing"})
MAX_FILES = 12
MAX_CHARS = 20_000
ALLOWED_MEDIA = frozenset({"text/plain"})
FILE_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
PURPOSE_TOKEN = re.compile(r"^[a-z_]{1,40}$")
NOT_CURRENT = frozenset({"stale", "missing", "future", "invalid"})

PROHIBITED_KEYS = frozenset(
    {
        "files_confirmed",
        "purpose_confirmed",
        "permitted_purpose",
        "reviewer_decision",
        "accepted_into_queue",
        "production_record_written",
        "external_sent",
        "anonymised",
        "anonymized",
        "agent_may_release",
        "approve",
        "reject",
        "commit",
        "send",
    }
)

LIMITATIONS = (
    "This draft does not confirm the files or the permitted purpose.",
    "A keyword class is not a decision about what the document is.",
    "A complete checklist is phrase presence. It is not a finding that the pack is sufficient.",
    "This starter reads text/plain only. Another media type is not_read, which is a gap, not a clean result.",
    "A file over 20,000 characters is not scanned. An instruction in it is not detected.",
    "UK identifier redaction is Experiment 08. The output is not anonymised. Names, email addresses, and telephone numbers are not detected.",
    "The file body is not copied into this draft. A filename is stored as supplied.",
    "The 90-day window is a stale flag for this starter. It is not a statutory retention period.",
    "B004, B007, UK11, and UK09 are labels. They are not called.",
    "No model was called.",
)


class IntakeForbidden(RuntimeError):
    """The intake has no queue, send, write, or release path."""


class NotSynthetic(ValueError):
    """The batch was not marked synthetic. The message does not include the body."""


def _gateway_propose():
    gateway_src = Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise IntakeForbidden(
            "Experiment 08 is not beside this experiment. Intake will not invent a redactor."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _strip_prohibited(mapping: dict, prefix: str) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS or (prefix and key == "requested_purpose"):
            found.append(f"{prefix}{key}" if prefix else key)
            del mapping[key]
    return found


def _parse_document_date(raw, as_of: date, window: int) -> tuple[str, str | None, int | None]:
    if raw is None or raw == "":
        return "missing", None, None
    if not isinstance(raw, str):
        return "invalid", None, None
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        return "invalid", None, None
    age = (as_of - parsed).days
    if age < 0:
        return "future", parsed.isoformat(), age
    if age > window:
        return "stale", parsed.isoformat(), age
    return "within_window", parsed.isoformat(), age


def _requested_purpose(value) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, str) or not PURPOSE_TOKEN.fullmatch(value):
        return {"id": None, "in_catalogue": False, "rejected": True, "preview_only": True}
    if value not in PURPOSES:
        return {"id": value, "in_catalogue": False, "rejected": False, "preview_only": True}
    purpose = PURPOSES[value]
    return {
        "id": value,
        "label": purpose["label"],
        "in_catalogue": True,
        "rejected": False,
        "preview_only": True,
        "downstream_catalogue_id": purpose["downstream_catalogue_id"],
    }


def _blockers(files: list[dict]) -> list[str]:
    reasons = []
    for file in files:
        if file["read_status"] != "read":
            reasons.append(f"{file['file_id']}:{file['read_status']}")
        elif file["checksum_matches"] is False:
            reasons.append(f"{file['file_id']}:checksum_mismatch")
    return reasons


def _warnings(files: list[dict]) -> list[str]:
    warnings = []
    for file in files:
        if file["date_status"] in NOT_CURRENT:
            warnings.append(f"{file['file_id']}:date_{file['date_status']}")
        if file["duplicate_of"]:
            warnings.append(f"{file['file_id']}:duplicate_of:{file['duplicate_of']}")
    return warnings


def _routing_awaiting(files: list[dict]) -> dict:
    return {
        "status": "awaiting_file_and_purpose_confirmation",
        "purpose_id": None,
        "downstream_catalogue_id": None,
        "downstream_note": "The user has not confirmed a purpose.",
        "handed_off": False,
        "blocked_reasons": _blockers(files),
        "warnings": _warnings(files),
    }


def _suggest_routing(files: list[dict], purpose_id: str, checklist: dict) -> dict:
    purpose = PURPOSES[purpose_id]
    blocked = _blockers(files)
    if blocked:
        status = "routing_blocked"
    elif not checklist["complete"]:
        status = "routing_suggested_with_gaps"
    else:
        status = "routing_suggested"
    return {
        "status": status,
        "purpose_id": purpose_id,
        "downstream_catalogue_id": purpose["downstream_catalogue_id"],
        "downstream_note": purpose["downstream_note"],
        "handed_off": False,
        "blocked_reasons": blocked,
        "warnings": _warnings(files),
    }


def _redaction(content: str, *, rules_as_of: date | None) -> dict:
    proposal = _gateway_propose()(
        content,
        caller=GATEWAY_CALLER,
        rules_as_of=rules_as_of,
        apply_model_suggestions=False,
        reversible=False,
    )
    findings = [
        finding
        for finding in proposal["audit_log"]["findings"]
        if finding.get("applied") and finding.get("method") == "deterministic"
    ]
    entity_types: list[str] = []
    for finding in findings:
        if finding["entity_type"] not in entity_types:
            entity_types.append(finding["entity_type"])
    return {
        "called": True,
        "gateway": GATEWAY_EXPERIMENT_ID,
        "catalogue_id": GATEWAY_CATALOGUE_ID,
        "caller": GATEWAY_CALLER,
        "finding_count": len(findings),
        "entity_types": entity_types,
        "rules_pinned_on": proposal["audit_log"]["rules_pinned_on"],
        "rules_stale": bool(proposal["audit_log"]["rules_stale"]),
        "model_assist": proposal["audit_log"]["model_assist"],
        "output_is_anonymised": False,
        "agent_may_release": False,
        "input_sha256": proposal["audit_log"]["input_sha256"],
    }


def _empty_pii() -> dict:
    return {
        "called": False,
        "gateway": GATEWAY_EXPERIMENT_ID,
        "catalogue_id": GATEWAY_CATALOGUE_ID,
        "caller": GATEWAY_CALLER,
        "finding_count": 0,
        "entity_types": [],
        "rules_pinned_on": None,
        "rules_stale": False,
        "model_assist": "not_called",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "input_sha256": None,
    }


def _file_row(
    raw: dict,
    *,
    as_of: date,
    window: int,
    rules_as_of: date | None,
    seen_hashes: dict[str, str],
) -> tuple[dict, list[dict]]:
    file_id = raw.get("file_id")
    if not isinstance(file_id, str) or not FILE_ID.fullmatch(file_id):
        raise ValueError("file_id must be 1 to 40 letters, digits, hyphens, or underscores")
    filename = raw.get("filename", "")
    if not isinstance(filename, str) or not filename or len(filename) > 120 or "\n" in filename:
        raise ValueError("filename must be a single line of at most 120 characters")
    media = raw.get("media_type", "")
    if not isinstance(media, str):
        media = ""
    media = media.strip().lower()
    content = raw.get("content", "")
    if not isinstance(content, str):
        raise ValueError("content must be a string")
    date_status, document_date, age_days = _parse_document_date(raw.get("document_date"), as_of, window)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    supplied = raw.get("sha256")
    if supplied is None:
        checksum_supplied = False
        checksum_matches = None
    else:
        checksum_supplied = True
        checksum_matches = isinstance(supplied, str) and supplied.lower() == digest
    duplicate_of = seen_hashes.get(digest)
    if digest not in seen_hashes and content != "":
        seen_hashes[digest] = file_id

    scans = [scan_text(filename, file_id=file_id, where="filename")]
    suggestion = {"suggested_class": None, "candidate_classes": []}
    found_markers: list[str] = []
    pii = _empty_pii()
    if media not in ALLOWED_MEDIA:
        read_status = "not_read"
    elif content == "":
        read_status = "empty"
    elif len(content) > MAX_CHARS:
        read_status = "too_large"
    else:
        read_status = "read"
    # A pasted string under the cap is scanned even when the media type is not
    # text/plain. That does not mean the file was read. An oversized file is
    # not truncated and then scanned.
    injection_scanned = bool(content) and len(content) <= MAX_CHARS
    if injection_scanned:
        scans.append(scan_text(content, file_id=file_id, where="body"))
    if read_status == "read":
        suggestion = suggest_class(content)
        found_markers = markers_in(content)
        pii = _redaction(content, rules_as_of=rules_as_of)

    row = {
        "file_id": file_id,
        "filename": filename,
        "media_type": media,
        "read_status": read_status,
        "sha256": digest,
        "checksum_supplied": checksum_supplied,
        "checksum_matches": checksum_matches,
        "char_count": len(content),
        "document_date": document_date,
        "date_status": date_status,
        "age_days": age_days,
        "suggested_class": suggestion["suggested_class"],
        "candidate_classes": suggestion["candidate_classes"],
        "markers_found": found_markers,
        "duplicate_of": duplicate_of,
        "pii": pii,
        "content_recorded": False,
        "injection_scanned": injection_scanned,
    }
    return row, scans


def _limitations(files: list[dict], *, catalogue_stale: bool, gateway_rules_stale: bool) -> list[str]:
    notes = list(LIMITATIONS)
    if any(file["read_status"] == "not_read" for file in files):
        notes.append("A file was not read. That is a gap, not a clean result.")
    if any(file["read_status"] == "too_large" for file in files):
        notes.append("A file over 20,000 characters was not scanned.")
    if catalogue_stale:
        notes.append(
            "The purpose catalogue is older than the stale window. "
            "The pinned list was still used."
        )
    if gateway_rules_stale:
        notes.append(
            "The caller supplied a rules date before Experiment 08's pin. "
            "Detection still used the pinned rules."
        )
    return notes


def _human_approval() -> dict:
    return {
        "files_and_purpose": {"required": True, "approver": USER_ROLE, "recorded": False},
        "routing": {"required": True, "approver": REVIEWER_ROLE, "recorded": False},
        "release_of_redacted_text": {
            "required": True,
            "approver": "Privacy reviewer",
            "recorded": False,
            "performed_by_this_agent": False,
        },
    }


def _flags() -> dict:
    return {
        "accepted_into_queue": False,
        "production_record_written": False,
        "external_sent": False,
        "underlying_matter_approved": False,
        "underlying_matter_rejected": False,
        "redacted_text_released": False,
        "output_is_anonymised": False,
        "purpose_taken_from_document": False,
        "files_confirmed_by_document": False,
        "handed_off": False,
    }


def _force_inert(draft: dict) -> None:
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["flags"] = _flags()
    draft["gateway"]["output_is_anonymised"] = False
    draft["gateway"]["agent_may_release"] = False
    draft["gateway"]["reversible_requested"] = False
    draft["gateway"]["model_suggestions_applied"] = False
    draft["prompt_injection"]["followed"] = False
    for signal in draft["prompt_injection"]["signals"]:
        signal["followed"] = False
    for file in draft["files"]:
        file["content_recorded"] = False
        file["pii"]["output_is_anonymised"] = False
        file["pii"]["agent_may_release"] = False
    draft["routing"]["handed_off"] = False
    draft["human_approval"]["release_of_redacted_text"]["recorded"] = False
    draft["human_approval"]["release_of_redacted_text"]["performed_by_this_agent"] = False
    if "checklist_preview" in draft and draft["checklist_preview"] is not None:
        draft["checklist_preview"]["sufficient"] = False
    if draft.get("checklist") is not None:
        draft["checklist"]["sufficient"] = False


def intake(
    batch: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    rules_as_of: date | None = None,
) -> dict:
    """Return a draft inventory. Confirmation flags stay false."""

    if not isinstance(batch, dict):
        raise TypeError("batch must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if rules_as_of is not None and not isinstance(rules_as_of, date):
        raise TypeError("rules_as_of must be a date")
    if batch.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")

    working = dict(batch)
    prohibited = _strip_prohibited(working, "")
    files_in = working.get("files")
    if not isinstance(files_in, list) or not files_in:
        raise ValueError("batch has no files")
    if len(files_in) > MAX_FILES:
        raise ValueError("batch has more files than the starter will inventory")

    batch_id = working.get("batch_id", "unspecified")
    if not isinstance(batch_id, str) or not batch_id or len(batch_id) > 80 or "\n" in batch_id:
        batch_id = "unspecified"

    rows = []
    scans = []
    seen_ids: set[str] = set()
    seen_hashes: dict[str, str] = {}
    for raw in files_in:
        if not isinstance(raw, dict):
            raise ValueError("each file must be an object")
        file_copy = dict(raw)
        prohibited.extend(_strip_prohibited(file_copy, f"file:{file_copy.get('file_id', '?')}:"))
        row, file_scans = _file_row(
            file_copy,
            as_of=as_of,
            window=stale_after_days,
            rules_as_of=rules_as_of,
            seen_hashes=seen_hashes,
        )
        if row["file_id"] in seen_ids:
            raise ValueError("duplicate file_id")
        seen_ids.add(row["file_id"])
        rows.append(row)
        scans.extend(file_scans)

    catalogue_age = (as_of - CATALOGUE_PINNED_ON).days
    catalogue_stale = catalogue_age > stale_after_days
    gateway_rules_stale = any(row["pii"]["rules_stale"] for row in rows)
    requested = _requested_purpose(working.get("requested_purpose"))
    checklist_preview = None
    if requested and requested.get("in_catalogue"):
        checklist_preview = build_checklist(requested["id"], rows)

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "batch_id": batch_id,
        "as_of": as_of.isoformat(),
        "catalogue_pinned_on": CATALOGUE_PINNED_ON.isoformat(),
        "catalogue_age_days": catalogue_age,
        "catalogue_stale": catalogue_stale,
        "stale_after_days": stale_after_days,
        "any_document_stale": any(row["date_status"] == "stale" for row in rows),
        "any_document_not_current": any(row["date_status"] in NOT_CURRENT for row in rows),
        "gateway_rules_stale": gateway_rules_stale,
        "rules_current": not catalogue_stale and not gateway_rules_stale,
        "model_called": False,
        "network_called": False,
        "gateway": {
            "experiment_id": GATEWAY_EXPERIMENT_ID,
            "catalogue_id": GATEWAY_CATALOGUE_ID,
            "called": any(row["pii"]["called"] for row in rows),
            "files_scanned": sum(1 for row in rows if row["pii"]["called"]),
            "output_is_anonymised": False,
            "agent_may_release": False,
            "reversible_requested": False,
            "model_suggestions_applied": False,
        },
        "files_confirmed": False,
        "purpose_confirmed": False,
        "permitted_purpose": None,
        "requested_purpose": requested,
        "confirmation": None,
        "reviewer_decision": None,
        "review": None,
        "routing": _routing_awaiting(rows),
        "actions_taken": [],
        "flags": _flags(),
        "prompt_injection": merge_scans(scans),
        "prohibited_payload_keys": prohibited,
        "files": rows,
        "checklist_preview": checklist_preview,
        "checklist": None,
        "human_approval": _human_approval(),
        "limitations": _limitations(
            rows,
            catalogue_stale=catalogue_stale,
            gateway_rules_stale=gateway_rules_stale,
        ),
    }
    _force_inert(draft)
    return draft


def _require_draft(draft: dict) -> dict:
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not an intake result")
    if draft.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("draft is not an intake result")
    return deepcopy(draft)


def record_user_confirmation(
    draft: dict,
    *,
    role: str,
    file_ids: list[str],
    purpose: str,
) -> dict:
    """Record that an intake user confirmed the files and a purpose.

    The agent must not call this. A matching role does not accept the batch
    into a queue and does not approve the underlying matter.
    """

    if role != USER_ROLE:
        raise ValueError("only an Intake user can confirm files and purpose")
    updated = _require_draft(draft)
    if not isinstance(file_ids, list) or not file_ids:
        raise ValueError("file_ids must list every file in the draft, in order")
    actual = [file["file_id"] for file in updated["files"]]
    if list(file_ids) != actual:
        raise ValueError("file_ids must match the draft, in order")
    if any(file["checksum_matches"] is False for file in updated["files"]):
        raise ValueError("a file checksum does not match; confirmation is refused")
    if purpose not in PURPOSES:
        raise ValueError("purpose is not in the closed list")

    checklist = build_checklist(purpose, updated["files"])
    checklist["preview_only"] = False
    updated["files_confirmed"] = True
    updated["purpose_confirmed"] = True
    updated["permitted_purpose"] = {
        "id": purpose,
        "label": PURPOSES[purpose]["label"],
        "downstream_catalogue_id": PURPOSES[purpose]["downstream_catalogue_id"],
        "downstream_note": PURPOSES[purpose]["downstream_note"],
    }
    updated["checklist"] = checklist
    updated["routing"] = _suggest_routing(updated["files"], purpose, checklist)
    updated["confirmation"] = {
        "role": USER_ROLE,
        "purpose_id": purpose,
        "file_ids": list(file_ids),
        "does_not_accept_into_queue": True,
        "does_not_approve_the_underlying_matter": True,
    }
    updated["human_approval"]["files_and_purpose"]["recorded"] = True
    updated["reviewer_decision"] = None
    updated["review"] = None
    _force_inert(updated)
    return updated


def record_reviewer_decision(
    draft: dict,
    *,
    role: str,
    decision: str,
    acknowledge_stale: bool = False,
) -> dict:
    """Record an intake reviewer's routing decision.

    The agent must not call this. ``accept_routing`` still does not write a
    queue. Stale, missing, or future material is refused unless the caller
    passes ``acknowledge_stale``. A blocked file is refused even then.
    """

    if role != REVIEWER_ROLE:
        raise ValueError("only an Intake reviewer can record this decision")
    if decision not in DECISIONS:
        raise ValueError("decision must be accept_routing, return_for_edit, or reject_routing")
    if acknowledge_stale is not True and acknowledge_stale is not False:
        raise TypeError("acknowledge_stale must be a boolean")
    updated = _require_draft(draft)
    if updated.get("files_confirmed") is not True or updated.get("purpose_confirmed") is not True:
        raise ValueError("files and purpose are not confirmed")
    if decision == "accept_routing":
        if updated["routing"]["status"] == "routing_blocked":
            raise ValueError("routing is blocked until every file is examined and checksums match")
        not_current = updated["any_document_not_current"] or updated["catalogue_stale"]
        if not_current and not acknowledge_stale:
            raise ValueError("stale, missing, or future material requires acknowledge_stale from a person")
    updated["reviewer_decision"] = decision
    updated["review"] = {
        "role": REVIEWER_ROLE,
        "decision": decision,
        "stale_acknowledged": bool(acknowledge_stale) if decision == "accept_routing" else False,
        "does_not_accept_into_queue": True,
    }
    updated["human_approval"]["routing"]["recorded"] = True
    _force_inert(updated)
    return updated


def commit_to_queue(_draft: dict) -> None:
    """Refuse to accept the batch into a queue."""

    raise IntakeForbidden("the agent does not accept a file into a queue")


def send_external(_draft: dict) -> None:
    """Refuse to send."""

    raise IntakeForbidden("the agent does not send")


def write_production_record(_draft: dict) -> None:
    """Refuse to write a production record."""

    raise IntakeForbidden("the agent does not write a production record")


def approve_underlying_matter(_draft: dict) -> None:
    """Refuse to approve KYC, a claim, a disclosure, or a finding."""

    raise IntakeForbidden(
        "the agent does not approve a KYC file, a claim, a disclosure, or a case"
    )


def reject_underlying_matter(_draft: dict) -> None:
    """Refuse to reject KYC, a claim, a disclosure, or a finding."""

    raise IntakeForbidden(
        "the agent does not reject a KYC file, a claim, a disclosure, or a case"
    )


def release_redacted(_draft: dict) -> None:
    """Refuse to release redacted text."""

    raise IntakeForbidden("redacted text is not released")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a document intake. Does not accept the batch.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--rules-as-of", default=None)
    args = parser.parse_args(argv)
    batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rules = date.fromisoformat(args.rules_as_of) if args.rules_as_of else None
    try:
        draft = intake(
            batch,
            as_of=date.fromisoformat(args.as_of),
            stale_after_days=args.stale_after_days,
            rules_as_of=rules,
        )
    except NotSynthetic:
        sys.stderr.write("REFUSED: record is not marked synthetic\n")
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
