"""Cover-sheet, agenda, conflict, and action checks. Nothing is approved here."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import date

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
    from negate import affirmed
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
    from .negate import affirmed

OUTSIDE_PHRASES = {
    "community-grants": ("community grants", "community grant"),
    "executive-remuneration": ("executive remuneration", "executive pay"),
    "nomination": ("nomination of directors",),
}

_LINE_LABELS = (
    ("purpose", "purpose"),
    ("recommendation", "recommendation"),
    ("version", "version"),
    ("document_date", "document date"),
    ("sponsor_ref", "sponsor"),
    ("marking", "marking"),
)


def digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def paper_projection(paper: dict) -> dict:
    cover = paper.get("cover") if isinstance(paper.get("cover"), dict) else {}
    body = paper.get("body") if isinstance(paper.get("body"), str) else None
    return {
        "paper_id": paper.get("paper_id"),
        "version": paper.get("version"),
        "author_ref": paper.get("author_ref"),
        "sponsor_ref": cover.get("sponsor_ref"),
        "purpose": cover.get("purpose"),
        "recommendation": cover.get("recommendation"),
        "document_date": cover.get("document_date"),
        "marking": cover.get("marking"),
        "risk": cover.get("risk"),
        "finance": cover.get("finance"),
        "legal": cover.get("legal"),
        "equality": cover.get("equality"),
        "body": body,
    }


def paper_hash(paper: dict) -> str:
    return digest(paper_projection(paper))


def version_key(value: object) -> tuple[int, ...] | None:
    """A version that is not dotted integers is unreadable. It is not zero."""

    if not isinstance(value, str) or not value.strip():
        return None
    parts = value.strip().split(".")
    numbers = []
    for part in parts:
        if not part.isdigit():
            return None
        numbers.append(int(part))
    return tuple(numbers)


def publish_count(count: object, threshold: object) -> dict:
    if type(threshold) is not int or threshold < 1:
        return {"published": None, "suppressed": False, "unreadable": True, "coerced": False}
    if type(count) is not int or count < 0:
        return {"published": None, "suppressed": False, "unreadable": True, "coerced": False}
    if count < threshold:
        return {
            "published": None,
            "suppressed": True,
            "unreadable": False,
            "threshold": threshold,
            "coerced": False,
        }
    return {
        "published": count,
        "suppressed": False,
        "unreadable": False,
        "threshold": threshold,
        "coerced": False,
    }


def _people(directory: dict) -> list[dict]:
    rows = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str) or not ref:
        return None
    for row in _people(directory):
        if row.get("employee_ref") == ref:
            return row
    return None


def _line_value(body: str, label: str) -> str | None:
    prefix = label.lower() + ":"
    for raw in (body or "").splitlines():
        line = raw.strip()
        if not line.lower().startswith(prefix):
            continue
        value = line[len(prefix):].strip()
        if value and affirmed(line, value):
            return value
    return None


def cover_standard(paper: dict, allowed_purposes: set[str]) -> dict:
    cover = paper.get("cover") if isinstance(paper.get("cover"), dict) else {}
    purpose = cover.get("purpose")
    purpose_stated = isinstance(purpose, str) and purpose in allowed_purposes
    recommendation = cover.get("recommendation")
    recommendation_present = isinstance(recommendation, str) and bool(recommendation.strip())
    implications = {}
    complete_implications = True
    for field in ("risk", "finance", "legal", "equality"):
        value = cover.get(field)
        if value == "completed":
            implications[field] = "completed"
        elif value == "not_applicable":
            note = cover.get(f"{field}_note")
            if isinstance(note, str) and note.strip():
                implications[field] = "not_applicable"
            else:
                implications[field] = "not_applicable_without_note"
                complete_implications = False
        else:
            implications[field] = "incomplete"
            complete_implications = False
    return {
        "purpose_stated": purpose_stated,
        "purpose": purpose if purpose_stated else None,
        "recommendation_present": recommendation_present,
        "implications": implications,
        "complete": purpose_stated and recommendation_present and complete_implications,
        "coerced": False,
    }


def inconsistencies(paper: dict) -> list[str]:
    cover = paper.get("cover") if isinstance(paper.get("cover"), dict) else {}
    body = paper.get("body") if isinstance(paper.get("body"), str) else ""
    found = []
    for field, label in _LINE_LABELS:
        stated = _line_value(body, label)
        if stated is None:
            continue
        cover_value = cover.get(field)
        cover_text = cover_value.strip() if isinstance(cover_value, str) else ""
        if stated.casefold() != cover_text.casefold():
            found.append(field)
    return found


def text_outside(body: str, terms: dict) -> list[str]:
    outside = set(terms.get("outside_remit") or []) if isinstance(terms, dict) else set()
    found = []
    for matter, phrases in OUTSIDE_PHRASES.items():
        if matter not in outside:
            continue
        for phrase in phrases:
            if affirmed(body or "", phrase):
                found.append(matter)
                break
    return found


def sponsor_status(paper: dict, directory: dict, ledger: list[dict]) -> dict:
    cover = paper.get("cover") if isinstance(paper.get("cover"), dict) else {}
    sponsor_ref = cover.get("sponsor_ref")
    row = person(directory, sponsor_ref)
    role_ok = bool(
        row
        and row.get("guest") is not True
        and (row.get("role") == "sponsor" or row.get("can_sponsor") is True)
    )
    expected = paper_hash(paper)
    text_claim = category_hit(paper.get("body") or "", "approval_marker") or "approved_by" in paper
    matched = False
    hash_mismatch = False
    for entry in ledger:
        if not isinstance(entry, dict):
            continue
        if entry.get("item") != "paper" or entry.get("decision") != "sponsor-approve":
            continue
        if entry.get("paper_id") != paper.get("paper_id") or entry.get("version") != paper.get("version"):
            continue
        if entry.get("sponsor_ref") != sponsor_ref:
            continue
        if entry.get("pins_seen") is not True:
            continue
        if entry.get("content_hash") == expected and role_ok:
            matched = True
            break
        if entry.get("content_hash") != expected:
            hash_mismatch = True
    return {
        "recorded": matched,
        "source": "deterministic_ledger" if matched else None,
        "from_text": bool(text_claim),
        "trusted_from_text": False,
        "sponsor_on_directory": role_ok,
        "hash_mismatch": hash_mismatch and not matched,
        "content_hash": expected,
    }


def version_flags(papers: list[dict]) -> dict[str, list[str]]:
    """Return flags keyed by submission_id. Unreadable versions are not zero."""

    groups: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        paper_id = paper.get("paper_id")
        if isinstance(paper_id, str):
            groups[paper_id].append(paper)
    flags: dict[str, list[str]] = {}
    for group in groups.values():
        parsed = []
        for paper in group:
            key = version_key(paper.get("version"))
            submission = str(paper.get("submission_id") or "")
            flags.setdefault(submission, [])
            if key is None:
                flags[submission].append("version_unparseable")
            else:
                parsed.append((key, submission))
        if parsed:
            best = max(key for key, _submission in parsed)
            for key, submission in parsed:
                if key < best:
                    flags[submission].append("superseded")
        counts = Counter(
            paper.get("version")
            for paper in group
            if version_key(paper.get("version")) is not None
        )
        for paper in group:
            version = paper.get("version")
            if version_key(version) is not None and counts[version] > 1:
                flags[str(paper.get("submission_id") or "")].append("duplicate")
    return flags


def interest_live(row: dict, on: date) -> dict:
    status = row.get("status")
    if status not in {"open", "closed"}:
        return {"live": False, "unreadable": True, "coerced": False}
    if status != "open":
        return {"live": False, "unreadable": False, "coerced": False}
    start = parse_date(row.get("start"))
    if start["unparseable"] or start["ambiguous"]:
        return {"live": False, "unreadable": True, "coerced": False}
    end_raw = row.get("end")
    end_day = None
    if end_raw not in (None, ""):
        end = parse_date(end_raw)
        if end["unparseable"] or end["ambiguous"]:
            return {"live": False, "unreadable": True, "coerced": False}
        end_day = as_date(end)
    start_day = as_date(start)
    if start_day is not None and on < start_day:
        return {"live": False, "unreadable": False, "coerced": False}
    if end_day is not None and on > end_day:
        return {"live": False, "unreadable": False, "coerced": False}
    return {"live": True, "unreadable": False, "coerced": False}


def is_late(submitted: object, deadline: object) -> bool | None:
    """A paper on the deadline day is not late. An unreadable date is not late and not on time."""

    left = as_date(parse_date(submitted))
    right = as_date(parse_date(deadline))
    if left is None or right is None:
        return None
    return left > right


def marking_for(paper: dict, ceiling: str | None) -> dict:
    cover = paper.get("cover") if isinstance(paper.get("cover"), dict) else {}
    meta, meta_bad = metadata_markings(cover.get("marking"))
    body = paper.get("body") if isinstance(paper.get("body"), str) else ""
    content = content_markings(body)
    applied = higher_marking(meta + content)
    hold, hold_bad = legal_hold(paper.get("legal_hold"), body)
    retention, retention_bad = retention_labels(paper.get("retention"), body)
    return {
        "applied": applied,
        "from_metadata": meta,
        "from_content": content,
        "metadata_unparseable": meta_bad,
        "above_clearance": above_ceiling(applied, ceiling),
        "legal_hold": hold,
        "legal_hold_unparseable": hold_bad,
        "retention": retention,
        "retention_unparseable": retention_bad,
        "body_copied": False,
    }


def scan_text(paper: dict) -> dict:
    body = paper.get("body") if isinstance(paper.get("body"), str) else ""
    found = hits(body)
    return {
        "cues": found,
        "distress": distress_hit(body),
        "carve_out": carve_out(body),
        "instructions": "embedded_instruction" in found,
        "approval_marker": "approval_marker" in found,
        "role_claim": "role_claim" in found,
        "conflict_declared": "conflict_declared" in found,
        "cue_copied": False,
    }


def carry_forward(minutes: dict, directory: dict, on: date) -> dict:
    actions = minutes.get("actions") if isinstance(minutes, dict) else None
    carried = []
    not_carried = []
    if not isinstance(actions, list):
        return {
            "carried": [],
            "not_carried": [],
            "unreadable": True,
            "minutes_approved": False,
            "decisions_recorded": False,
            "text_copied": False,
        }
    for action in actions:
        if not isinstance(action, dict):
            not_carried.append({"action_id": None, "reason": "not_an_object", "coerced": False})
            continue
        status = action.get("status")
        action_id = action.get("action_id") if isinstance(action.get("action_id"), str) else None
        if status == "closed":
            not_carried.append({"action_id": action_id, "reason": "closed", "coerced": False})
            continue
        if status != "open":
            not_carried.append({"action_id": action_id, "reason": "status_unreadable", "coerced": False})
            continue
        due = parse_date(action.get("due"))
        due_day = as_date(due)
        owner_ref = action.get("owner_ref")
        owner = person(directory, owner_ref)
        carried.append(
            {
                "action_id": action_id,
                "owner_ref": owner_ref if isinstance(owner_ref, str) else None,
                "owner_on_directory": owner is not None,
                "due": due["iso"],
                "due_unparseable": bool(due["unparseable"] or due["ambiguous"]),
                "overdue": (due_day < on) if due_day is not None else None,
                "text_copied": False,
                "minutes_approved": False,
            }
        )
    return {
        "carried": carried,
        "not_carried": not_carried,
        "unreadable": False,
        "minutes_approved": False,
        "decisions_recorded": False,
        "text_copied": False,
    }
