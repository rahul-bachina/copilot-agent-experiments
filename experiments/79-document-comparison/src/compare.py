"""Compare two synthetic document versions. Do not edit either document.

The named reader confirms which two versions are being compared, and which
one is the baseline, on a separate object bound to the agent-held copy.
The reader owns the interpretation. The agent does not edit, approve,
publish, or send, and it does not give legal advice.

Autonomy is A0. A sentence inside either document is not the confirmation.
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
    from align import align
    from cues import category_hit, sensitive_categories
    from dates import as_date, parse_date, with_question_date
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import empty_mask, mask_text, suppress_small_counts
    from material import CHECKS, compare_texts, hidden_or_tracked, visible_text
    from siblings import identifier_counts, intake_versions, neighbours
    from sources import uk_context
else:
    from .align import align
    from .cues import category_hit, sensitive_categories
    from .dates import as_date, parse_date, with_question_date
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import empty_mask, mask_text, suppress_small_counts
    from .material import CHECKS, compare_texts, hidden_or_tracked, visible_text
    from .siblings import identifier_counts, intake_versions, neighbours
    from .sources import uk_context

LABEL = (
    "DRAFT COMPARISON FOR THE NAMED READER. NOT LEGAL ADVICE. "
    "THE READER OWNS THE INTERPRETATION."
)
CATALOGUE_ID = "O004"
EXPERIMENT_ID = "exp-79-document-comparison"
ROOT = Path(__file__).resolve().parents[1]
KINDS = frozenset({"contract", "internal_policy", "guidance"})
ROLES = frozenset({"document_owner", "reader"})
COMPARISON_ID = re.compile(r"^CMP-\d{4}$")
VERSION_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
_HELD: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "versions_confirmed",
    "interpretation_acknowledged",
    "approved",
    "document_approved",
    "published",
    "sent",
    "edited",
    "role",
    "clearance",
    "baseline_confirmed",
    "no_material_change",
    "marked_acceptable",
    "legal_advice",
)


class CompareForbidden(RuntimeError):
    """The agent does not edit, approve, publish, send, or advise."""

    __test__ = False


class NotSynthetic(ValueError):
    """The request was not marked synthetic."""


def edit_document(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not edit a document.")


def approve_document(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not approve a document.")


def publish_document(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not publish a document.")


def send_document(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not send a document.")


def give_legal_advice(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not give legal advice.")


def reset_held() -> None:
    _HELD.clear()


def held_record(comparison_id: object) -> dict | None:
    if not isinstance(comparison_id, str):
        return None
    row = _HELD.get(comparison_id)
    if not isinstance(row, dict):
        return None
    return {
        "comparison_id": comparison_id,
        "content_hash": row.get("content_hash"),
        "document_hashes": dict(row.get("document_hashes") or {}),
    }


def pinned_directory() -> dict:
    return json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _projection(result: dict) -> dict:
    return {
        "comparison_id": result.get("comparison_id"),
        "reader_ref": result.get("reader_ref"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "baseline_version_id": result.get("baseline_version_id"),
        "other_version_id": result.get("other_version_id"),
        "provisional_orientation": result.get("provisional_orientation"),
        "versions_confirmed": result.get("versions_confirmed") is True,
        "interpretation_acknowledged": result.get("interpretation_acknowledged") is True,
        "route_seen": result.get("route_seen") is True,
        "document_hashes": result.get("document_hashes"),
        "rows": result.get("rows"),
        "class_counts": result.get("class_counts"),
        "material": result.get("material"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "legal_hold_unparseable": result.get("legal_hold_unparseable"),
        "retention": result.get("retention"),
        "retention_unparseable": result.get("retention_unparseable"),
        "prompt_injection": result.get("prompt_injection"),
        "suppression": result.get("suppression"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "duplicate_conflicts": result.get("duplicate_conflicts"),
        "low_confidence_count": result.get("low_confidence_count"),
        "hidden_or_tracked": result.get("hidden_or_tracked"),
        "dates": result.get("dates"),
        "parties": result.get("parties"),
        "bodies_withheld": result.get("bodies_withheld"),
        "distress": result.get("distress"),
        "leading_criteria": result.get("leading_criteria"),
        "unparseable_clauses": result.get("unparseable_clauses"),
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _force(result: dict) -> None:
    result["document_edited"] = False
    result["document_approved"] = False
    result["published"] = False
    result["sent"] = False
    result["legal_advice"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["caller_directory_applied"] = False
    result["caller_taxonomy_applied"] = False
    result["coerced"] = False
    result["described_as_anonymised"] = False
    result["marked_acceptable"] = False
    result["experiment_38_compare_called"] = False
    result["may_be_relied_on"] = False
    result["production_written"] = False
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


def _question_date(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("as_of must be a calendar date.")
    reading = parse_date(value)
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


def _store(result: dict, document_hashes: dict[str, str]) -> None:
    comparison_id = result.get("comparison_id")
    if not isinstance(comparison_id, str):
        return
    result["content_hash"] = _hash(result)
    _HELD[comparison_id] = {
        "content_hash": result["content_hash"],
        "projection": _projection(result),
        "document_hashes": dict(document_hashes),
    }


def _remember(result: dict) -> None:
    """Hash the returned object. Replace the held copy only when the step succeeded."""

    comparison_id = result.get("comparison_id")
    held = _HELD.get(comparison_id) if isinstance(comparison_id, str) else None
    hashes = dict((held or {}).get("document_hashes") or result.get("document_hashes") or {})
    result["content_hash"] = _hash(result)
    if result.get("blocked_reason") or not isinstance(comparison_id, str):
        return
    _HELD[comparison_id] = {
        "content_hash": result["content_hash"],
        "projection": _projection(result),
        "document_hashes": hashes,
    }


def prepare_comparison(request: dict, *, as_of: str, directory: dict | None = None) -> dict:
    """Return a draft comparison. Versions are not confirmed. Nothing is edited."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object.")
    if request.get("synthetic") is not True:
        raise NotSynthetic("The request was not marked synthetic.")
    question = _question_date(as_of)
    stripped, ignored = _strip(request)
    pinned = pinned_directory()
    caller_directory = stripped.get("directory")
    caller_taxonomy = stripped.get("taxonomy", stripped.get("clause_taxonomy"))
    versions = stripped.get("versions")
    comparison_id = stripped.get("comparison_id")
    reader_ref = stripped.get("reader_ref")
    kind = stripped.get("document_kind")
    suggested = stripped.get("suggested_baseline_id")

    result = _shell(
        comparison_id=comparison_id if isinstance(comparison_id, str) else None,
        reader_ref=reader_ref if isinstance(reader_ref, str) else None,
        as_of=question.isoformat(),
        ignored=ignored,
    )
    result["caller_directory_differs"] = caller_directory is not None and caller_directory != pinned
    result["caller_taxonomy_supplied"] = caller_taxonomy is not None
    result["document_kind"] = kind if isinstance(kind, str) and kind in KINDS else "unrecognised"
    result["document_kind_recognised"] = result["document_kind"] != "unrecognised"
    if not isinstance(kind, str) or kind not in KINDS:
        result["flags"].append("document_kind_unrecognised")

    reader = _person(pinned, reader_ref)
    usable = (
        reader is not None
        and reader.get("active") is True
        and reader.get("guest") is not True
        and reader.get("role") in ROLES
    )
    result["reader_on_directory"] = usable
    result["reader_role"] = reader.get("role") if usable else None
    result["reader_clearance"] = reader.get("clearance") if usable else None
    if not usable:
        result["flags"].append("reader_not_on_directory")

    if not isinstance(comparison_id, str) or not COMPARISON_ID.fullmatch(comparison_id):
        result["flags"].append("comparison_id_unusable")
        result["outcome"] = "needs_human"
        result["coerced"] = False
        _finish(result, question, [], {})
        return result

    if not isinstance(versions, list) or len(versions) != 2:
        result["flags"].append("version_count")
        result["outcome"] = "needs_human"
        result["version_count"] = len(versions) if isinstance(versions, list) else None
        _finish(result, question, [], {})
        return result

    prepared = []
    for version in versions:
        if not isinstance(version, dict):
            result["flags"].append("version_not_object")
            result["outcome"] = "needs_human"
            _finish(result, question, [], {})
            return result
        version_id = version.get("version_id")
        if not isinstance(version_id, str) or not VERSION_ID.fullmatch(version_id):
            result["flags"].append("version_id_unusable")
            result["outcome"] = "needs_human"
            _finish(result, question, [], {})
            return result
        prepared.append(_prepare_version(version, question))

    ids = [item["version_id"] for item in prepared]
    if len(set(ids)) != 2:
        result["flags"].append("duplicate_version_id")
        result["outcome"] = "needs_human"
        _finish(result, question, prepared, {})
        return result

    if not isinstance(suggested, str) or suggested not in ids:
        result["flags"].append("baseline_not_usable")
        result["outcome"] = "needs_human"
        result["provisional_orientation"] = None
        _apply_version_facts(result, prepared, reader.get("clearance") if usable else None)
        _finish(result, question, prepared, _document_hashes(prepared))
        return result

    other_id = ids[0] if ids[1] == suggested else ids[1]
    by_id = {item["version_id"]: item for item in prepared}
    baseline = by_id[suggested]
    other = by_id[other_id]
    result["provisional_orientation"] = suggested
    result["baseline_version_id"] = None
    result["other_version_id"] = None
    result["orientation_is_not_confirmation"] = True

    _apply_version_facts(result, prepared, reader.get("clearance") if usable else None)
    _scan_note(result, stripped.get("note"))
    withhold = result["bodies_withheld"] is True
    sensitive = bool(result["distress"]["categories"])
    rows = align(baseline["align_clauses"], other["align_clauses"])
    _annotate(rows, baseline, other, question, withhold=withhold, sensitive_text=result["distress"]["source_seen"])
    result["rows"] = rows
    result["class_counts"] = _counts(rows)
    result["class_count_total"] = len(rows)
    result["duplicate_conflicts"] = sum(1 for row in rows if row["change_class"] == "duplicate_conflict")
    result["low_confidence_count"] = sum(1 for row in rows if row["low_confidence"])
    result["hidden_or_tracked"] = any(item["hidden_or_tracked"] for item in prepared) or any(
        "hidden_or_tracked" in (row.get("material") or []) for row in rows
    )
    _material_statement(result)
    _acknowledgements(result)
    if sensitive:
        result["outcome"] = "route_to_human"
        result["routine"] = False
    elif result["flags"]:
        result["outcome"] = "needs_confirmation"
        result["routine"] = True
    else:
        result["outcome"] = "needs_confirmation"
        result["routine"] = True
    document_hashes = _document_hashes(prepared)
    result["document_hashes"] = document_hashes
    _finish(result, question, prepared, document_hashes)
    return result


