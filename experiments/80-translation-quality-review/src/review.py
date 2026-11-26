"""Review a synthetic translation. Do not publish, send, or overwrite it.

The named bilingual reviewer validates every high-risk segment and owns
the final translation. Those steps are separate objects bound to the
agent-held copy. A sentence in the source or the target is not a step.

Autonomy is A0. Automatic quality estimation is a pattern check. It is
limited, especially where the target language shares few words with English.
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
    from checks import (
        CHECKS,
        analyse,
        content_risk,
        glossary_differences,
        injection_report,
        joined_text,
        pinned_glossary,
        read_date,
        sensitive_report,
    )
    from risk import distress_sentences
    from siblings import identifier_counts, neighbours
    from sources import uk_context
else:
    from .checks import (
        CHECKS,
        analyse,
        content_risk,
        glossary_differences,
        injection_report,
        joined_text,
        pinned_glossary,
        read_date,
        sensitive_report,
    )
    from .risk import distress_sentences
    from .siblings import identifier_counts, neighbours
    from .sources import uk_context

LABEL = (
    "DRAFT TRANSLATION REVIEW FOR THE NAMED BILINGUAL REVIEWER. "
    "NOT A QUALITY CERTIFICATE. THE REVIEWER OWNS THE FINAL TRANSLATION."
)
CATALOGUE_ID = "O006"
EXPERIMENT_ID = "exp-80-translation-quality-review"
ROOT = Path(__file__).resolve().parents[1]
REVIEW_ID = re.compile(r"^TRN-\d{4}$")
LANGUAGES = frozenset({"en", "cy", "pl"})
KINDS = frozenset({"public_information", "correspondence", "guidance"})
ROLE = "bilingual_reviewer"
_HELD: dict[str, dict] = {}
_PROHIBITED = (
    "translation_owned",
    "translation_approved",
    "approved",
    "published",
    "sent",
    "overwritten",
    "no_issues",
    "high_risk_validated",
    "route_seen",
    "segments_validated",
    "clearance",
    "role",
    "reviewer_role",
    "human_approval",
    "quality_score",
)


class ReviewForbidden(RuntimeError):
    """The agent does not publish, send, overwrite, or approve a translation."""

    __test__ = False


class NotSynthetic(ValueError):
    """The request was not marked synthetic."""


def publish_translation(*_args, **_kwargs) -> None:
    raise ReviewForbidden("The agent does not publish a translation.")


def send_translation(*_args, **_kwargs) -> None:
    raise ReviewForbidden("The agent does not send a translation.")


def overwrite_document(*_args, **_kwargs) -> None:
    raise ReviewForbidden("The agent does not overwrite a document.")


def approve_translation(*_args, **_kwargs) -> None:
    raise ReviewForbidden("The agent does not approve a translation. The named reviewer owns it.")


def reset_held() -> None:
    _HELD.clear()


def held_record(review_id: object) -> dict | None:
    if not isinstance(review_id, str):
        return None
    row = _HELD.get(review_id)
    if not isinstance(row, dict):
        return None
    return {
        "review_id": review_id,
        "content_hash": row.get("content_hash"),
        "document_hashes": dict(row.get("document_hashes") or {}),
    }


def pinned_directory() -> dict:
    return json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _projection(result: dict) -> dict:
    return {
        "review_id": result.get("review_id"),
        "reviewer_ref": result.get("reviewer_ref"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "source_language": result.get("source_language"),
        "target_language": result.get("target_language"),
        "document_kind": result.get("document_kind"),
        "segments_validated": result.get("segments_validated") is True,
        "translation_owned": result.get("translation_owned") is True,
        "published": result.get("published") is True,
        "sent": result.get("sent") is True,
        "overwritten": result.get("overwritten") is True,
        "translation_approved_by_agent": result.get("translation_approved_by_agent") is True,
        "instructions_followed": result.get("instructions_followed") is True,
        "high_risk_validated": result.get("high_risk_validated") is True,
        "route_seen": result.get("route_seen") is True,
        "document_hashes": result.get("document_hashes"),
        "rows": result.get("rows"),
        "flags": result.get("flags"),
        "checks_performed": result.get("checks_performed"),
        "no_issues": result.get("no_issues") is True,
        "statement": result.get("statement"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "legal_hold_unparseable": result.get("legal_hold_unparseable"),
        "retention": result.get("retention"),
        "retention_unparseable": result.get("retention_unparseable"),
        "prompt_injection": result.get("prompt_injection"),
        "suppression": result.get("suppression"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "glossary_report": result.get("glossary_report"),
        "caller_glossary_applied": result.get("caller_glossary_applied") is True,
        "low_confidence_count": result.get("low_confidence_count"),
        "high_risk": result.get("high_risk"),
        "distress": result.get("distress"),
        "duplicate_conflicts": result.get("duplicate_conflicts"),
        "unparseable": result.get("unparseable"),
        "dates": result.get("dates"),
        "quality_estimation": result.get("quality_estimation"),
        "bodies_withheld": result.get("bodies_withheld"),
        "masking": result.get("masking"),
        "uk_identifiers": result.get("uk_identifiers"),
        "excerpts": result.get("excerpts"),
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _force(result: dict) -> None:
    result["published"] = False
    result["sent"] = False
    result["overwritten"] = False
    result["translation_approved_by_agent"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["caller_glossary_applied"] = False
    result["caller_directory_applied"] = False
    result["coerced"] = False
    result["described_as_anonymised"] = False
    result["may_be_relied_on"] = False
    result["production_written"] = False
    result["experiment_38_compare_called"] = False
    result["automatic_quality_estimation_limited"] = True
    estimation = result.get("quality_estimation")
    if isinstance(estimation, dict):
        estimation["quality_score"] = None
        estimation["limited"] = True
        estimation["score_used_to_clear_high_risk"] = False
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
    reading = read_date(value, None)
    parsed = neighbours()["as_date"](reading)
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


def _store(result: dict, document_hashes: dict) -> None:
    review_id = result.get("review_id")
    if not isinstance(review_id, str):
        return
    result["content_hash"] = _hash(result)
    _HELD[review_id] = {
        "content_hash": result["content_hash"],
        "projection": _projection(result),
        "document_hashes": dict(document_hashes),
    }


def _remember(result: dict) -> None:
    review_id = result.get("review_id")
    held = _HELD.get(review_id) if isinstance(review_id, str) else None
    hashes = dict((held or {}).get("document_hashes") or result.get("document_hashes") or {})
    result["content_hash"] = _hash(result)
    if result.get("blocked_reason") or not isinstance(review_id, str):
        return
    _HELD[review_id] = {
        "content_hash": result["content_hash"],
        "projection": _projection(result),
        "document_hashes": hashes,
    }


def _body_hash(side: str, payload: object) -> str:
    return _digest({"side": side, "body": payload})


def _segments(payload: object) -> list:
    if isinstance(payload, dict) and isinstance(payload.get("segments"), list):
        return payload["segments"]
    return []


def _cover(payload: object) -> str:
    if isinstance(payload, dict) and isinstance(payload.get("cover"), str):
        return payload["cover"]
    return ""


def _date_row(field: str, value: object, question: date, owner: str) -> dict:
    reading = read_date(value, question)
    parsed = neighbours()["as_date"](reading)
    stale = field == "review_date" and parsed is not None and parsed <= question
    future = reading.get("future") is True and field != "review_date"
    reason = reading.get("reason")
    if stale:
        reason = "stale"
    elif field == "review_date" and reading.get("future") is True:
        reason = None
        future = False
    return {
        "field": field,
        "owner": owner,
        "iso": reading.get("iso"),
        "unparseable": reading.get("unparseable") is True,
        "ambiguous": reading.get("ambiguous") is True,
        "future": future,
        "stale": stale,
        "reason": reason,
        "coerced": False,
    }


def _excerpt(text: str) -> tuple[str, dict, dict]:
    tools = neighbours()
    redacted = text
    for sentence in distress_sentences(text):
        redacted = redacted.replace(sentence, "[routed to the reviewer]")
    masked, report = tools["mask_text"](redacted)
    suppressed, suppression = tools["suppress_small_counts"](masked)
    report = dict(report)
    report["values_stored"] = False
    report["values_copied"] = False
    report["described_as_anonymised"] = False
    report["masked_text_included"] = True
    return suppressed, report, suppression


def _merge_mask(total: dict, report: dict) -> None:
    counts = total.setdefault("counts", {})
    for key, value in (report.get("counts") or {}).items():
        counts[key] = int(counts.get(key, 0)) + int(value)
    total["any"] = any(counts.values())
    total["values_stored"] = False
    total["values_copied"] = False
    total["described_as_anonymised"] = False
    total["masked_text_included"] = True


def _reviewer_state(directory: dict, ref: object, target_language: str) -> dict:
    person = _person(directory, ref)
    if person is None:
        return {"on_directory": False, "language_gap": True, "active_reviewer": False}
    languages = person.get("languages") if isinstance(person.get("languages"), list) else []
    active = (
        person.get("active") is True
        and person.get("guest") is not True
        and person.get("role") == ROLE
    )
    return {
        "on_directory": True,
        "language_gap": target_language not in languages,
        "active_reviewer": active,
        "clearance": person.get("clearance") if isinstance(person.get("clearance"), str) else None,
    }


def prepare_review(request: dict, *, as_of: str, directory: dict | None = None) -> dict:
    """Return a draft review. The translation is not owned. Nothing is sent."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object.")
    if request.get("synthetic") is not True:
        raise NotSynthetic("The request was not marked synthetic.")
    question = _question_date(as_of)
    stripped, ignored = _strip(request)
    pinned = pinned_directory()
    if directory is not None and directory != pinned:
        caller_directory = True
    else:
        caller_directory = "directory" in stripped
    glossary = pinned_glossary()
    source = stripped.get("source") if isinstance(stripped.get("source"), dict) else {}
    target = stripped.get("target") if isinstance(stripped.get("target"), dict) else {}
    source_segments = _segments(source)
    target_segments = _segments(target)
    source_language = stripped.get("source_language")
    target_language = stripped.get("target_language")
    document_kind = stripped.get("document_kind")
    review_id = stripped.get("review_id")
    unparseable = []
    if source_language != "en":
        unparseable.append({"field": "source_language", "reason": "source_must_be_en", "coerced": False})
    if target_language not in LANGUAGES:
        unparseable.append({"field": "target_language", "reason": "language_not_in_the_pinned_set", "coerced": False})
        target_language = None
    if document_kind not in KINDS:
        unparseable.append({"field": "document_kind", "reason": "kind_not_in_the_pinned_set", "coerced": False})
        document_kind = None
    if not isinstance(review_id, str) or not REVIEW_ID.fullmatch(review_id):
        unparseable.append({"field": "review_id", "reason": "review_id_not_readable", "coerced": False})
        review_id = review_id if isinstance(review_id, str) else None

    reviewer_ref = stripped.get("reviewer_ref")
    reviewer = _reviewer_state(pinned, reviewer_ref, target_language or "")
    analysis = analyse(
        source_segments,
        target_segments,
        target_language=target_language or "en",
        document_kind=document_kind or "public_information",
        glossary=glossary,
        question=question,
    )
    if target_language is None or document_kind is None:
        # The checks ran only so the list is present. They are not a clearance.
        analysis["unparseable"] = list(analysis["unparseable"]) + unparseable
    else:
        analysis["unparseable"] = list(analysis["unparseable"]) + unparseable

    high_risk = content_risk(source_segments, target_segments)
    for row in high_risk:
        analysis["flags"].append({
            "type": "high_risk_content",
            "segment_id": row.get("segment_id"),
            "detail": "High-risk content is routed to the reviewer regardless of overlap.",
            "categories": list(row.get("categories") or []),
            "values_published": False,
            "published_count": None,
            "published_difference": None,
            "published_percentage": None,
            "headcount": None,
            "delta": None,
            "source_values": None,
            "target_values": None,
        })
    distress = sensitive_report(source_segments, target_segments)
    note = stripped.get("note") if isinstance(stripped.get("note"), str) else ""
    injection = injection_report(
        joined_text(source_segments),
        joined_text(target_segments),
        _cover(source),
        _cover(target),
        note,
        json.dumps(stripped.get("caller_glossary"), default=str) if stripped.get("caller_glossary") is not None else "",
    )
    glossary_report = glossary_differences(stripped.get("caller_glossary"), glossary)
    if glossary_report["differences"] or glossary_report["unparseable"]:
        analysis["flags"].append({
            "type": "caller_glossary_difference",
            "segment_id": None,
            "detail": "The caller glossary differs from the pinned glossary. It was not applied.",
            "values_published": False,
            "published_count": None,
            "published_difference": None,
            "published_percentage": None,
            "headcount": None,
            "delta": None,
            "source_values": None,
            "target_values": None,
        })

    tools = neighbours()
    cover = "\n".join(part for part in (_cover(source), _cover(target)) if part)
    full_text = "\n".join(part for part in (cover, joined_text(source_segments), joined_text(target_segments)) if part)
    content_labels = tools["content_markings"](full_text)
    meta_labels, meta_bad = tools["metadata_markings"](source.get("protective_marking"))
    target_labels, target_bad = tools["metadata_markings"](target.get("protective_marking"))
    applied = tools["higher_marking"](content_labels + meta_labels + target_labels)
    hold, hold_bad = tools["legal_hold"](source.get("legal_hold"), full_text)
    target_hold, target_hold_bad = tools["legal_hold"](target.get("legal_hold"), "")
    retention, retention_bad = tools["retention_labels"](source.get("retention"), full_text)
    target_retention, target_retention_bad = tools["retention_labels"](target.get("retention"), "")
    for label in target_retention:
        if label not in retention:
            retention.append(label)
    ceiling = reviewer.get("clearance")
    withhold = tools["above_ceiling"](applied, ceiling) or reviewer.get("on_directory") is not True
    if withhold:
        for flag in analysis["flags"]:
            flag["values_published"] = False
            flag["source_values"] = None
            flag["target_values"] = None
            flag["published_count"] = None
            flag["published_difference"] = None
            flag["published_percentage"] = None
            flag["headcount"] = None
            flag["delta"] = None

    dates = []
    for owner, payload in (("source", source), ("target", target)):
        if not isinstance(payload, dict):
            continue
        for field in ("effective_date", "review_date", "retention_trigger"):
            if field in payload:
                dates.append(_date_row(field, payload.get(field), question, owner))
    if isinstance(glossary.get("review_date"), str):
        dates.append(_date_row("review_date", glossary.get("review_date"), question, "pinned_glossary"))

    excerpts = []
    mask_total = tools["empty_mask"]()
    suppression = {"applied": False, "threshold": 5, "published_count": None, "published_difference": None, "published_percentage": None, "headcount": None, "delta": None, "described_as_anonymised": False}
    if not withhold:
        for side, segments in (("source", source_segments), ("target", target_segments)):
            for segment in segments:
                if not isinstance(segment, dict) or not isinstance(segment.get("text"), str):
                    continue
                text, report, suppressed = _excerpt(segment["text"])
                _merge_mask(mask_total, report)
                if suppressed.get("applied"):
                    suppression["applied"] = True
                excerpts.append({
                    "side": side,
                    "segment_id": segment.get("segment_id"),
                    "excerpt": text,
                    "masked": True,
                    "cue_copied": False,
                })
    else:
        excerpts.append({
            "side": "both",
            "segment_id": None,
            "excerpt": "[withheld: above the reviewer's directory clearance]",
            "masked": False,
            "cue_copied": False,
        })

    duplicate_conflicts = [row for row in analysis["flags"] if row["type"] == "duplicate_conflict"]
    substantive = [
        row for row in analysis["flags"]
        if row["type"] not in {"low_confidence_alignment", "high_risk_content"}
    ]
    needs_route = bool(
        distress["routed"]
        or high_risk
        or substantive
        or analysis["low_confidence_count"]
        or analysis["unparseable"]
        or glossary_report["differences"]
        or glossary_report["unparseable"]
        or duplicate_conflicts
        or withhold
        or reviewer["language_gap"]
        or reviewer["active_reviewer"] is not True
        or injection["signals"]
        or any(row.get("stale") or row.get("unparseable") or row.get("ambiguous") or row.get("future") for row in dates)
    )
    no_issues = not needs_route and bool(analysis["checks_performed"])
    if no_issues:
        statement = "No issues found in the checks that were run."
        outcome = "checks_clear"
    else:
        statement = "Issues or a human route remain. The checks that were run are listed."
        outcome = "route_to_human"
    if "no issues" in statement.casefold() and not no_issues:
        statement = "Issues or a human route remain. The checks that were run are listed."

    sources_current = not any(
        row.get("stale") or row.get("unparseable") or row.get("ambiguous") or row.get("future") for row in dates
    )
    required = ["pins_seen", "segments_seen"]
    if any(row.get("stale") or row.get("unparseable") or row.get("ambiguous") or row.get("future") for row in dates):
        required.append("dates_seen")
    if not sources_current:
        required.append("sources_seen")
    if applied:
        required.append("markings_seen")
    if analysis["flags"] or analysis["low_confidence_count"]:
        required.append("flags_seen")
    if glossary_report["present"]:
        required.append("glossary_seen")

    document_hashes = {
        "source": _body_hash("source", {"cover": _cover(source), "segments": source_segments, "marking": source.get("protective_marking"), "legal_hold": source.get("legal_hold"), "retention": source.get("retention")}),
        "target": _body_hash("target", {"cover": _cover(target), "segments": target_segments, "marking": target.get("protective_marking"), "legal_hold": target.get("legal_hold"), "retention": target.get("retention")}),
    }
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A0",
        "synthetic": True,
        "review_id": review_id,
        "reviewer_ref": reviewer_ref if isinstance(reviewer_ref, str) else None,
        "reviewer_on_directory": reviewer["on_directory"],
        "reviewer_language_gap": reviewer["language_gap"],
        "as_of": question.isoformat(),
        "question_date_respected": True,
        "today_not_used": True,
        "source_language": "en" if source_language == "en" else None,
        "target_language": target_language,
        "document_kind": document_kind,
        "outcome": outcome,
        "statement": statement,
        "no_issues": no_issues,
        "checks_performed": list(CHECKS),
        "flags": analysis["flags"],
        "rows": analysis["rows"],
        "low_confidence_count": analysis["low_confidence_count"],
        "high_risk": high_risk,
        "high_risk_routed_regardless_of_score": bool(high_risk),
        "distress": distress,
        "duplicate_conflicts": duplicate_conflicts,
        "unparseable": analysis["unparseable"],
        "prompt_injection": injection,
        "ignored_request_keys": ignored,
        "glossary_report": glossary_report,
        "caller_glossary_applied": False,
        "caller_directory_applied": False,
        "caller_directory_present": caller_directory,
        "marking": {
            "applied": applied,
            "from_content": content_labels,
            "from_metadata": meta_labels + target_labels,
            "metadata_unparseable": meta_bad or target_bad,
            "higher_of_conflict": True,
            "self_declared_clearance_ignored": True,
        },
        "legal_hold": hold or target_hold,
        "legal_hold_unparseable": hold_bad or target_hold_bad,
        "retention": retention,
        "retention_unparseable": retention_bad or target_retention_bad,
        "dates": dates,
        "sources_current": sources_current,
        "bodies_withheld": withhold,
        "excerpts": excerpts,
        "masking": mask_total,
        "suppression": suppression,
        "uk_identifiers": {"called": False, "count": 0, "types": [], "output_is_anonymised": False, "values_stored": False, "redacted_text_copied": False},
        "document_hashes": document_hashes,
        "required_acknowledgements": required,
        "segments_validated": False,
        "high_risk_validated": False,
        "route_seen": False,
        "translation_owned": False,
        "human_approval": None,
        "blocked_reason": None,
        "uk_context": uk_context(),
        "quality_estimation": {
            "method": "deterministic_patterns",
            "learned_quality_estimation": False,
            "limited": True,
            "lower_resource_languages": ["cy", "pl"],
            "note": (
                "Welsh and Polish are not scored by a translation model. "
                "Lexical overlap with English is expected to be low. "
                "A low-confidence alignment is reported and is not a quality score. "
                "High-risk segments are routed to the reviewer regardless of overlap."
            ),
            "quality_score": None,
            "score_used_to_clear_high_risk": False,
            "not_a_certificate": True,
        },
        "alignment": {
            "reused": "experiments/79-document-comparison/src/align.py",
            "copied": False,
        },
        "experiment_79_align_called": True,
        "experiment_08_called": False,
        "experiment_38_compare_called": False,
    }
    _force(result)
    if full_text and not withhold:
        try:
            result["uk_identifiers"] = identifier_counts(full_text, on=question)
            result["experiment_08_called"] = True
        except Exception as exc:  # noqa: BLE001 — a neighbour failure is a flag, not a guessed count
            result["uk_identifiers"] = {
                "called": False,
                "error": type(exc).__name__,
                "values_stored": False,
                "output_is_anonymised": False,
                "redacted_text_copied": False,
            }
            result["unparseable"].append({"field": "uk_identifiers", "reason": type(exc).__name__, "coerced": False})
    result["uk_identifiers"]["redacted_text_copied"] = False
    result["uk_identifiers"]["values_stored"] = False
    result["uk_identifiers"]["output_is_anonymised"] = False
    _force(result)
    if isinstance(review_id, str):
        _store(result, document_hashes)
    else:
        result["content_hash"] = _hash(result)
    return result


