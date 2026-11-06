"""One verdict per quoted clause. The cited lines have to contain it.

Support means the quote, after case and whitespace are folded, is a contiguous
part of the cited lines. That rule is Experiment 33's normalise and resolve_span.
A paraphrase fails. Numbers and ISO dates are checked with Experiment 29.
A shared word is not enough.

Stale and withheld documents fail the quote even when the words match.
A quote with no citation fails. One quote has one verdict. Later failures are
listed and are not added to the failure count.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from .injection import injection_codes, prohibited_codes
from .siblings import load

VERDICTS = (
    "supported",
    "citation_missing",
    "pinpoint_incomplete",
    "citation_not_in_pack",
    "pinpoint_not_in_document",
    "prohibited_action",
    "untrusted_instruction",
    "withheld_identifier",
    "stale_or_superseded",
    "number_or_date_mismatch",
    "span_does_not_support",
)

_PRIORITY = (
    "citation_missing",
    "pinpoint_incomplete",
    "citation_not_in_pack",
    "pinpoint_not_in_document",
    "prohibited_action",
    "untrusted_instruction",
    "withheld_identifier",
    "stale_or_superseded",
    "number_or_date_mismatch",
    "span_does_not_support",
)

_PIN_FIELDS = ("document_id", "clause_ref", "page", "paragraph", "line_start", "line_end")
_NOT_CURRENT_INTAKE = frozenset({"stale", "missing", "future", "invalid"})
_BASIS = re.compile(r"\bbasis of (?:the )?contract\b", re.I)


def normalise(text: str) -> str:
    return load()["citation_normalise"](text)


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"\d+", value.strip()):
        return int(value.strip())
    return None


def document_block_reason(
    document: dict[str, Any],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> str | None:
    """Why a whole document must not be quoted. None means it may be quoted."""
    file_id = document.get("file_id")
    if not isinstance(file_id, str) or file_id not in intake_files:
        return "not_in_intake"
    row = intake_files[file_id]
    if row["read_status"] != "read":
        return "intake_not_read"
    if row["date_status"] in _NOT_CURRENT_INTAKE:
        return "intake_date_not_current"
    if row["finding_count"] > 0:
        return "withheld_identifier"
    status = document.get("status")
    if status != "current":
        return "superseded" if status == "superseded" else "status_not_current"
    if document.get("superseded_by"):
        return "superseded"
    try:
        reviewed_on = date.fromisoformat(str(document.get("reviewed_on")))
        as_of_date = date.fromisoformat(as_of)
    except (TypeError, ValueError):
        return "review_date_missing_or_invalid"
    age = (as_of_date - reviewed_on).days
    if age < 0:
        return "review_date_after_as_of"
    if age > stale_after_days:
        return "stale"
    return None


def _block_to_verdict(reason: str | None) -> str | None:
    if reason is None:
        return None
    if reason == "withheld_identifier":
        return "withheld_identifier"
    return "stale_or_superseded"


def numbers_or_dates_mismatch(text: str, span: str) -> bool:
    checker = load()["score"]
    if any(not checker.number_in(number, span) for number in checker.extract_numbers(text)):
        return True
    folded = checker.normalise(span)
    for item in checker.extract_dates(text):
        if checker.normalise(item) not in folded:
            return True
    return False


def _paragraph_clause_ref(document: dict[str, Any], page: int, paragraph: int) -> str | None:
    for page_row in document.get("pages") or []:
        if page_row.get("page") != page:
            continue
        for para in page_row.get("paragraphs") or []:
            if para.get("paragraph") == paragraph:
                ref = para.get("clause_ref")
                if isinstance(ref, str) and ref.strip():
                    return ref.strip()
                return None
    return None


def basis_of_contract_words(text: str) -> bool:
    return bool(_BASIS.search(text or ""))


def check_quote(
    quote: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the quote plus one verdict. other_failures are not a second count."""
    siblings = load()
    text = str(quote.get("text") or "")
    citation = quote.get("citation") if isinstance(quote.get("citation"), dict) else None
    failures: list[str] = []
    span = None
    block_reason = None
    if not citation:
        failures.append("citation_missing")
    else:
        missing = [field for field in _PIN_FIELDS if citation.get(field) in (None, "")]
        page = _as_int(citation.get("page"))
        paragraph = _as_int(citation.get("paragraph"))
        line_start = _as_int(citation.get("line_start"))
        line_end = _as_int(citation.get("line_end"))
        if missing or None in {page, paragraph, line_start, line_end}:
            failures.append("pinpoint_incomplete")
        else:
            document_id = str(citation.get("document_id") or "").strip()
            document = documents.get(document_id)
            if document is None:
                failures.append("citation_not_in_pack")
            else:
                span = siblings["resolve_span"](document, page, paragraph, line_start, line_end)
                cited_ref = str(citation.get("clause_ref") or "").strip()
                actual_ref = _paragraph_clause_ref(document, page, paragraph)
                if span is None or actual_ref != cited_ref:
                    failures.append("pinpoint_not_in_document")
                    span = None if span is None or actual_ref != cited_ref else span
                else:
                    block_reason = document_block_reason(document, as_of, stale_after_days, intake_files)
    if prohibited_codes(text):
        failures.append("prohibited_action")
    if injection_codes(text):
        failures.append("untrusted_instruction")
    mapped = _block_to_verdict(block_reason)
    if mapped:
        failures.append(mapped)
    if span is not None and numbers_or_dates_mismatch(text, span):
        failures.append("number_or_date_mismatch")
    if span is not None and normalise(text) not in normalise(span):
        failures.append("span_does_not_support")
    if not failures:
        verdict = "supported"
        other: list[str] = []
    else:
        verdict = next(name for name in _PRIORITY if name in failures)
        other = [name for name in _PRIORITY if name in failures and name != verdict]
    return {
        "text": text,
        "inferred": False,
        "citation": citation,
        "verdict": verdict,
        "other_failures": other,
        "block_reason": block_reason,
        "basis_of_contract_words": basis_of_contract_words(text) if verdict == "supported" else False,
        "basis_clause_of_no_effect": None,
        "experiment_33_span_check": True,
        "experiment_29_number_check": True,
    }


def empty_verdict_counts() -> dict[str, int]:
    return {name: 0 for name in VERDICTS}