def _shell(*, comparison_id, reader_ref, as_of, ignored) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A0",
        "comparison_id": comparison_id,
        "reader_ref": reader_ref,
        "as_of": as_of,
        "outcome": "needs_human",
        "routine": False,
        "human_approval": None,
        "versions_confirmed": False,
        "interpretation_acknowledged": False,
        "route_seen": False,
        "baseline_version_id": None,
        "other_version_id": None,
        "provisional_orientation": None,
        "orientation_is_not_confirmation": True,
        "rows": [],
        "class_counts": {},
        "class_count_total": 0,
        "flags": [],
        "ignored_request_keys": ignored,
        "document_hashes": {},
        "marking": {"applied": None, "from_metadata": [], "from_content": [], "self_declared_clearance_ignored": True},
        "legal_hold": False,
        "legal_hold_unparseable": False,
        "retention": [],
        "retention_unparseable": False,
        "bodies_withheld": False,
        "dates": [],
        "parties": {"compared": False, "differ": False, "unparseable": False, "applied_caller_list": False},
        "distress": {"routed": False, "categories": [], "cue_copied": False, "source_seen": False},
        "leading_criteria": {"detected": False, "applied": False},
        "prompt_injection": {"detected": False, "signals": [], "followed": False},
        "suppression": {
            "applied": False,
            "threshold": 5,
            "published_values": None,
            "published_difference": None,
            "published_percentage": None,
            "published_count": None,
            "headcount": None,
            "delta": None,
        },
        "duplicate_conflicts": 0,
        "low_confidence_count": 0,
        "hidden_or_tracked": False,
        "unparseable_clauses": [],
        "required_acknowledgements": [],
        "material": {
            "statement": None,
            "checks_performed": list(CHECKS),
            "checks_with_findings": [],
            "checks_incomplete": [],
            "findings": [],
        },
        "intake": {"called": False},
        "uk_identifiers": {"called": False, "output_is_anonymised": False, "values_stored": False},
        "masking": empty_mask(),
        "uk_context": uk_context(),
        "sources_current": True,
        "blocked_reason": None,
    }


