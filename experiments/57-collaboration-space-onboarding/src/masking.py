"""Mask a copied string and report what was actually replaced.

The output is not anonymised. A count is recorded only for a pattern that
matched text this function was given. Callers that copy nothing must not
claim a mask ran on that text.
"""

from __future__ import annotations

import re

EMAIL = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE = re.compile(
    r"(?<!\d)(?:\+44[\s\-()]?\d(?:[\s\-()]?\d){8,12}|0\d(?:[\s\-()]?\d){8,11})(?!\d)"
)
DOB = re.compile(
    r"\b(?:date of birth|d\.?o\.?b\.?|born on|born)\b[:\s,/-]{0,16}"
    r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}",
    re.IGNORECASE,
)
DATE_NEAR_BIRTH = re.compile(
    r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b(?=[^.]{0,24}\b(?:date of birth|born)\b)",
    re.IGNORECASE,
)
STREET = re.compile(
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\s+"
    r"(?:Street|Road|Lane|Avenue|Close|Way|Drive|Place|Gardens|Crescent)\b",
    re.IGNORECASE,
)
POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.IGNORECASE)
NAME = re.compile(
    r"\b(?:Mr|Mrs|Ms|Mx|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b"
)

_PATTERNS = (
    ("date_of_birth", DOB, "[date of birth]"),
    ("date_of_birth_near", DATE_NEAR_BIRTH, "[date of birth]"),
    ("email", EMAIL, "[email]"),
    ("phone", PHONE, "[phone]"),
    ("address", STREET, "[address]"),
    ("postcode", POSTCODE, "[postcode]"),
    ("name", NAME, "[name]"),
)


def mask_text(text: str) -> tuple[str, dict]:
    if not isinstance(text, str):
        return "", {"copied": False, "replacements": {}}
    masked = text
    replacements: dict[str, int] = {}
    for name, pattern, token in _PATTERNS:
        found = pattern.findall(masked)
        if found:
            replacements[name] = replacements.get(name, 0) + len(found)
            masked = pattern.sub(token, masked)
    masked = re.sub(r"\s+", " ", masked).strip()
    return masked, {"copied": True, "replacements": replacements}


def empty_mask_report() -> dict:
    return {
        "snippets_copied": False,
        "document_extracts_copied": False,
        "external_urls_copied": False,
        "output_is_anonymised": False,
        "replacements": {
            "phone": 0,
            "email": 0,
            "date_of_birth": 0,
            "address": 0,
            "postcode": 0,
            "name": 0,
        },
        "note": "Nothing was copied, so nothing was masked. The output is not anonymised.",
    }


def add_replacements(report: dict, detail: dict) -> None:
    report["snippets_copied"] = True
    for name, count in detail["replacements"].items():
        key = "date_of_birth" if name.startswith("date_of_birth") else name
        report["replacements"][key] = report["replacements"].get(key, 0) + count
    report["note"] = (
        "Counts are replacements this run made in text it copied. "
        "A zero means that pattern did not match the copied text. "
        "The output is not anonymised."
    )
