"""Deterministic UK identifier spans.

A finding is a proposal to redact. ``not_redacted`` records a span the rules
deliberately left in place. Neither structure contains the matched text.
The caller already has the source.
"""

from __future__ import annotations

from identifiers import (
    ACCOUNT_LABEL_RE,
    CRN_LABEL_RE,
    CRN_PREFIXES,
    CRN_RE,
    EIGHT_DIGIT_RE,
    IBAN_RE,
    NHS_CUE_RE,
    NHS_GROUPED_RE,
    NHS_LABEL_RE,
    NINO_RE,
    POSTCODE_RE,
    SORT_LABEL_RE,
    SORT_RE,
    UTR_RE,
    classify_nino_prefix,
    iban_checksum_status,
    label_within,
    looks_like_day_and_month,
    nhs_checksum_status,
)

PRIORITY = {
    "iban": 0,
    "nino": 1,
    "nhs_number": 2,
    "sort_code": 3,
    "account_number": 4,
    "postcode": 5,
    "crn": 6,
    "utr": 7,
}


def _span(entity_type: str, start: int, end: int, detector: str, checksum: str, confidence: str, **detail: str) -> dict:
    return {
        "entity_type": entity_type,
        "start": start,
        "end": end,
        "detector": detector,
        "checksum": checksum,
        "confidence": confidence,
        "detail": detail,
    }


def _ninos(text: str) -> list[dict]:
    found = []
    for match in NINO_RE.finditer(text):
        prefix = match.group(1).upper()
        suffix = match.group(5).upper()
        prefix_class = classify_nino_prefix(prefix)
        found.append(
            _span(
                "nino",
                match.start(),
                match.end(),
                "nino_pattern",
                "not_applicable",
                "high",
                prefix_class=prefix_class,
                suffix=suffix,
            )
        )
    return found


def _ibans(text: str) -> list[dict]:
    found = []
    for match in IBAN_RE.finditer(text):
        status = iban_checksum_status(match.group(1))
        confidence = "high" if status == "passed" else "medium"
        found.append(
            _span(
                "iban",
                match.start(),
                match.end(),
                "gb_iban_pattern",
                status,
                confidence,
            )
        )
    return found


def _nhs(text: str) -> tuple[list[dict], list[dict]]:
    found: list[dict] = []
    skipped: list[dict] = []
    seen: set[tuple[int, int]] = set()

    def add(start: int, end: int, digits: str, detector: str, labelled: bool) -> None:
        key = (start, end)
        if key in seen:
            return
        seen.add(key)
        status = nhs_checksum_status(digits)
        if status == "passed":
            found.append(
                _span("nhs_number", start, end, detector, "passed", "high", labelled=str(labelled).lower())
            )
            return
        if labelled:
            found.append(
                _span(
                    "nhs_number",
                    start,
                    end,
                    detector,
                    status,
                    "context",
                    labelled="true",
                )
            )
            return
        skipped.append(
            {
                "reason": "nhs_checksum_failed_unlabelled",
                "entity_type": "nhs_number",
                "start": start,
                "end": end,
                "checksum": status,
            }
        )

    for match in NHS_GROUPED_RE.finditer(text):
        digits = match.group(1) + match.group(2) + match.group(3)
        labelled = label_within(text, match.start(), NHS_CUE_RE)
        add(match.start(), match.end(), digits, "nhs_grouped", labelled)

    for match in NHS_LABEL_RE.finditer(text):
        raw = match.group(1)
        digits = "".join(character for character in raw if character.isdigit())
        add(match.start(1), match.end(1), digits, "nhs_labelled", True)
    return found, skipped


def _sort_codes(text: str) -> tuple[list[dict], list[dict]]:
    found = []
    skipped = []
    for match in SORT_RE.finditer(text):
        token = match.group(1)
        labelled = label_within(text, match.start(), SORT_LABEL_RE)
        if looks_like_day_and_month(token) and not labelled:
            skipped.append(
                {
                    "reason": "date_shaped_sort_code",
                    "entity_type": "sort_code",
                    "start": match.start(),
                    "end": match.end(),
                    "checksum": "not_checked",
                }
            )
            continue
        found.append(
            _span(
                "sort_code",
                match.start(),
                match.end(),
                "sort_code_pattern",
                "not_checked",
                "medium",
                labelled=str(labelled).lower(),
            )
        )
    return found, skipped