def _prepare_version(version: dict, question: date) -> dict:
    version_id = version["version_id"]
    clauses_in = version.get("clauses")
    align_clauses = []
    unparseable = []
    texts = []
    if not isinstance(clauses_in, list):
        unparseable.append({"version_id": version_id, "reason": "clauses_not_a_list", "coerced": False})
        clauses_in = []
    normalised_rows = []
    for index, clause in enumerate(clauses_in):
        if not isinstance(clause, dict):
            unparseable.append({"version_id": version_id, "index": index, "reason": "clause_not_object", "coerced": False})
            continue
        body, bad, conflict = _body(clause)
        if bad or conflict:
            unparseable.append(
                {
                    "version_id": version_id,
                    "index": index,
                    "clause_id": clause.get("clause_id") if isinstance(clause.get("clause_id"), str) else None,
                    "reason": "conflicting_clause_fields" if conflict else "unparseable_clause_text",
                    "coerced": False,
                }
            )
            continue
        texts.append(body)
        normalised_rows.append((index, clause, body))
    duplicate_ids = _duplicate_keys(normalised_rows)
    for index, clause, body in normalised_rows:
        clause_id = clause.get("clause_id") if isinstance(clause.get("clause_id"), str) else ""
        number = clause.get("number") if isinstance(clause.get("number"), str) else ""
        heading = clause.get("heading") if isinstance(clause.get("heading"), str) else ""
        key = clause_id or (f"number:{number}" if number else "")
        align_clauses.append(
            {
                "clause_id": clause_id,
                "number": number,
                "heading": heading,
                "text": visible_text(body),
                "raw": body,
                "duplicate_conflict": key in duplicate_ids,
                "citation": {
                    "version_id": version_id,
                    "page": 1,
                    "paragraph": index + 1,
                    "line_start": 1,
                    "line_end": 1,
                },
            }
        )
    cover = version.get("cover") if isinstance(version.get("cover"), str) else ""
    blob = "\n".join([cover, *[item["raw"] for item in align_clauses]])
    meta_labels, meta_bad = metadata_markings(version.get("protective_marking"))
    content_labels = content_markings(cover + "\n" + blob)
    retention, retention_bad = retention_labels(version.get("retention"), blob)
    held, hold_bad = legal_hold(version.get("legal_hold"), blob)
    return {
        "version_id": version_id,
        "title": version.get("title") if isinstance(version.get("title"), str) else "",
        "align_clauses": align_clauses,
        "unparseable_clauses": unparseable,
        "blob": blob,
        "cover": cover,
        "meta_labels": meta_labels,
        "meta_bad": meta_bad,
        "content_labels": content_labels,
        "retention": retention,
        "retention_unparseable": retention_bad,
        "legal_hold": held,
        "legal_hold_unparseable": hold_bad,
        "hidden_or_tracked": hidden_or_tracked(blob),
        "dates": _version_dates(version, question),
        "parties": _party_list(version.get("parties")),
        "effective_raw": version.get("effective_date"),
        "review_raw": version.get("review_date"),
    }


