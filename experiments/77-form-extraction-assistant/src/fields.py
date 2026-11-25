"""Read labelled lines against a pinned schema.

A missing value stays missing. An illegible value is not guessed.
Two different values for one field are both kept as locations and neither
is chosen. A checkbox that is ticked and crossed is not resolved.
A signature is present or absent. It is never verified.
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

if __package__ in {None, ""}:
    from dates import parse_date
else:
    from .dates import parse_date

_PAGE = re.compile(r"^PAGE\s+(\d+)\s*$", re.IGNORECASE)
_FIELD = re.compile(
    r"^(?:LINE\s+(?P<line>\d+)\s+)?"
    r"(?:BOX\s+(?P<box>[A-Za-z0-9_-]+)\s+)?"
    r"(?P<label>[^:]{1,80}?):\s*(?P<value>.*)$"
)
_ILLEGIBLE = re.compile(r"\[(?:illegible|unclear|unreadable)\]|\?\?\?|#{3,}|�", re.IGNORECASE)
_NEGATED = re.compile(
    r"not true that|not the case that|\bit is not\b|\bthis is not\b|\bis not\b|\bisn't\b|\bnever\b",
    re.IGNORECASE,
)
_TICK = re.compile(r"\[(?:x|✓|✔)\]|\bticked\b|\byes\b", re.IGNORECASE)
_CROSS = re.compile(r"\[(?:✗|✘)\]|\bcrossed\b|\bunticked\b|\bno\b", re.IGNORECASE)
_POSTCODE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$")
_BLANK = {"", "-", "—", "–"}

_PROBLEM = {
    "ambiguous",
    "impossible",
    "unparseable",
    "out_of_range",
    "illegible",
    "negated",
    "contradictory_duplicate",
    "ticked_and_crossed",
    "verification_claim_ignored",
}


def _label_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def _index(schema_fields: list[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for field in schema_fields:
        index[_label_key(field["field_id"].replace("_", " "))] = field
        index[_label_key(field["field_id"])] = field
        for label in field.get("labels") or []:
            index[_label_key(str(label))] = field
    return index


def _location(page: int | None, line: int, box: str | None) -> dict:
    return {"page": page, "line": line, "box_id": box}


def _money(raw: str, *, minimum: object, maximum: object) -> tuple[str | None, list[str]]:
    cleaned = raw.strip().replace("£", "").replace(",", "").replace(" ", "")
    if not re.fullmatch(r"-?\d+(?:\.\d{1,2})?", cleaned):
        return None, ["unparseable"]
    try:
        amount = Decimal(cleaned)
    except InvalidOperation:
        return None, ["unparseable"]
    normalised = f"{amount:.2f}"
    flags: list[str] = []
    if minimum is not None and amount < Decimal(str(minimum)):
        flags.append("out_of_range")
    if maximum is not None and amount > Decimal(str(maximum)):
        flags.append("out_of_range")
    return normalised, flags


def _postcode(raw: str) -> str | None:
    compact = re.sub(r"\s+", "", raw.strip().upper())
    if not _POSTCODE.fullmatch(compact):
        return None
    return f"{compact[:-3]} {compact[-3:]}"


def _sort_code(raw: str) -> str | None:
    if not re.fullmatch(r"[\d\s-]+", raw.strip()):
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 6:
        return None
    return f"{digits[0:2]}-{digits[2:4]}-{digits[4:6]}"


def _account(raw: str) -> str | None:
    text = raw.strip()
    if not re.fullmatch(r"\d{8}", text):
        return None
    return text


def _count(raw: str) -> str | None:
    text = raw.strip()
    if not re.fullmatch(r"\d+", text):
        return None
    return str(int(text))


def _checkbox(raw: str) -> tuple[str | None, list[str], str]:
    text = raw.strip()
    if text.casefold() in _BLANK:
        return None, ["blank"], "blank"
    if _ILLEGIBLE.search(text):
        return None, ["illegible"], "illegible"
    ticked = _TICK.search(text) is not None
    crossed = _CROSS.search(text) is not None
    if ticked and crossed:
        return None, ["ticked_and_crossed"], "ticked_and_crossed"
    if ticked:
        return "ticked", [], "extracted"
    if crossed:
        return "unticked", [], "extracted"
    return None, ["unparseable"], "unparseable"


def _signature(raw: str) -> tuple[str | None, list[str], str]:
    text = raw.strip()
    if _ILLEGIBLE.search(text):
        return None, ["illegible"], "illegible"
    if text.casefold() in _BLANK:
        return "absent", ["blank_box"], "extracted"
    present = re.search(r"\[signed\]|\bsigned\b|signature present|\bpresent\b", text, re.IGNORECASE)
    absent = re.search(r"\bunsigned\b|signature absent|\bnot signed\b|\babsent\b", text, re.IGNORECASE)
    verified_claim = re.search(r"\bverified\b", text, re.IGNORECASE) is not None
    if present and absent:
        flags = ["contradictory_duplicate"]
        if verified_claim:
            flags.append("verification_claim_ignored")
        return None, flags, "contradictory"
    if present or verified_claim:
        flags = ["verification_claim_ignored"] if verified_claim else []
        return "present", flags, "extracted"
    if absent:
        return "absent", [], "extracted"
    return None, ["unparseable"], "unparseable"


def _one(raw: str, field: dict, *, on: date) -> dict:
    text = raw.strip()
    kind = field["kind"]
    flags: list[str] = []
    status = "extracted"
    value: str | None = None
    normalised: str | None = None
    days = None
    verified = False

    if kind == "signature":
        value, flags, status = _signature(text)
        normalised = value
    elif kind == "checkbox":
        value, flags, status = _checkbox(text)
        normalised = value
    elif text.casefold() in _BLANK:
        status = "blank"
        flags = ["blank"]
    elif _ILLEGIBLE.search(text):
        status = "illegible"
        flags = ["illegible"]
    elif kind != "text" and _NEGATED.search(text):
        status = "negated"
        flags = ["negated"]
    elif kind == "date":
        parsed = parse_date(text, on=on)
        if parsed["ambiguous"]:
            status = "ambiguous"
            flags = ["ambiguous"]
        elif parsed["impossible"]:
            status = "impossible"
            flags = ["impossible"]
        elif parsed["unparseable"] or not parsed["iso"]:
            status = "unparseable"
            flags = ["unparseable"]
        else:
            value = parsed["iso"]
            normalised = parsed["iso"]
            days = parsed["days_from_as_of"]
            if parsed["future"]:
                flags.append("future")
    elif kind == "amount":
        normalised, flags = _money(text, minimum=field.get("minimum"), maximum=field.get("maximum"))
        if normalised is None:
            status = "unparseable"
        else:
            value = normalised
            if "out_of_range" in flags:
                status = "out_of_range"
    elif kind == "postcode":
        normalised = _postcode(text)
        if normalised is None:
            status = "unparseable"
            flags = ["unparseable"]
        else:
            value = normalised
    elif kind == "sort_code":
        normalised = _sort_code(text)
        if normalised is None:
            status = "unparseable"
            flags = ["unparseable"]
        else:
            value = normalised
    elif kind == "account_number":
        normalised = _account(text)
        if normalised is None:
            status = "unparseable"
            flags = ["unparseable"]
        else:
            value = normalised
    elif kind in {"count", "percent", "difference"}:
        normalised = _count(text)
        if normalised is None:
            status = "unparseable"
            flags = ["unparseable"]
        else:
            value = normalised
    else:
        if _NEGATED.search(text):
            status = "negated"
            flags = ["negated"]
        else:
            value = text
            normalised = text

    confidence = _confidence(status, flags)
    return {
        "raw": text,
        "value": value,
        "normalised": normalised,
        "flags": flags,
        "status": status,
        "days_from_as_of": days,
        "verified": verified,
        "confidence": confidence[0],
        "confidence_band": confidence[1],
        "coerced": False,
    }


def _confidence(status: str, flags: list[str]) -> tuple[float | None, str | None]:
    if status in {"blank", "missing"}:
        return None, None
    if status in {"illegible", "negated", "contradictory", "ticked_and_crossed"}:
        return 0.15, "low"
    if status in {"ambiguous", "impossible", "unparseable", "out_of_range"} or (
        set(flags) & _PROBLEM
    ):
        return 0.55, "review"
    return 0.95, "high"


def _empty(field: dict) -> dict:
    return {
        "field_id": field["field_id"],
        "kind": field["kind"],
        "material": bool(field.get("material")),
        "material_class": field.get("material_class"),
        "required": bool(field.get("required")),
        "status": "missing",
        "value": None,
        "stated": None,
        "normalised": None,
        "confidence": None,
        "confidence_band": None,
        "locations": [],
        "flags": ["missing"] if field.get("required") else ["blank"],
        "coerced": False,
        "suppressed": False,
        "verified": False,
        "days_from_as_of": None,
        "values_withheld": False,
    }


def _merge(field: dict, sightings: list[dict]) -> dict:
    row = _empty(field)
    if not sightings:
        return row
    row["locations"] = [item["location"] for item in sightings]
    row["flags"] = []
    comparable = [item["parsed"]["normalised"] for item in sightings]
    distinct = {item for item in comparable if item is not None}
    problem_status = [item["parsed"]["status"] for item in sightings if item["parsed"]["status"] != "extracted"]
    if len(sightings) > 1 and (len(distinct) > 1 or (distinct and problem_status)):
        row["status"] = "contradictory"
        row["value"] = None
        row["stated"] = None
        row["normalised"] = None
        row["flags"] = ["contradictory_duplicate"]
        row["confidence"] = 0.15
        row["confidence_band"] = "low"
        return row
    if len(sightings) > 1 and len(distinct) == 1 and not problem_status:
        chosen = sightings[0]["parsed"]
        row.update(_from_parsed(chosen))
        row["flags"] = list(chosen["flags"]) + ["duplicated"]
        row["status"] = "duplicated"
        return row
    if len(sightings) > 1 and not distinct:
        chosen = sightings[0]["parsed"]
        row.update(_from_parsed(chosen))
        if "contradictory_duplicate" not in row["flags"]:
            row["flags"] = list(row["flags"]) + ["contradictory_duplicate"]
        row["status"] = "contradictory"
        row["value"] = None
        row["normalised"] = None
        row["stated"] = None
        return row
    row.update(_from_parsed(sightings[0]["parsed"]))
    row["stated"] = sightings[0]["parsed"]["raw"] if row["value"] is not None or row["status"] in {
        "ambiguous",
        "impossible",
        "unparseable",
        "out_of_range",
        "negated",
    } else None
    if row["status"] in {"illegible", "blank", "negated", "ticked_and_crossed"}:
        row["stated"] = None
    return row


def _from_parsed(parsed: dict) -> dict:
    return {
        "status": parsed["status"],
        "value": parsed["value"],
        "normalised": parsed["normalised"],
        "flags": list(parsed["flags"]),
        "confidence": parsed["confidence"],
        "confidence_band": parsed["confidence_band"],
        "verified": False,
        "days_from_as_of": parsed["days_from_as_of"],
        "coerced": False,
        "stated": parsed["raw"] if parsed["value"] is not None else None,
    }


def _suppress(rows: list[dict], threshold: int) -> dict:
    small: list[str] = []
    for row in rows:
        if row["kind"] != "count" or row["normalised"] is None:
            continue
        try:
            number = int(row["normalised"])
        except (TypeError, ValueError):
            continue
        if 0 < number < threshold:
            small.append(row["field_id"])
    percent_ids = [row["field_id"] for row in rows if row["kind"] == "percent"]
    difference_ids = [row["field_id"] for row in rows if row["kind"] == "difference"]
    count_ids = [row["field_id"] for row in rows if row["kind"] == "count"]
    if small:
        for row in rows:
            if row["kind"] in {"count", "percent", "difference"}:
                row["value"] = None
                row["stated"] = None
                row["normalised"] = None
                row["days_from_as_of"] = None
                row["suppressed"] = True
                if "suppressed_small_number" not in row["flags"]:
                    row["flags"].append("suppressed_small_number")
    return {
        "threshold": threshold,
        "small_count_field_ids": small,
        "count_field_ids": count_ids if small else [],
        "percent_field_ids": percent_ids if small else [],
        "difference_field_ids": difference_ids if small else [],
        "values_copied": False,
        "rule": "A count from 1 to 4 is withheld, and so are percentages, differences, and counts under other field names. Five is this starter's threshold, not a claim of anonymisation.",
    }


def extract_fields(text: str, schema_fields: list[dict], *, on: date, threshold: int) -> dict:
    index = _index(schema_fields)
    grouped: dict[str, list[dict]] = {field["field_id"]: [] for field in schema_fields}
    unexpected: list[dict] = []
    page: int | None = None
    for physical, line in enumerate((text or "").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        page_match = _PAGE.fullmatch(stripped)
        if page_match:
            page = int(page_match.group(1))
            continue
        field_match = _FIELD.fullmatch(stripped)
        if not field_match:
            continue
        label = field_match.group("label")
        raw_value = field_match.group("value")
        line_no = int(field_match.group("line") or physical)
        box = field_match.group("box")
        key = _label_key(label)
        if key in {"retention", "legal hold", "page"}:
            continue
        field = index.get(key)
        if field is None:
            unexpected.append(
                {
                    "label": _label_key(label)[:80],
                    "page": page,
                    "line": line_no,
                    "box_id": box,
                    "value_copied": False,
                    "masked": True,
                }
            )
            continue
        parsed = _one(raw_value, field, on=on)
        grouped[field["field_id"]].append(
            {"parsed": parsed, "location": _location(page, line_no, box)}
        )

    rows = [_merge(field, grouped[field["field_id"]]) for field in schema_fields]
    rows.sort(key=lambda item: item["field_id"])
    suppression = _suppress(rows, threshold)
    return {"fields": rows, "unexpected_fields": unexpected, "suppression": suppression}


def withhold(rows: list[dict]) -> None:
    for row in rows:
        row["value"] = None
        row["stated"] = None
        row["normalised"] = None
        row["days_from_as_of"] = None
        row["values_withheld"] = True
