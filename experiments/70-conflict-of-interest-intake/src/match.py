"""Dates, amounts, supplier links, and source diffs.

An unreadable date or amount is flagged. It is not replaced with zero or
with today. A caller-supplied register is not the pinned register.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date

if __package__ in {None, ""}:
    from negate import affirmed, denied_at, sentences
else:
    from .negate import affirmed, denied_at, sentences

_ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
_UK = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b")
_VAGUE_DATE = re.compile(
    r"\b(?:sometime|last spring|last autumn|last winter|last summer|a while ago|the other day|ages ago)\b",
    re.IGNORECASE,
)
_MONEY = re.compile(r"£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)")
_VAGUE_MONEY = re.compile(
    r"\b(?:several thousand|a few thousand|about lots|some money|a large sum|loads of money)\b",
    re.IGNORECASE,
)
_PROC = re.compile(r"\bPROC-\d{4}-\d{3}\b", re.IGNORECASE)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def parse_iso(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _valid(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _denied_span(sentence: str, start: int, end: int) -> bool:
    return denied_at(sentence, sentence[start:end], start)


def extract_dates(text: str) -> dict:
    parsed: list[str] = []
    unparseable = 0
    for sentence in sentences(text or ""):
        for match in _ISO.finditer(sentence):
            if _denied_span(sentence, match.start(), match.end()):
                continue
            iso = _valid(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            if iso is None:
                unparseable += 1
            elif iso not in parsed:
                parsed.append(iso)
        for match in _UK.finditer(sentence):
            if _denied_span(sentence, match.start(), match.end()):
                continue
            iso = _valid(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            if iso is None:
                unparseable += 1
            elif iso not in parsed:
                parsed.append(iso)
        for match in _VAGUE_DATE.finditer(sentence):
            if _denied_span(sentence, match.start(), match.end()):
                continue
            unparseable += 1
    return {
        "dates": [{"iso": item, "precision": "day", "raw_stored": False} for item in parsed],
        "unparseable_count": unparseable,
        "raw_stored": False,
        "coerced": False,
    }


def extract_amounts(text: str) -> dict:
    amounts: list[dict] = []
    unparseable = 0
    seen: set[str] = set()
    for sentence in sentences(text or ""):
        for match in _MONEY.finditer(sentence):
            if _denied_span(sentence, match.start(), match.end()):
                continue
            number = match.group(1).replace(",", "")
            if "." not in number:
                number = number + ".00"
            if number not in seen:
                seen.add(number)
                amounts.append({"amount": number, "currency": "GBP", "raw_stored": False})
        for match in _VAGUE_MONEY.finditer(sentence):
            if _denied_span(sentence, match.start(), match.end()):
                continue
            unparseable += 1
    return {
        "amounts": amounts,
        "unparseable_count": unparseable,
        "raw_stored": False,
        "coerced": False,
    }


def _rows(document: dict, key: str) -> list[dict]:
    rows = document.get(key)
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def mentioned_supplier_ids(text: str, suppliers: dict) -> list[str]:
    found: list[str] = []
    rows = sorted(_rows(suppliers, "suppliers"), key=lambda row: len(str(row.get("name") or "")), reverse=True)
    for row in rows:
        name = row.get("name")
        supplier_id = row.get("supplier_id")
        if not isinstance(name, str) or not isinstance(supplier_id, str):
            continue
        if affirmed(text, name) or affirmed(text, supplier_id):
            if supplier_id not in found:
                found.append(supplier_id)
    return found


def mentioned_procurement_ids(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        for match in _PROC.finditer(sentence):
            if _denied_span(sentence, match.start(), match.end()):
                continue
            token = match.group(0).upper()
            if token not in found:
                found.append(token)
    return found


def _row_live(row: dict, on: date) -> dict:
    status = row.get("status")
    start_raw = row.get("start")
    end_raw = row.get("end")
    start = parse_iso(start_raw) if start_raw not in (None, "") else None
    end = parse_iso(end_raw) if end_raw not in (None, "") else None
    unreadable = False
    if start_raw not in (None, "") and start is None:
        unreadable = True
    if end_raw not in (None, "") and end is None:
        unreadable = True
    if status not in {"live", "ended", "planned"}:
        unreadable = True
    if unreadable:
        return {"live_on_question_date": False, "coverage": "unreadable", "coerced": False}
    if start is not None and on < start:
        return {"live_on_question_date": False, "coverage": "not_yet", "coerced": False}
    if end is not None and on > end:
        return {"live_on_question_date": False, "coverage": "ended", "coerced": False}
    if status != "live":
        return {"live_on_question_date": False, "coverage": status, "coerced": False}
    return {"live_on_question_date": True, "coverage": "live", "coerced": False}


def procurement_view(register: dict, supplier_ids: list[str], named_ids: list[str], on: date) -> dict:
    links = []
    named = []
    unreadable = []
    unknown = []
    known = {}
    for row in _rows(register, "procurements"):
        procurement_id = row.get("procurement_id")
        supplier_id = row.get("supplier_id")
        if isinstance(procurement_id, str):
            known[procurement_id.upper()] = row
        if not isinstance(procurement_id, str) or not isinstance(supplier_id, str):
            unreadable.append({"procurement_id": None, "coverage": "unreadable"})
            continue
        relevant = supplier_id in supplier_ids or procurement_id.upper() in named_ids
        if not relevant:
            continue
        coverage = _row_live(row, on)
        item = {
            "procurement_id": procurement_id,
            "supplier_id": supplier_id,
            "title_from_register": row.get("title") if isinstance(row.get("title"), str) else None,
            "declarant_named_procurement": procurement_id.upper() in named_ids,
            "live_on_question_date": coverage["live_on_question_date"],
            "coverage": coverage["coverage"],
            "for_ethics_team": True,
            "conflict_exists": None,
            "coerced": False,
        }
        if coverage["coverage"] == "unreadable":
            unreadable.append(item)
        elif coverage["live_on_question_date"]:
            links.append(item)
        else:
            named.append(item)
    for token in named_ids:
        if token not in known:
            unknown.append(token)
    return {
        "potential_links": links,
        "not_live": named,
        "unreadable_rows": unreadable,
        "unknown_procurement_ids": unknown,
    }


def id_set(document: object, key: str, field: str) -> set[str] | None:
    if not isinstance(document, dict):
        return None
    rows = document.get(key)
    if not isinstance(rows, list):
        return None
    found = set()
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get(field), str):
            found.add(row[field])
    return found


def source_note(pinned: object, supplied: object, *, row_key: str | None, id_field: str | None) -> dict:
    if supplied is None:
        return {
            "supplied": False,
            "differs": False,
            "unreadable": False,
            "only_in_supplied": [],
            "missing_from_supplied": [],
            "used": "pinned",
        }
    if not isinstance(supplied, dict) or not isinstance(pinned, dict):
        return {
            "supplied": True,
            "differs": True,
            "unreadable": True,
            "only_in_supplied": [],
            "missing_from_supplied": [],
            "used": "pinned",
        }
    differs = canonical(pinned) != canonical(supplied)
    only: list[str] = []
    missing: list[str] = []
    if row_key and id_field:
        left = id_set(pinned, row_key, id_field) or set()
        right = id_set(supplied, row_key, id_field)
        if right is None:
            return {
                "supplied": True,
                "differs": True,
                "unreadable": True,
                "only_in_supplied": [],
                "missing_from_supplied": [],
                "used": "pinned",
            }
        only = sorted(right - left)
        missing = sorted(left - right)
    return {
        "supplied": True,
        "differs": differs,
        "unreadable": False,
        "only_in_supplied": only,
        "missing_from_supplied": missing,
        "used": "pinned",
    }