def _body(clause: dict) -> tuple[str, bool, bool]:
    text = clause.get("text", None)
    lines = clause.get("lines", None)
    if lines is None and "text" not in clause:
        return "", True, False
    joined = None
    if lines is not None:
        if not isinstance(lines, list) or not lines:
            return "", True, False
        parts = []
        for line in lines:
            if not isinstance(line, dict) or not isinstance(line.get("text"), str):
                return "", True, False
            parts.append(line["text"])
        joined = " ".join(part.strip() for part in parts if part.strip())
    if text is not None and not isinstance(text, str):
        return "", True, False
    if joined is not None and isinstance(text, str) and text.strip():
        if neighbours()["normalise"](text) != neighbours()["normalise"](joined):
            return "", False, True
        return joined, False, False
    if joined is not None:
        return joined, False, False
    if isinstance(text, str):
        return text, False, False
    return "", True, False


def _duplicate_keys(rows: list[tuple[int, dict, str]]) -> set[str]:
    grouped: dict[str, set[str]] = {}
    for _index, clause, body in rows:
        clause_id = clause.get("clause_id") if isinstance(clause.get("clause_id"), str) else ""
        number = clause.get("number") if isinstance(clause.get("number"), str) else ""
        key = clause_id or (f"number:{number}" if number else "")
        if not key:
            continue
        grouped.setdefault(key, set()).add(neighbours()["normalise"](visible_text(body)))
    return {key for key, bodies in grouped.items() if len(bodies) > 1}


def _version_dates(version: dict, question: date) -> list[dict]:
    rows = []
    for field in ("effective_date", "review_date", "retention_trigger"):
        if field not in version:
            continue
        reading = with_question_date(parse_date(version.get(field)), question)
        stale = False
        parsed = as_date(reading)
        if field == "review_date" and parsed is not None and parsed <= question:
            stale = True
        # A review date after the question date is still inside its review window.
        # An effective date after the question date is not yet in force.
        future = reading.get("future") is True and field != "review_date"
        reason = reading.get("reason")
        if stale:
            reason = "stale"
        elif field == "review_date" and reading.get("future") is True:
            reason = None
        rows.append(
            {
                "field": field,
                "version_id": version.get("version_id"),
                "iso": reading.get("iso"),
                "unparseable": reading.get("unparseable") is True,
                "ambiguous": reading.get("ambiguous") is True,
                "future": future,
                "stale": stale,
                "reason": reason,
                "coerced": False,
            }
        )
    return rows


def _party_list(value: object) -> dict:
    if value is None:
        return {"present": False, "names": [], "unparseable": False}
    if not isinstance(value, list):
        return {"present": True, "names": [], "unparseable": True}
    names = []
    bad = False
    for item in value:
        if isinstance(item, str) and item.strip():
            names.append(item.strip())
        elif item not in (None, ""):
            bad = True
    return {"present": True, "names": names, "unparseable": bad}


def _document_hashes(prepared: list[dict]) -> dict[str, str]:
    hashes = {}
    for item in prepared:
        payload = [
            {
                "clause_id": clause.get("clause_id"),
                "number": clause.get("number"),
                "heading": clause.get("heading"),
                "text": clause.get("raw"),
            }
            for clause in item["align_clauses"]
        ]
        hashes[item["version_id"]] = _digest({"version_id": item["version_id"], "clauses": payload})
    return hashes


