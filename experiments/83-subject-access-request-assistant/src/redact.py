"""Propose redactions of third-party personal data.

Experiment 08 supplies UK identifiers. Names, emails, phones, dates of birth,
postal addresses, and staff ids are detected here. The requester's own values
are not proposed for redaction. Matched text is not stored. The output is not
described as anonymised.
"""

from __future__ import annotations

import re
from datetime import date

if __package__ in {None, ""}:
    from siblings import identifier_spans
else:
    from .siblings import identifier_spans

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE = re.compile(
    r"(?:\+44[\s-]?\d(?:[\s-]?\d){9,12}|07\d{3}[\s-]?\d{6}|0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4})"
)
_DOB = re.compile(
    r"\b(?:date of birth|d\.?o\.?b\.?|born on)\b[:\s-]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    re.IGNORECASE,
)
_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.IGNORECASE)
_STREET = re.compile(
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+"
    r"(?:Street|Road|Avenue|Lane|Close|Drive|Way|Court)\b"
)
_NAME = re.compile(
    r"\b(?:Mr|Mrs|Ms|Miss|Dr|Mx|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b"
    r"|(?i:\b(?:my name is|name is|neighbour|neighbor|called)\s+)[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b"
    r"|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b"
)
_NOT_NAMES = frozenset({
    "subject access",
    "data protection",
    "reedmarsh borough",
    "borough council",
    "legal professional",
    "official sensitive",
    "legal hold",
    "information governance",
    "united kingdom",
    "freedom of",
    "personal data",
    "confidential reference",
    "management forecasting",
    "management planning",
})
_STAFF = re.compile(
    r"\b(?:staff id|staff number|employee id|employee number)\s*[:#-]?\s*[A-Z]{2,5}-?\d{3,6}\b"
    r"|\b(?:STF|EMP)-\d{4,6}\b",
    re.IGNORECASE,
)
_MALFORMED_AMOUNT = re.compile(r"£\s*\d{1,3},\d{2}\.\d{2}")

_PLACEHOLDER = {
    "email": "[email]",
    "phone": "[phone]",
    "date_of_birth": "[date of birth]",
    "postal_address": "[address]",
    "personal_name": "[name]",
    "staff_id": "[staff id]",
    "uk_identifier": "[uk identifier]",
}


def _fold(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value).strip().casefold()


def _own_values(requester: dict) -> set[str]:
    keys = (
        "name", "email", "date_of_birth", "address", "postcode",
        "staff_id", "reference", "phone", "nino",
    )
    values = set()
    for key in keys:
        folded = _fold(requester.get(key))
        if folded:
            values.add(folded)
    name = _fold(requester.get("name"))
    if name:
        values.add(name)
    return values


def _is_own(span_text: str, own: set[str], requester_name: str) -> bool:
    folded = _fold(span_text)
    if not folded:
        return False
    if folded in own:
        return True
    if requester_name and requester_name in folded:
        return True
    for value in own:
        if value and value in folded:
            return True
    return False


def _collect(text: str, own: set[str], requester_name: str, on: date) -> list[tuple[int, int, str]]:
    patterns = (
        ("email", _EMAIL),
        ("phone", _PHONE),
        ("date_of_birth", _DOB),
        ("postal_address", _POSTCODE),
        ("postal_address", _STREET),
        ("personal_name", _NAME),
        ("staff_id", _STAFF),
    )
    found: list[tuple[int, int, str]] = []
    for kind, pattern in patterns:
        for match in pattern.finditer(text):
            if kind == "personal_name" and _fold(match.group(0)) in _NOT_NAMES:
                continue
            if _is_own(match.group(0), own, requester_name):
                continue
            found.append((match.start(), match.end(), kind))
    for start, end, _placeholder in identifier_spans(text, on=on):
        if _is_own(text[start:end], own, requester_name):
            continue
        found.append((start, end, "uk_identifier"))
    found.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    chosen: list[tuple[int, int, str]] = []
    cursor = -1
    for start, end, kind in found:
        if start < cursor:
            continue
        chosen.append((start, end, kind))
        cursor = end
    return chosen


def propose(text: str, requester: dict, *, on: date, document_id: str) -> dict:
    own = _own_values(requester if isinstance(requester, dict) else {})
    requester_name = _fold((requester or {}).get("name") if isinstance(requester, dict) else "")
    body = text if isinstance(text, str) else ""
    spans = _collect(body, own, requester_name, on)
    redactions = []
    masked = body
    for index, (start, end, kind) in enumerate(reversed(spans), start=1):
        redactions.append({
            "redaction_id": f"{document_id}-R{len(spans) - index + 1}",
            "document_id": document_id,
            "kind": kind,
            "placeholder": _PLACEHOLDER[kind],
            "applied_by_agent": False,
            "human_decision": None,
        })
        masked = masked[:start] + _PLACEHOLDER[kind] + masked[end:]
    redactions.reverse()
    counts: dict[str, int] = {}
    for row in redactions:
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
    return {
        "redactions": redactions,
        "masked_text": masked,
        "counts": counts,
        "values_stored": False,
        "described_as_anonymised": False,
        "malformed_amount": bool(_MALFORMED_AMOUNT.search(body)),
        "amount_coerced": False,
    }
