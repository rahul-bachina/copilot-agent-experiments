"""Assemble a draft board pack. Do not circulate it.

The named company secretary approves the exact pack hash before a copy is
written to the synthetic staging store. The agent does not circulate,
publish, file, or send, and it does not record minutes or decisions as approved.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    from checks import (
        carry_forward,
        cover_standard,
        inconsistencies,
        interest_live,
        is_late,
        marking_for,
        paper_hash,
        person,
        publish_count,
        scan_text,
        sponsor_status,
        text_outside,
        version_flags,
    )
    from cues import distress_hit, hits
    from dates import as_date, parse_date
    from negate import affirmed
    from marking import higher_marking
    from mask import mask_text
    from reuse import NeighbourMissing, conflict_links, identifier_counts, intake_papers
    from sources import uk_context
else:
    from .checks import (
        carry_forward,
        cover_standard,
        inconsistencies,
        interest_live,
        is_late,
        marking_for,
        paper_hash,
        person,
        publish_count,
        scan_text,
        sponsor_status,
        text_outside,
        version_flags,
    )
    from .cues import distress_hit, hits
    from .dates import as_date, parse_date
    from .negate import affirmed
    from .marking import higher_marking
    from .mask import mask_text
    from .reuse import NeighbourMissing, conflict_links, identifier_counts, intake_papers
    from .sources import uk_context

LABEL = "BOARD PACK DRAFT FOR THE NAMED COMPANY SECRETARY"
CATALOGUE_ID = "L010"
EXPERIMENT_ID = "exp-74-board-governance-pack"
ROOT = Path(__file__).resolve().parents[1]
_STORE: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "approved",
    "approval",
    "circulated",
    "published",
    "filed",
    "sent",
    "minutes_approved",
    "decisions_recorded",
    "role",
    "clearance",
    "staged",
    "marked_acceptable",
)


class PackForbidden(RuntimeError):
    """The agent does not circulate, publish, file, send, or approve minutes."""

    __test__ = False


class NotSynthetic(ValueError):
    """The record is not marked synthetic."""


def circulate(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not circulate a pack.")


def publish(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not publish a pack.")


def file_pack(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not file a pack.")


def send(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not send a pack.")


def record_decision(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not record a board decision.")


def approve_minutes(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not record minutes as approved.")


def write_production(*_args, **_kwargs) -> None:
    raise PackForbidden("The agent does not write a production record.")


def reset_staging() -> None:
    _STORE.clear()


def _load_json(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    return {
        "agenda": _load_json("forward_agenda.json"),
        "terms": _load_json("terms_of_reference.json"),
        "directory": _load_json("directory.json"),
        "register": _load_json("register.json"),
        "minutes": _load_json("minutes.json"),
        "papers": _load_json("papers.json"),
        "approvals": _load_json("approvals.json"),
        "suppliers": _load_json("suppliers.json"),
        "procurements": _load_json("procurements.json"),
        "standard": _load_json("standard.json"),
    }


def _force(result: dict) -> None:
    result["circulated"] = False
    result["published"] = False
    result["filed"] = False
    result["sent"] = False
    result["minutes_approved"] = False
    result["decisions_recorded"] = False
    result["production_written"] = False
    result["coerced"] = False
    result["instructions_followed"] = False
    result["described_as_anonymised"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["caller_agenda_applied"] = False
    result["caller_terms_applied"] = False
    result["caller_directory_applied"] = False
    result["caller_register_applied"] = False
    result["caller_papers_applied"] = False
    result["conflict_decided"] = False
    result["marked_acceptable"] = False
    result["body_copied"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False


def _projection(result: dict) -> dict:
    return {
        "meeting_id": result.get("meeting_id"),
        "committee_id": result.get("committee_id"),
        "secretary_ref": result.get("secretary_ref"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "agenda": result.get("agenda"),
        "pack_index": result.get("pack_index"),
        "superseded": result.get("superseded"),
        "missing_papers": result.get("missing_papers"),
        "action_log": result.get("action_log"),
        "conflicts": result.get("conflicts"),
        "pack_marking": (result.get("marking") or {}).get("applied"),
        "sources_current": result.get("sources_current"),
        "route_seen": result.get("route_seen"),
    }


def _hash(result: dict) -> str:
    if __package__ in {None, ""}:
        from checks import digest
    else:
        from .checks import digest
    return digest(_projection(result))


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in _PROHIBITED:
        if key in working:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


def _id_diff(caller: object, pinned_ids: set[str], id_field: str) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": "not_object", "applied": False}]
    rows = caller.get("items") or caller.get("people") or caller.get("interests") or caller.get("papers") or []
    if not isinstance(rows, list):
        rows = []
    caller_ids = set()
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get(id_field), str):
            caller_ids.add(row[id_field])
    diffs = []
    for item_id in sorted(caller_ids - pinned_ids):
        diffs.append({"id": item_id, "kind": "not_in_pinned", "applied": False})
    for item_id in sorted(pinned_ids - caller_ids):
        diffs.append({"id": item_id, "kind": "missing_from_caller", "applied": False})
    if not diffs and caller_ids != pinned_ids:
        diffs.append({"kind": "differs_from_pinned", "applied": False})
    if caller_ids == pinned_ids and caller != {}:
        # Same ids can still hide a different title or remit. Any supplied object differs
        # unless it is absent. A supplied copy is never the pinned source.
        if not diffs:
            diffs.append({"kind": "caller_copy_not_authoritative", "applied": False})
    return diffs


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
        "meeting_id": None,
        "committee_id": None,
        "secretary_ref": None,
        "secretary_on_directory": False,
        "agenda": [],
        "pack_index": [],
        "superseded": [],
        "missing_papers": [],
        "duplicates": [],
        "action_log": {"carried": [], "not_carried": [], "minutes_approved": False, "decisions_recorded": False},
        "conflicts": [],
        "papers": [],
        "prompt_injection": {"followed": False, "signals": []},
        "distress": {"routed": False, "cue_copied": False},
        "marking": {"applied": None, "from_metadata": [], "from_content": []},
        "legal_hold": False,
        "retention": [],
        "uk_context": uk_context(),
        "required_acknowledgements": ["pins_seen"],
        "ignored_request_fields": [],
    }
    _force(result)
    result["content_hash"] = _hash(result)
    return result


def _select_papers(pinned_papers: list[dict], request: dict) -> tuple[list[dict], list[str]]:
    flags = []
    selected = [deepcopy(paper) for paper in pinned_papers if isinstance(paper, dict)]
    include = request.get("include_paper_ids", None)
    if include is not None:
        if not isinstance(include, list) or not all(isinstance(item, str) for item in include):
            flags.append("include_paper_ids_unreadable")
        else:
            known = {paper.get("paper_id") for paper in selected}
            unknown = [item for item in include if item not in known]
            if unknown:
                flags.append("unknown_paper_id")
            selected = [paper for paper in selected if paper.get("paper_id") in set(include)]
    additional = request.get("additional_papers")
    if additional is not None:
        if not isinstance(additional, list):
            flags.append("additional_papers_unreadable")
        else:
            for item in additional:
                if isinstance(item, dict):
                    selected.append(deepcopy(item))
                else:
                    flags.append("additional_paper_not_object")
    return selected, flags


def _ceiling(directory: dict, secretary_ref: object) -> str | None:
    row = person(directory, secretary_ref)
    if row is None:
        return None
    clearance = row.get("clearance")
    if not isinstance(clearance, str):
        return None
    return clearance


def assemble_pack(request: dict, as_of: str) -> dict:
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    parsed_on = parse_date(as_of)
    if parsed_on["unparseable"] or parsed_on["ambiguous"] or not parsed_on.get("iso"):
        result = _blank(as_of if isinstance(as_of, str) else "", "unreadable_date")
        result["coerced"] = False
        result["content_hash"] = _hash(result)
        return result
    on = as_date(parsed_on)
    assert on is not None
    pinned = pinned_sources()
    working, ignored = _strip(request)
    agenda = pinned["agenda"]
    terms = pinned["terms"]
    directory = pinned["directory"]
    if working.get("meeting_id") != agenda.get("meeting_id"):
        result = _blank(on.isoformat(), "unknown_meeting")
        result["meeting_id"] = working.get("meeting_id") if isinstance(working.get("meeting_id"), str) else None
        result["ignored_request_fields"] = ignored
        result["content_hash"] = _hash(result)
        return result
    papers, select_flags = _select_papers(pinned["papers"].get("papers") or [], working)
    allowed = set(pinned["standard"].get("purposes") or [])
    threshold = pinned["standard"].get("small_number_threshold")
    ledger = pinned["approvals"].get("approvals") or []
    flags_by_submission = version_flags(papers)
    secretary_ref = working.get("secretary_ref")
    ceiling = _ceiling(directory, secretary_ref)
    secretary = person(directory, secretary_ref)
    secretary_ok = bool(secretary and secretary.get("role") == "company_secretary" and secretary.get("guest") is not True)

    caller_agenda = _id_diff(
        working.get("caller_agenda"),
        {item.get("item_id") for item in agenda.get("items") or [] if isinstance(item, dict)},
        "item_id",
    )
    in_remit = set(terms.get("in_remit") or [])
    caller_terms = _id_diff(working.get("caller_terms"), in_remit, "matter_id")
    if working.get("caller_terms") is not None and not caller_terms:
        caller_terms = [{"kind": "caller_copy_not_authoritative", "applied": False}]
    caller_directory = _id_diff(
        working.get("caller_directory"),
        {row.get("employee_ref") for row in directory.get("people") or [] if isinstance(row, dict)},
        "employee_ref",
    )
    caller_register = _id_diff(
        working.get("caller_register"),
        {row.get("interest_id") for row in pinned["register"].get("interests") or [] if isinstance(row, dict)},
        "interest_id",
    )
    caller_papers = _id_diff(
        working.get("caller_papers"),
        {row.get("paper_id") for row in pinned["papers"].get("papers") or [] if isinstance(row, dict)},
        "paper_id",
    )

    note = working.get("note") if isinstance(working.get("note"), str) else ""
    minute_text = json.dumps(
        {key: pinned["minutes"].get(key) for key in ("minutes_id", "note") if key in pinned["minutes"]}
    )
    # The minutes note is scanned and not copied.
    scanned_minutes = pinned["minutes"].get("note") if isinstance(pinned["minutes"].get("note"), str) else ""

    paper_rows = []
    conflicts = []
    interest_unreadable = False
    distress = False
    signals: list[str] = []
    mask_counts = {"phone": 0, "email": 0, "date_of_birth": 0, "postal_address": 0, "personal_name": 0}
    visible_text = []
    files = []
    all_markings: list[str] = []
    all_retention: list[str] = []
    any_hold = False
    dates_unreadable = False

    for token in hits(note) + hits(scanned_minutes):
        if token not in signals:
            signals.append(token)
    if distress_hit(note) or distress_hit(scanned_minutes):
        distress = True

    attendance = [ref for ref in agenda.get("attendance") or [] if isinstance(ref, str)]
    by_id: dict[str, list[dict]] = {}
    for paper in papers:
        if not isinstance(paper.get("paper_id"), str) or not isinstance(paper.get("submission_id"), str):
            select_flags.append("paper_identity_unreadable")
            continue
        submission = paper["submission_id"]
        row_flags = list(flags_by_submission.get(submission) or [])
        cover = cover_standard(paper, allowed)
        if not cover["purpose_stated"]:
            row_flags.append("purpose_missing_or_invalid")
        if not cover["recommendation_present"]:
            row_flags.append("recommendation_missing")
        for field, state in cover["implications"].items():
            if state != "completed" and state != "not_applicable":
                row_flags.append(f"implication_incomplete:{field}")
        inconsistent = inconsistencies(paper)
        if inconsistent:
            row_flags.append("inconsistent_with_body")
        sponsor = sponsor_status(paper, directory, ledger)
        if not sponsor["recorded"]:
            if sponsor["hash_mismatch"]:
                row_flags.append("sponsor_approval_hash_mismatch")
            else:
                row_flags.append("sponsor_approval_missing")
        if not sponsor["sponsor_on_directory"]:
            row_flags.append("sponsor_not_on_directory")
        author = person(directory, paper.get("author_ref"))
        if author is None or author.get("guest") is True:
            row_flags.append("author_not_on_directory")
        submitted = parse_date(paper.get("submitted_on"))
        document = parse_date((paper.get("cover") or {}).get("document_date") if isinstance(paper.get("cover"), dict) else None)
        if submitted["unparseable"] or submitted["ambiguous"] or document["unparseable"] or document["ambiguous"]:
            row_flags.append("date_unparseable")
            dates_unreadable = True
        late = is_late(paper.get("submitted_on"), agenda.get("papers_deadline"))
        if late is True:
            row_flags.append("late")
        marks = marking_for(paper, ceiling)
        if marks["applied"] is None:
            row_flags.append("marking_missing")
        if marks["above_clearance"]:
            row_flags.append("above_clearance")
        if marks["legal_hold_unparseable"] or marks["retention_unparseable"] or marks["metadata_unparseable"]:
            row_flags.append("label_unparseable")
        scan = scan_text(paper)
        for cue in scan["cues"]:
            if cue not in signals:
                signals.append(cue)
            if cue == "embedded_instruction":
                row_flags.append("embedded_instruction")
            if cue == "approval_marker":
                row_flags.append("approval_marker_in_text")
            if cue == "role_claim":
                row_flags.append("role_in_text")
            if cue == "biased_criteria":
                row_flags.append("biased_criteria")
            if cue == "carve_out":
                row_flags.append("carve_out")
        if scan["distress"]:
            distress = True
            row_flags.append("distress_routed")
        if scan["conflict_declared"]:
            conflicts.append(
                {
                    "paper_id": paper["paper_id"],
                    "kind": "declared",
                    "interest_id": None,
                    "person_ref": None,
                    "conflict_decided": False,
                }
            )
            row_flags.append("conflict_declared")
        outside_text = text_outside(paper.get("body") or "", terms)
        matter = paper.get("matter_id")
        if isinstance(matter, str) and matter not in in_remit:
            row_flags.append("outside_terms")
        elif not isinstance(matter, str) or not matter:
            row_flags.append("matter_unreadable")
        if outside_text:
            row_flags.append("outside_terms_in_text")
        expected_ids = {
            item.get("expected_paper_id")
            for item in agenda.get("items") or []
            if isinstance(item, dict)
        }
        if paper["paper_id"] not in expected_ids:
            row_flags.append("not_on_agenda")
        _masked, counts = mask_text(paper.get("body") or "")
        for kind, count in counts["counts"].items():
            mask_counts[kind] = mask_counts.get(kind, 0) + count
        if not marks["above_clearance"] and isinstance(paper.get("body"), str):
            visible_text.append(paper["body"])
        if marks["applied"]:
            all_markings.append(marks["applied"])
        for label in marks["retention"]:
            if label not in all_retention:
                all_retention.append(label)
        if marks["legal_hold"]:
            any_hold = True
        document_iso = document["iso"] if not document["unparseable"] and not document["ambiguous"] else None
        if not marks["above_clearance"] and document_iso:
            files.append(
                {
                    "file_id": submission.replace(" ", "")[:40],
                    "filename": f"{paper['paper_id']}.txt",
                    "media_type": "text/plain",
                    "document_date": document_iso,
                    "content": paper.get("body") if isinstance(paper.get("body"), str) else "",
                }
            )
        row = {
            "paper_id": paper["paper_id"],
            "submission_id": submission,
            "version": paper.get("version") if isinstance(paper.get("version"), str) else None,
            "agenda_item_id": paper.get("agenda_item_id") if isinstance(paper.get("agenda_item_id"), str) else None,
            "purpose": cover["purpose"],
            "author_ref": paper.get("author_ref") if isinstance(paper.get("author_ref"), str) else None,
            "sponsor_ref": (paper.get("cover") or {}).get("sponsor_ref") if isinstance(paper.get("cover"), dict) else None,
            "matter_id": matter if isinstance(matter, str) else None,
            "flags": row_flags,
            "inconsistencies": inconsistent,
            "cover_complete": cover["complete"],
            "sponsor_approval_recorded": sponsor["recorded"],
            "sponsor_approval_from_text": sponsor["from_text"],
            "sponsor_approval_trusted_from_text": False,
            "marking": {
                "applied": marks["applied"],
                "from_metadata": marks["from_metadata"],
                "from_content": marks["from_content"],
            },
            "above_clearance": marks["above_clearance"],
            "legal_hold": marks["legal_hold"],
            "retention": marks["retention"],
            "body_copied": False,
            "superseded": "superseded" in row_flags,
            "duplicate": "duplicate" in row_flags,
            "late": "late" in row_flags,
        }
        paper_rows.append(row)
        by_id.setdefault(paper["paper_id"], []).append(row)

    for interest in pinned["register"].get("interests") or []:
        if not isinstance(interest, dict):
            interest_unreadable = True
            continue
        live = interest_live(interest, on)
        if live["unreadable"]:
            interest_unreadable = True
            continue
        if not live["live"]:
            continue
        supplier = interest.get("supplier_name") if isinstance(interest.get("supplier_name"), str) else ""
        person_ref = interest.get("person_ref")
        connected = person_ref in attendance or any(
            row.get("author_ref") == person_ref or row.get("sponsor_ref") == person_ref for row in paper_rows
        )
        if not connected:
            continue
        for row in paper_rows:
            source = next((paper for paper in papers if paper.get("submission_id") == row["submission_id"]), None)
            body = source.get("body") if isinstance(source, dict) and isinstance(source.get("body"), str) else ""
            matter_hit = row.get("matter_id") == interest.get("matter_id") or (
                isinstance(interest.get("matter_id"), str)
                and interest["matter_id"] == row.get("matter_id")
            )
            name_hit = bool(supplier) and affirmed(body, supplier)
            if matter_hit or name_hit:
                conflicts.append(
                    {
                        "paper_id": row["paper_id"],
                        "kind": "likely_from_register",
                        "interest_id": interest.get("interest_id"),
                        "person_ref": person_ref if isinstance(person_ref, str) else None,
                        "conflict_decided": False,
                    }
                )
                if "conflict_likely" not in row["flags"]:
                    row["flags"].append("conflict_likely")

    agenda_rows = []
    missing = []
    for item in agenda.get("items") or []:
        if not isinstance(item, dict):
            continue
        expected = item.get("expected_paper_id")
        present = [row for row in paper_rows if row["paper_id"] == expected and not row["superseded"]]
        item_flags = []
        if not present:
            item_flags.append("missing_paper")
            if isinstance(expected, str):
                missing.append(expected)
        expected_version = item.get("expected_version")
        if isinstance(expected_version, str) and present:
            if not any(row["version"] == expected_version for row in present):
                item_flags.append("expected_version_absent")
        matter = item.get("matter_id")
        outside = isinstance(matter, str) and matter not in in_remit
        if outside:
            item_flags.append("outside_terms")
        agenda_rows.append(
            {
                "item_id": item.get("item_id"),
                "purpose": item.get("purpose") if item.get("purpose") in allowed else None,
                "matter_id": matter if isinstance(matter, str) else None,
                "expected_paper_id": expected if isinstance(expected, str) else None,
                "papers": list(dict.fromkeys(row["paper_id"] for row in present)),
                "flags": item_flags,
                "outside_terms": outside,
            }
        )

    index = []
    superseded = []
    duplicates = []
    seen_current = set()
    for row in paper_rows:
        if row["superseded"]:
            superseded.append({"paper_id": row["paper_id"], "version": row["version"], "flags": ["superseded"]})
            continue
        key = (row["paper_id"], row["version"])
        if key in seen_current:
            continue
        if row["duplicate"]:
            duplicates.append({"paper_id": row["paper_id"], "version": row["version"]})
        seen_current.add(key)
        index.append(
            {
                "paper_id": row["paper_id"],
                "version": row["version"],
                "purpose": row["purpose"],
                "marking": row["marking"]["applied"],
                "sponsor_approval_recorded": row["sponsor_approval_recorded"],
                "flags": row["flags"],
                "legal_hold": row["legal_hold"],
                "retention": row["retention"],
            }
        )

    actions = carry_forward(pinned["minutes"], directory, on)
    if any(row.get("due_unparseable") for row in actions["carried"]):
        dates_unreadable = True

    agenda_review = _review(agenda, on)
    terms_review = _review(terms, on)
    sources_current = agenda_review["stale"] is False and terms_review["stale"] is False
    if agenda_review["unreadable"] or terms_review["unreadable"]:
        sources_current = False
    caller_differs = any((caller_agenda, caller_terms, caller_directory, caller_register, caller_papers))
    acknowledgements = ["pins_seen"]
    if not sources_current or caller_differs:
        acknowledgements.append("sources_seen")
    if dates_unreadable or interest_unreadable or "date_unparseable" in select_flags:
        acknowledgements.append("dates_seen")

    refs = set(attendance)
    for row in paper_rows:
        if isinstance(row.get("author_ref"), str):
            refs.add(row["author_ref"])
        if isinstance(row.get("sponsor_ref"), str):
            refs.add(row["sponsor_ref"])
    for row in actions["carried"]:
        if isinstance(row.get("owner_ref"), str):
            refs.add(row["owner_ref"])
    directory_refs = {row.get("employee_ref") for row in directory.get("people") or [] if isinstance(row, dict)}
    people = publish_count(len(refs & directory_refs), threshold)

    try:
        identifiers = identifier_counts("\n".join(visible_text), on=on) if visible_text else {
            "called": False,
            "reason": "no_visible_text",
            "output_is_anonymised": False,
            "values_stored": False,
            "redacted_text_copied": False,
        }
    except (NeighbourMissing, RuntimeError, TypeError, ValueError):
        identifiers = {
            "called": False,
            "reason": "neighbour_unavailable",
            "output_is_anonymised": False,
            "values_stored": False,
            "redacted_text_copied": False,
        }
    try:
        intake = intake_papers(files, on=on)
    except NeighbourMissing:
        intake = {
            "called": False,
            "reason": "neighbour_missing",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "content_recorded": False,
        }
    try:
        linked = conflict_links("\n".join(visible_text), pinned["suppliers"], pinned["procurements"], on=on)
    except NeighbourMissing:
        linked = {
            "called": False,
            "reason": "neighbour_missing",
            "conflict_exists": None,
            "decides_conflict": False,
        }

    outcome = "route_to_human" if distress else "draft"
    if not secretary_ok:
        outcome = "route_to_human" if distress else "needs_secretary"
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "as_of": on.isoformat(),
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "may_be_relied_on": False,
        "sources_current": sources_current,
        "meeting_id": agenda.get("meeting_id"),
        "committee_id": terms.get("committee_id"),
        "secretary_ref": secretary_ref if isinstance(secretary_ref, str) else None,
        "secretary_on_directory": secretary_ok,
        "agenda": agenda_rows,
        "pack_index": index,
        "superseded": superseded,
        "missing_papers": missing,
        "duplicates": duplicates,
        "action_log": actions,
        "conflicts": conflicts,
        "papers": paper_rows,
        "select_flags": select_flags,
        "caller_agenda_diff": caller_agenda,
        "caller_terms_diff": caller_terms,
        "caller_directory_diff": caller_directory,
        "caller_register_diff": caller_register,
        "caller_papers_diff": caller_papers,
        "prompt_injection": {"followed": False, "signals": signals},
        "distress": {"routed": distress, "cue_copied": False},
        "marking": {
            "applied": higher_marking(all_markings),
            "labels_kept": all_markings,
        },
        "legal_hold": any_hold,
        "retention": all_retention,
        "masking": {
            "counts": mask_counts,
            "values_stored": False,
            "values_copied": False,
            "described_as_anonymised": False,
            "masked_text_included": False,
        },
        "people_count": people,
        "uk_identifiers": identifiers,
        "intake": intake,
        "experiment_70": linked,
        "interest_date_unreadable": interest_unreadable,
        "uk_context": uk_context(),
        "required_acknowledgements": acknowledgements,
        "ignored_request_fields": ignored,
        "ignored_instructions": True,
    }
    _force(result)
    result["content_hash"] = _hash(result)
    return result


def _named_secretary(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_sources()["directory"]
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("secretary_ref"):
        return None, "not_the_named_secretary"
    row = person(pinned, approver_ref)
    if row is None or row.get("guest") is True or row.get("role") != "company_secretary":
        return None, "approver_not_directory_secretary"
    return row, None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named secretary has seen a human route. Nothing is staged."""

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
    _row, reason = _named_secretary(result, directory, approval.get("approver_ref"))
    if reason:
        updated["blocked_reason"] = reason
        updated["content_hash"] = _hash(updated)
        return updated
    updated["route_seen"] = True
    updated["distress"] = {"routed": True, "cue_copied": False, "seen": True}
    updated["content_hash"] = _hash(updated)
    return updated