def _apply_version_facts(result: dict, prepared: list[dict], ceiling: object) -> None:
    labels = []
    content = []
    retention: list[str] = []
    hold = False
    hold_bad = False
    retention_bad = False
    meta_bad = False
    for item in prepared:
        labels.extend(item["meta_labels"])
        content.extend(item["content_labels"])
        for label in item["retention"]:
            if label not in retention:
                retention.append(label)
        hold = hold or item["legal_hold"]
        hold_bad = hold_bad or item["legal_hold_unparseable"]
        retention_bad = retention_bad or item["retention_unparseable"]
        meta_bad = meta_bad or item["meta_bad"]
        result["dates"].extend(item["dates"])
        result["unparseable_clauses"].extend(item["unparseable_clauses"])
    applied = higher_marking(labels + content)
    result["marking"] = {
        "applied": applied,
        "from_metadata": list(dict.fromkeys(labels)),
        "from_content": list(dict.fromkeys(content)),
        "metadata_unparseable": meta_bad,
        "self_declared_clearance_ignored": True,
    }
    result["legal_hold"] = hold
    result["legal_hold_unparseable"] = hold_bad
    result["retention"] = retention
    result["retention_unparseable"] = retention_bad
    result["bodies_withheld"] = above_ceiling(applied, ceiling if isinstance(ceiling, str) else None)
    if any(row.get("stale") or row.get("unparseable") or row.get("ambiguous") or row.get("future") for row in result["dates"]):
        result["sources_current"] = False
        result["flags"].append("dates_need_a_person")
    party_rows = [item["parties"] for item in prepared]
    if any(row["unparseable"] for row in party_rows):
        result["parties"] = {"compared": False, "differ": False, "unparseable": True, "applied_caller_list": False}
        result["flags"].append("parties_unparseable")
    elif all(row["present"] for row in party_rows):
        differ = party_rows[0]["names"] != party_rows[1]["names"]
        result["parties"] = {"compared": True, "differ": differ, "unparseable": False, "applied_caller_list": False}
        if differ:
            result["flags"].append("parties_differ")
    blob = "\n".join(item["blob"] for item in prepared)
    categories = []
    signals = []
    leading = False
    for item in prepared:
        for clause in item["align_clauses"]:
            raw = "\n".join(part for part in (clause.get("heading") or "", clause["raw"]) if part)
            for category in sensitive_categories(raw):
                if category not in categories:
                    categories.append(category)
            if category_hit(raw, "embedded_instruction") and "embedded_instruction" not in signals:
                signals.append("embedded_instruction")
            if category_hit(raw, "forged_confirmation") and "forged_confirmation" not in signals:
                signals.append("forged_confirmation")
            if category_hit(raw, "leading_criterion"):
                leading = True
    result["distress"] = {
        "routed": bool(categories),
        "categories": categories,
        "cue_copied": False,
        "source_seen": bool(categories),
    }
    result["prompt_injection"] = {"detected": bool(signals), "signals": signals, "followed": False}
    result["leading_criteria"] = {"detected": leading, "applied": False}
    if leading:
        result["flags"].append("leading_criterion")
    if signals:
        result["flags"].append("embedded_instruction")
    _ = blob


def _scan_note(result: dict, note: object) -> None:
    if not isinstance(note, str) or not note:
        return
    if category_hit(note, "embedded_instruction"):
        result["prompt_injection"]["detected"] = True
        if "embedded_instruction" not in result["prompt_injection"]["signals"]:
            result["prompt_injection"]["signals"].append("embedded_instruction")
    if category_hit(note, "forged_confirmation"):
        result["prompt_injection"]["detected"] = True
        if "forged_confirmation" not in result["prompt_injection"]["signals"]:
            result["prompt_injection"]["signals"].append("forged_confirmation")
    result["prompt_injection"]["followed"] = False


def _annotate(rows, baseline, other, question, *, withhold: bool, sensitive_text: bool) -> None:
    base_by_index = {clause["citation"]["paragraph"] - 1: clause for clause in baseline["align_clauses"]}
    other_by_index = {clause["citation"]["paragraph"] - 1: clause for clause in other["align_clauses"]}
    base_doc = _span_document(baseline)
    other_doc = _span_document(other)
    for row in rows:
        left = _original(row.get("baseline"), base_by_index)
        right = _original(row.get("other"), other_by_index)
        if left is not None and right is not None and row["change_class"] not in {"duplicate_conflict"}:
            diff = compare_texts(left, right, question=question)
            _apply_diff(row, diff)
        elif row["change_class"] in {"added", "deleted"}:
            present = right if row["change_class"] == "added" else left
            absent = ""
            if present is not None:
                diff = compare_texts(present if row["change_class"] == "deleted" else absent,
                                     absent if row["change_class"] == "deleted" else present,
                                     question=question)
                if row["change_class"] == "deleted" and diff.get("left_carve_out"):
                    diff["flags"] = list(dict.fromkeys([*diff["flags"], "carve_outs"]))
                _apply_diff(row, diff)
        _publish_side(row, "baseline", base_by_index, base_doc, withhold, sensitive_text, question)
        _publish_side(row, "other", other_by_index, other_doc, withhold, sensitive_text, question)