def _labelled_crn_spans(text: str) -> set[tuple[int, int]]:
    return {(match.start(1), match.end(1)) for match in CRN_LABEL_RE.finditer(text)}


def _accounts(text: str, sort_hits: list[dict], crn_spans: set[tuple[int, int]]) -> list[dict]:
    found = []
    occupied: set[tuple[int, int]] = set()
    for match in ACCOUNT_LABEL_RE.finditer(text):
        occupied.add((match.start(1), match.end(1)))
        found.append(
            _span(
                "account_number",
                match.start(1),
                match.end(1),
                "account_labelled",
                "not_applicable",
                "medium",
                labelled="true",
            )
        )
    for sort_hit in sort_hits:
        window_end = min(len(text), sort_hit["end"] + 48)
        for match in EIGHT_DIGIT_RE.finditer(text, sort_hit["end"], window_end):
            key = (match.start(1), match.end(1))
            if key in occupied or key in crn_spans:
                continue
            occupied.add(key)
            found.append(
                _span(
                    "account_number",
                    match.start(1),
                    match.end(1),
                    "account_after_sort_code",
                    "not_applicable",
                    "medium",
                    labelled="false",
                )
            )
    return found


def _postcodes(text: str) -> list[dict]:
    found = []
    for match in POSTCODE_RE.finditer(text):
        found.append(
            _span(
                "postcode",
                match.start(),
                match.end(),
                "uk_postcode_shape",
                "not_applicable",
                "medium",
            )
        )
    return found


def _crns(text: str) -> list[dict]:
    found = []
    seen: set[tuple[int, int]] = set()
    for match in CRN_RE.finditer(text):
        prefix = match.group(1).upper()
        if prefix not in CRN_PREFIXES:
            continue
        key = (match.start(), match.end())
        seen.add(key)
        found.append(
            _span(
                "crn",
                match.start(),
                match.end(),
                "crn_prefix",
                "not_applicable",
                "medium",
                prefix=prefix,
            )
        )
    for match in CRN_LABEL_RE.finditer(text):
        key = (match.start(1), match.end(1))
        if key in seen:
            continue
        seen.add(key)
        found.append(
            _span(
                "crn",
                match.start(1),
                match.end(1),
                "crn_labelled",
                "not_applicable",
                "medium",
                prefix="none",
            )
        )
    return found


def _utrs(text: str) -> list[dict]:
    found = []
    for match in UTR_RE.finditer(text):
        found.append(
            _span(
                "utr",
                match.start(1),
                match.end(1),
                "utr_labelled",
                "not_checked",
                "medium",
            )
        )
    return found


def _overlaps(left: dict, right: dict) -> bool:
    return left["start"] < right["end"] and right["start"] < left["end"]


def _resolve(candidates: list[dict]) -> list[dict]:
    ordered = sorted(
        candidates,
        key=lambda item: (
            PRIORITY[item["entity_type"]],
            0 if item["checksum"] == "passed" else 1,
            item["start"],
            -(item["end"] - item["start"]),
        ),
    )
    kept: list[dict] = []
    for candidate in ordered:
        if any(_overlaps(candidate, earlier) for earlier in kept):
            continue
        kept.append(candidate)
    kept.sort(key=lambda item: item["start"])
    return kept


def detect(text: str) -> dict:
    """Return proposed spans and spans the rules deliberately skipped.

    The matched characters are not copied onto either list.
    """

    nino_hits = _ninos(text)
    iban_hits = _ibans(text)
    nhs_hits, nhs_skipped = _nhs(text)
    sort_hits, sort_skipped = _sort_codes(text)
    account_hits = _accounts(text, sort_hits, _labelled_crn_spans(text))
    findings = _resolve(
        nino_hits
        + iban_hits
        + nhs_hits
        + sort_hits
        + account_hits
        + _postcodes(text)
        + _crns(text)
        + _utrs(text)
    )
    return {"findings": findings, "not_redacted": nhs_skipped + sort_skipped}