def record_secretary_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Stage the draft only when the named company secretary approves this content hash."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        return updated
    if approval.get("decision") in {"circulate", "publish", "file", "send", "approve-minutes"}:
        updated["blocked_reason"] = "consequential_action_is_not_this_step"
        return updated
    if approval.get("item") != "board-pack" or approval.get("decision") != "approve-draft":
        updated["blocked_reason"] = "wrong_item"
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        return updated
    if approval.get("content_hash") != result.get("content_hash") or approval.get("content_hash") != _hash(result):
        updated["blocked_reason"] = "content_hash_mismatch"
        return updated
    if approval.get("meeting_id") != result.get("meeting_id"):
        updated["blocked_reason"] = "meeting_mismatch"
        return updated
    reason = _ack(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        return updated
    secretary, role_reason = _named_secretary(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        return updated
    updated["human_approval"] = {
        "item": "board-pack",
        "approver_ref": secretary["employee_ref"],
        "content_hash": result["content_hash"],
        "recorded": True,
        "minutes_approved": False,
        "decisions_recorded": False,
    }
    updated["staged"] = True
    updated["route_seen"] = result.get("route_seen") is True
    _force(updated)
    holds = []
    retention = []
    for row in result.get("papers") or []:
        if row.get("legal_hold") and row.get("paper_id") not in holds:
            holds.append(row.get("paper_id"))
        for label in row.get("retention") or []:
            if label not in retention:
                retention.append(label)
    stored = {
        "meeting_id": result.get("meeting_id"),
        "content_hash": result["content_hash"],
        "secretary_ref": secretary["employee_ref"],
        "pack_index": deepcopy(result.get("pack_index")),
        "marking": deepcopy(result.get("marking")),
        "legal_hold": result.get("legal_hold"),
        "legal_hold_papers": holds,
        "retention": retention,
        "circulated": False,
        "published": False,
        "filed": False,
        "sent": False,
        "minutes_approved": False,
        "decisions_recorded": False,
        "production_written": False,
        "store": "synthetic",
    }
    _STORE[f"{result.get('meeting_id')}:{result['content_hash']}"] = stored
    updated["staging_store"] = "synthetic"
    updated["content_hash"] = result["content_hash"]
    return updated


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble a synthetic board-pack draft.")
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