def _original(citation, index) -> str | None:
    if citation is None:
        return None
    if isinstance(citation, list):
        parts = []
        for item in citation:
            clause = index.get(item.get("index"))
            if clause is None:
                return None
            parts.append(clause["raw"])
        return " ".join(parts)
    clause = index.get(citation.get("index"))
    if clause is None:
        return None
    return clause["raw"]


def _apply_diff(row: dict, diff: dict) -> None:
    flags = list(diff.get("flags") or [])
    existing = list(row.get("material") or [])
    for flag in flags:
        if flag not in existing:
            existing.append(flag)
    row["material"] = existing
    row["checks_incomplete"] = list(diff.get("incomplete") or [])
    substantive_flags = [flag for flag in flags if flag not in {"hidden_or_tracked"}]
    if substantive_flags and row["change_class"] in {"unchanged", "renumbered", "reformatted", "moved", "changed", "low_confidence"}:
        if (row.get("score") or 0) >= 0.8 or row["change_class"] in {"unchanged", "renumbered", "reformatted", "moved"}:
            row["hidden_inside_reformat"] = True
        row["also_renumbered"] = row["change_class"] == "renumbered" or row.get("also_renumbered") is True
        if row["change_class"] != "low_confidence":
            row["change_class"] = "changed"
        row["substantive"] = True
    elif substantive_flags and row["change_class"] in {"split", "merged"}:
        row["substantive"] = True
    if "hidden_or_tracked" in flags and row["change_class"] == "unchanged":
        row["hidden_inside_reformat"] = False
    if row["low_confidence"]:
        if "alignment_confidence" not in row["material"]:
            row["material"].append("alignment_confidence")
    row["removed_carve_out"] = diff.get("removed_carve_out") is True
    row["chosen_text"] = None


def _publish_side(row, side, index, document, withhold, sensitive_text, question) -> None:
    citation = row.get(side)
    if isinstance(citation, list):
        for item in citation:
            _publish_one(item, index, document, withhold, sensitive_text, question)
        return
    if isinstance(citation, dict):
        _publish_one(citation, index, document, withhold, sensitive_text, question)


def _publish_one(citation, index, document, withhold, sensitive_text, question) -> None:
    clause = index.get(citation.get("index"))
    raw = clause["raw"] if clause else ""
    sensitive = sensitive_text and bool(sensitive_categories(raw))
    span = neighbours()["resolve_span"](
        document,
        citation.get("page") or 1,
        citation.get("paragraph") or 1,
        citation.get("line_start") or 1,
        citation.get("line_end") or 1,
    )
    citation["span_supported"] = bool(span) and neighbours()["normalise"](span or "") == neighbours()["normalise"](raw)
    if withhold:
        citation["excerpt"] = "[withheld: above clearance]"
        citation["heading"] = "[withheld: above clearance]"
        citation["small_number_suppressed"] = False
        return
    if sensitive or sensitive_categories(str(citation.get("heading") or "")):
        citation["excerpt"] = "[withheld: routed to a person]"
        citation["heading"] = "[withheld: routed to a person]"
        citation["small_number_suppressed"] = False
        return
    try:
        identified = identifier_counts(raw, on=question)
        masked_source = identified.get("masked") if isinstance(identified.get("masked"), str) else raw
    except Exception:  # noqa: BLE001 — a neighbour failure must not publish the raw identifier
        masked_source = raw
    masked, _report = mask_text(masked_source)
    suppressed, report = suppress_small_counts(masked)
    citation["excerpt"] = suppressed
    citation["small_number_suppressed"] = report["applied"]


def _span_document(version: dict) -> dict:
    paragraphs = []
    for clause in version["align_clauses"]:
        paragraphs.append(
            {
                "paragraph": clause["citation"]["paragraph"],
                "lines": [{"line": 1, "text": clause["raw"]}],
            }
        )
    return {"document_id": version["version_id"], "pages": [{"page": 1, "paragraphs": paragraphs}]}


def _counts(rows: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["change_class"]] = counts.get(row["change_class"], 0) + 1
    return counts


