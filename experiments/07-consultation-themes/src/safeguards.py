"""Redaction and prompt-injection flags for consultation responses.

Responses are data. Nothing in this module reads them as instructions.
Recognised identifier values are replaced and are not returned.
"""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
# UK national format, including +44. Aimed at numbers respondents type, not at
# every digit string.
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+44[\s-]?\d(?:[\s-]?\d){9,10}|\b0\d(?:[\s-]?\d){9,10})(?!\d)"
)
# Temporary NI prefixes that are not issued. Case folding is on the expression.
NI_RE = re.compile(
    r"\b(?!BG)(?!GB)(?!KN)(?!NK)(?!NT)(?!TN)(?!ZZ)"
    r"[A-CEGHJ-PR-TW-Z]{2}\s*\d{2}\s*\d{2}\s*\d{2}\s*[A-D]\b",
    re.IGNORECASE,
)
NHS_RE = re.compile(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b")
POSTCODE_RE = re.compile(
    r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b",
    re.IGNORECASE,
)
SORT_CODE_RE = re.compile(r"\b\d{2}-\d{2}-\d{2}\b")

# Word list only. A hit is a flag for the analyst, not a theme and not a diagnosis.
SPECIAL_CATEGORY_RE = re.compile(
    r"\b(?:disability|disabled|cancer|hiv|mental health|wheelchair|diagnosis|diagnosed)\b",
    re.IGNORECASE,
)

# Instruction-shaped phrases. A resident who disagrees with the council is not
# a match: "I ignore the council leaflet" does not match these patterns.
INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_instructions",
        re.compile(
            r"\bignore\s+(?:all\s+|any\s+|the\s+)?(?:previous|above|prior)\s+instructions\b",
            re.IGNORECASE,
        ),
    ),
    (
        "disregard_rules",
        re.compile(
            r"\bdisregard\s+(?:your|the)\s+(?:instructions|rules|system\s+prompt)\b",
            re.IGNORECASE,
        ),
    ),
    ("you_are_now", re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE)),
    (
        "system_prompt_request",
        re.compile(
            r"\b(?:output|reveal|print|show)\s+the\s+system\s+prompt\b",
            re.IGNORECASE,
        ),
    ),
    (
        "set_framework_approved",
        re.compile(r"\bset\s+framework_approved\s+to\s+true\b", re.IGNORECASE),
    ),
    (
        "mark_samples_accepted",
        re.compile(
            r"\bmark\s+(?:all|every)\s+samples?\s+(?:as\s+)?accepted\b",
            re.IGNORECASE,
        ),
    ),
    (
        "drop_minority_instruction",
        re.compile(
            r"\b(?:drop|delete|exclude|omit)\s+(?:the\s+)?minority\s+views?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "publish_report",
        re.compile(r"\bpublish\s+the\s+(?:report|analysis)\b", re.IGNORECASE),
    ),
    (
        "email_instruction",
        re.compile(r"\bemail\s+the\s+\w+\b", re.IGNORECASE),
    ),
    (
        "role_marker",
        re.compile(r"<\|im_start\|>|\[INST\]|###\s*system\b", re.IGNORECASE),
    ),
)


def nhs_checksum_ok(digits: str) -> bool:
    """Return True for a 10-digit NHS number with a valid check digit."""
    if len(digits) != 10 or not digits.isdigit():
        return False
    total = sum(int(digit) * (10 - index) for index, digit in enumerate(digits[:9]))
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        check = 0
    if check == 10:
        return False
    return check == int(digits[9])


def _replace(pattern: re.Pattern[str], token: str, text: str, type_name: str, found: list[str]) -> str:
    def replacer(_match: re.Match[str]) -> str:
        found.append(type_name)
        return token

    return pattern.sub(replacer, text)


def redact(text: str) -> tuple[str, list[str], list[str]]:
    """Replace recognised identifiers. Return redacted text, types, and special-category flags.

    The raw match is not returned. Types are sorted and de-duplicated.
    """
    found: list[str] = []
    redacted = text or ""
    redacted = _replace(EMAIL_RE, "[EMAIL]", redacted, "email", found)
    redacted = _replace(PHONE_RE, "[PHONE]", redacted, "phone", found)
    redacted = _replace(NI_RE, "[NI-NUMBER]", redacted, "ni_number", found)

    def nhs_replacer(match: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if nhs_checksum_ok(digits):
            found.append("nhs_number")
            return "[NHS-NUMBER]"
        return match.group(0)

    redacted = NHS_RE.sub(nhs_replacer, redacted)
    redacted = _replace(POSTCODE_RE, "[POSTCODE]", redacted, "postcode", found)
    redacted = _replace(SORT_CODE_RE, "[SORT-CODE]", redacted, "sort_code", found)
    special: list[str] = []
    if SPECIAL_CATEGORY_RE.search(redacted):
        special.append("health")
    types = sorted(set(found))
    return redacted, types, special


def injection_flags(text: str) -> list[str]:
    """Return pattern ids for instruction-shaped phrases. Empty if none."""
    flags = [name for name, pattern in INJECTION_PATTERNS if pattern.search(text or "")]
    return flags