def _named_reviewer(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_directory()
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("reviewer_ref"):
        return None, "not_the_named_reviewer"
    person = _person(pinned, approver_ref)
    if person is None or person.get("active") is not True or person.get("guest") is True or person.get("role") != ROLE:
        return None, "approver_not_directory_reviewer"
    if result.get("reviewer_on_directory") is not True:
        return None, "approver_not_directory_reviewer"
    languages = person.get("languages") if isinstance(person.get("languages"), list) else []
    if result.get("target_language") not in languages:
        return None, "language_not_on_directory"
    return person, None


def _bound(result: dict, approval: dict) -> str | None:
    review_id = result.get("review_id")
    held = _HELD.get(review_id) if isinstance(review_id, str) else None
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


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def _documents_match(result: dict, approval: dict) -> str | None:
    held = _HELD[result["review_id"]]
    if approval.get("source_document_hash") != held["document_hashes"].get("source"):
        return "document_hash_mismatch"
    if approval.get("target_document_hash") != held["document_hashes"].get("target"):
        return "document_hash_mismatch"
    if "segments" in approval or "text" in approval or "source" in approval or "target" in approval:
        return "caller_rehash_rejected"
    return None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named reviewer has seen a human route. Nothing is sent."""

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
    _person_row, role_reason = _named_reviewer(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    if approval.get("review_id") != result.get("review_id"):
        updated["blocked_reason"] = "review_mismatch"
        _remember(updated)
        return updated
    updated["route_seen"] = True
    updated["distress"] = {
        "routed": True if (result.get("distress") or {}).get("categories") else (result.get("distress") or {}).get("routed"),
        "categories": list((result.get("distress") or {}).get("categories") or []),
        "cue_copied": False,
        "source_seen": True,
        "seen": True,
    }
    updated["blocked_reason"] = None
    _force(updated)
    _remember(updated)
    return updated


def record_high_risk_validated(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named reviewer has validated the high-risk segments."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["high_risk_validated"] = False
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if approval.get("item") != "high-risk" or approval.get("decision") != "validated":
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    if not result.get("high_risk"):
        updated["blocked_reason"] = "no_high_risk_segments"
        _remember(updated)
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        _remember(updated)
        return updated
    reason = _bound(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        _remember(updated)
        return updated
    if approval.get("review_id") != result.get("review_id"):
        updated["blocked_reason"] = "review_mismatch"
        _remember(updated)
        return updated
    if _documents_match(result, approval):
        updated["blocked_reason"] = _documents_match(result, approval)
        _remember(updated)
        return updated
    _person_row, role_reason = _named_reviewer(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    if approval.get("validated_by_reviewer") is not True:
        updated["blocked_reason"] = "validated_by_reviewer_not_boolean_true"
        _remember(updated)
        return updated
    updated["high_risk_validated"] = True
    updated["segments_validated"] = True
    updated["blocked_reason"] = None
    updated["human_approval"] = {
        "item": "high-risk",
        "approver_ref": approval.get("approver_ref"),
        "content_hash": _HELD[result["review_id"]]["content_hash"],
        "recorded": True,
        "approves_translation": False,
    }
    _force(updated)
    _remember(updated)
    return updated


def record_translation_owned(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named reviewer owns this exact translation. Do not publish it."""

    updated = deepcopy(result)
    _force(updated)
    updated["translation_owned"] = False
    updated["human_approval"] = None
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if approval.get("item") != "translation-owned" or approval.get("decision") != "own":
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        _remember(updated)
        return updated
    if result.get("high_risk") and result.get("high_risk_validated") is not True:
        updated["blocked_reason"] = "high_risk_not_validated"
        _remember(updated)
        return updated
    reason = _bound(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        _remember(updated)
        return updated
    if approval.get("review_id") != result.get("review_id"):
        updated["blocked_reason"] = "review_mismatch"
        _remember(updated)
        return updated
    document_reason = _documents_match(result, approval)
    if document_reason:
        updated["blocked_reason"] = document_reason
        _remember(updated)
        return updated
    _person_row, role_reason = _named_reviewer(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    ack_reason = _ack(result, approval)
    if ack_reason:
        updated["blocked_reason"] = ack_reason
        _remember(updated)
        return updated
    if approval.get("translation_owned_by_reviewer") is not True:
        updated["blocked_reason"] = "translation_owned_by_reviewer_not_boolean_true"
        _remember(updated)
        return updated
    updated["translation_owned"] = True
    updated["segments_validated"] = True
    updated["blocked_reason"] = None
    updated["outcome"] = "translation_owned_by_reviewer"
    updated["human_approval"] = {
        "item": "translation-owned",
        "approver_ref": approval.get("approver_ref"),
        "content_hash": _HELD[result["review_id"]]["content_hash"],
        "recorded": True,
        "approves_translation": False,
        "publishes": False,
    }
    _force(updated)
    _remember(updated)
    return updated


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review a synthetic translation. Do not publish it.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = prepare_review(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