def _material_statement(result: dict) -> None:
    findings: list[str] = []
    incomplete: list[str] = []
    for row in result["rows"]:
        for flag in row.get("material") or []:
            if flag not in findings:
                findings.append(flag)
        for item in row.get("checks_incomplete") or []:
            if item not in incomplete:
                incomplete.append(item)
    if result["hidden_or_tracked"] and "hidden_or_tracked" not in findings:
        findings.append("hidden_or_tracked")
    if result["duplicate_conflicts"] and "duplicates" not in findings:
        findings.append("duplicates")
    if result["low_confidence_count"] and "alignment_confidence" not in findings:
        findings.append("alignment_confidence")
    if result["parties"].get("differ") and "parties" not in findings:
        findings.append("parties")
    if result["parties"].get("unparseable") and "parties" not in incomplete:
        incomplete.append("parties")
    if result["bodies_withheld"] and "bodies_withheld" not in incomplete:
        incomplete.append("bodies_withheld")
    if result["unparseable_clauses"] and "clauses" not in incomplete:
        incomplete.append("clauses")
    for row in result["dates"]:
        if row.get("unparseable") or row.get("ambiguous") or row.get("future") or row.get("stale"):
            if "dates" not in incomplete and "dates" not in findings:
                findings.append("dates")
    suppressed = any(
        (cite or {}).get("small_number_suppressed")
        for row in result["rows"]
        for cite in _citations(row)
    )
    result["suppression"]["applied"] = suppressed
    if suppressed and "people_count_withheld" not in findings:
        findings.append("people_count_withheld")
    clean = not findings and not incomplete and not result["distress"]["routed"]
    statement = "no material change" if clean else None
    result["material"] = {
        "statement": statement,
        "checks_performed": list(CHECKS),
        "checks_with_findings": findings,
        "checks_incomplete": incomplete,
        "findings": findings,
    }
    if statement == "no material change" and result["material"]["checks_performed"] != list(CHECKS):
        result["material"]["statement"] = None


def _citations(row: dict) -> list[dict]:
    found = []
    for side in ("baseline", "other"):
        citation = row.get(side)
        if isinstance(citation, list):
            found.extend(item for item in citation if isinstance(item, dict))
        elif isinstance(citation, dict):
            found.append(citation)
    return found


def _acknowledgements(result: dict) -> None:
    required = ["versions_seen", "pins_seen"]
    if any(row.get("stale") or row.get("unparseable") or row.get("ambiguous") or row.get("future") for row in result["dates"]):
        required.append("dates_seen")
    if result["sources_current"] is False:
        if "sources_seen" not in required:
            required.append("sources_seen")
    if result["marking"]["applied"]:
        required.append("markings_seen")
    if result["material"]["findings"] or result["low_confidence_count"] or result["hidden_or_tracked"]:
        required.append("material_seen")
    result["required_acknowledgements"] = required


def _finish(result: dict, question: date, prepared: list[dict], document_hashes: dict) -> None:
    files = []
    mask_counts = empty_mask()
    identifier = {"called": False, "count": 0, "types": [], "output_is_anonymised": False, "values_stored": False, "redacted_text_copied": False}
    blob_parts = []
    for item in prepared:
        if not isinstance(item, dict) or "blob" not in item:
            continue
        blob_parts.append(item["blob"])
        document_date = item.get("effective_raw") if isinstance(item.get("effective_raw"), str) else None
        files.append(
            {
                "file_id": item["version_id"],
                "filename": f"{item['version_id']}.txt",
                "media_type": "text/plain",
                "document_date": document_date,
                "content": item["blob"],
            }
        )
    blob = "\n".join(blob_parts)
    if blob and not result["bodies_withheld"]:
        try:
            identifier = identifier_counts(blob, on=question)
        except Exception as exc:  # noqa: BLE001 — a neighbour failure is a flag, not a guessed count
            identifier = {"called": False, "error": type(exc).__name__, "values_stored": False, "output_is_anonymised": False}
        masked, mask_counts = mask_text(blob)
        _ = masked
    if files and not result["bodies_withheld"]:
        try:
            result["intake"] = intake_versions(files, on=question)
        except Exception as exc:  # noqa: BLE001
            result["intake"] = {"called": False, "error": type(exc).__name__, "content_recorded": False, "files_confirmed": False}
    else:
        result["intake"] = {
            "called": False,
            "reason": "withheld" if result["bodies_withheld"] else "no_files",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "content_recorded": False,
        }
    result["uk_identifiers"] = {
        "called": identifier.get("called") is True,
        "count": identifier.get("count", 0) if identifier.get("called") else 0,
        "types": identifier.get("types") or [],
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
    }
    result["masking"] = mask_counts
    result["experiment_12_called"] = result["intake"].get("called") is True
    result["experiment_08_called"] = result["uk_identifiers"]["called"] is True
    result["experiment_33_called"] = True
    result["experiment_29_called"] = True
    _force(result)
    if result.get("class_counts"):
        if sum(result["class_counts"].values()) != result["class_count_total"]:
            result["flags"].append("class_counts_do_not_add_up")
    _store(result, document_hashes or result.get("document_hashes") or {})


def _named_reader(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_directory()
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("reader_ref"):
        return None, "not_the_named_reader"
    person = _person(pinned, approver_ref)
    if person is None or person.get("active") is not True or person.get("guest") is True or person.get("role") not in ROLES:
        return None, "approver_not_directory_reader"
    if result.get("reader_on_directory") is not True:
        return None, "approver_not_directory_reader"
    return person, None


def _bound(result: dict, approval: dict) -> str | None:
    comparison_id = result.get("comparison_id")
    held = _HELD.get(comparison_id) if isinstance(comparison_id, str) else None
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


def _ack(result: dict, approval: dict, extra: tuple[str, ...] = ()) -> str | None:
    for key in list(result.get("required_acknowledgements") or []) + list(extra):
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named reader has seen a human route. Nothing is edited."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if approval.get("item") != "route-seen" or approval.get("decision") != "seen":
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    reason = _bound(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        updated["route_seen"] = False
        _remember(updated)
        return updated
    _person_row, role_reason = _named_reader(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    if approval.get("comparison_id") != result.get("comparison_id"):
        updated["blocked_reason"] = "comparison_mismatch"
        _remember(updated)
        return updated
    updated["route_seen"] = True
    updated["distress"] = {
        "routed": True,
        "categories": list((result.get("distress") or {}).get("categories") or []),
        "cue_copied": False,
        "source_seen": True,
        "seen": True,
    }
    updated["blocked_reason"] = None
    _force(updated)
    _remember(updated)
    return updated


def confirm_versions(result: dict, directory: dict, confirmation: dict) -> dict:
    """Confirm the two held versions and which one is the baseline. Do not edit them."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["versions_confirmed"] = False
    updated["document_approved"] = False
    if not isinstance(confirmation, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if confirmation.get("item") != "version-pair" or confirmation.get("decision") != "confirm-versions":
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        _remember(updated)
        return updated
    reason = _bound(result, confirmation)
    if reason:
        updated["blocked_reason"] = reason
        _remember(updated)
        return updated
    if confirmation.get("comparison_id") != result.get("comparison_id"):
        updated["blocked_reason"] = "comparison_mismatch"
        _remember(updated)
        return updated
    orientation = result.get("provisional_orientation")
    ids = list((result.get("document_hashes") or {}).keys())
    baseline_id = confirmation.get("baseline_version_id")
    other_id = confirmation.get("other_version_id")
    if baseline_id != orientation or baseline_id not in ids:
        updated["blocked_reason"] = "baseline_mismatch"
        _remember(updated)
        return updated
    if other_id not in ids or other_id == baseline_id:
        updated["blocked_reason"] = "other_version_mismatch"
        _remember(updated)
        return updated
    held = _HELD[result["comparison_id"]]
    if confirmation.get("baseline_document_hash") != held["document_hashes"].get(baseline_id):
        updated["blocked_reason"] = "document_hash_mismatch"
        _remember(updated)
        return updated
    if confirmation.get("other_document_hash") != held["document_hashes"].get(other_id):
        updated["blocked_reason"] = "document_hash_mismatch"
        _remember(updated)
        return updated
    if "versions" in confirmation or "clauses" in confirmation or "text" in confirmation:
        updated["blocked_reason"] = "caller_rehash_rejected"
        _remember(updated)
        return updated
    person, role_reason = _named_reader(result, directory, confirmation.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    ack_reason = _ack(result, confirmation)
    if ack_reason:
        updated["blocked_reason"] = ack_reason
        _remember(updated)
        return updated
    updated["versions_confirmed"] = True
    updated["baseline_version_id"] = baseline_id
    updated["other_version_id"] = other_id
    updated["human_approval"] = {
        "item": "version-pair",
        "approver_ref": person["employee_ref"],
        "content_hash": held["content_hash"],
        "recorded": True,
        "approves_document": False,
    }
    updated["blocked_reason"] = None
    updated["outcome"] = "versions_confirmed"
    _force(updated)
    _remember(updated)
    return updated


def record_interpretation_seen(result: dict, directory: dict, acknowledgement: dict) -> dict:
    """Record that the reader owns the interpretation of this exact comparison."""

    updated = deepcopy(result)
    _force(updated)
    updated["interpretation_acknowledged"] = False
    if not isinstance(acknowledgement, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if acknowledgement.get("item") != "interpretation" or acknowledgement.get("decision") != "seen":
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    if result.get("versions_confirmed") is not True:
        updated["blocked_reason"] = "versions_not_confirmed"
        _remember(updated)
        return updated
    reason = _bound(result, acknowledgement)
    if reason:
        updated["blocked_reason"] = reason
        _remember(updated)
        return updated
    if acknowledgement.get("interpretation_owned_by_user") is not True:
        updated["blocked_reason"] = "interpretation_not_boolean_true"
        _remember(updated)
        return updated
    person, role_reason = _named_reader(result, directory, acknowledgement.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    updated["interpretation_acknowledged"] = True
    updated["legal_advice"] = False
    updated["document_approved"] = False
    updated["blocked_reason"] = None
    _force(updated)
    _remember(updated)
    return updated


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two synthetic document versions.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = prepare_comparison(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
