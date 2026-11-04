"""One verdict per summary sentence. The cited lines have to contain it.

Support means the sentence, after case and whitespace are folded, is a
contiguous part of the cited lines. A shared word is not enough. A paraphrase
fails. That is the difference from Experiment 29's token check.

Stale and superseded documents fail the sentence even when the words match.
A sentence with no citation fails. One sentence has one verdict. Later
failures are listed and are not added to the failure count.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from .injection import injection_codes, prohibited_codes

VERDICTS = (
    "supported",
    "citation_missing",
    "pinpoint_incomplete",
    "citation_not_in_bundle",
    "pinpoint_not_in_document",
    "prohibited_action",
    "untrusted_instruction",
    "stale_or_superseded",
    "span_does_not_support",
)

_PRIORITY = (
    "citation_missing",
    "pinpoint_incomplete",
    "citation_not_in_bundle",
    "pinpoint_not_in_document",
    "prohibited_action",
    "untrusted_instruction",
    "stale_or_superseded",
    "span_does_not_support",
)

_PIN_FIELDS = ("document_id", "page", "paragraph", "line_start", "line_end")


def normalise(text: str) -> str:
    text = (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
    return re.sub(r"\s+", " ", text).strip().casefold()


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"\d+", value.strip()):
        return int(value.strip())
    return None


def document_block_reason(document: dict[str, Any], as_of: str, stale_after_days: int) -> str | None:
    """Why a whole document must not be used. None means it may be quoted."""
    status = document.get("status")
    if status != "current":
        return "superseded" if status == "superseded" else "status_not_current"
    if document.get("superseded_by"):
        return "superseded"
    reviewed = document.get("reviewed_on")
    try:
        reviewed_on = date.fromisoformat(str(reviewed))
        as_of_date = date.fromisoformat(as_of)
    except (TypeError, ValueError):
        return "review_date_missing_or_invalid"
    age = (as_of_date - reviewed_on).days
    if age < 0:
        return "review_date_after_as_of"
    if age > stale_after_days:
        return "stale"
    return None


def index_documents(documents: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for document in documents:
        document_id = str(document.get("document_id") or "").strip()
        if not document_id:
            raise ValueError("A document has no document_id.")
        if document_id in index:
            raise ValueError(f"Duplicate document id {document_id}.")
        index[document_id] = document
    return index


def resolve_span(document: dict[str, Any], page: int, paragraph: int, line_start: int, line_end: int) -> str | None:
    if line_end < line_start:
        return None
    for page_row in document.get("pages") or []:
        if page_row.get("page") != page:
            continue
        for para in page_row.get("paragraphs") or []:
            if para.get("paragraph") != paragraph:
                continue
            lines = {
                row.get("line"): str(row.get("text") or "")
                for row in (para.get("lines") or [])
                if isinstance(row, dict)
            }
            collected: list[str] = []
            for number in range(line_start, line_end + 1):
                if number not in lines:
                    return None
                collected.append(lines[number].strip())
            return " ".join(part for part in collected if part)
    return None


def _citation_failure(sentence: dict[str, Any], documents: dict[str, dict[str, Any]]) -> tuple[list[str], str | None]:
    citation = sentence.get("citation", "MISSING")
    if citation is None or citation == {} or citation == "MISSING":
        return ["citation_missing"], None
    if not isinstance(citation, dict):
        return ["pinpoint_incomplete"], None
    codes: list[str] = []
    if any(citation.get(field) in (None, "") for field in _PIN_FIELDS):
        codes.append("pinpoint_incomplete")
    document_id = str(citation.get("document_id") or "").strip()
    page = _as_int(citation.get("page"))
    paragraph = _as_int(citation.get("paragraph"))
    line_start = _as_int(citation.get("line_start"))
    line_end = _as_int(citation.get("line_end"))
    if page is None or paragraph is None or line_start is None or line_end is None or not document_id:
        if "pinpoint_incomplete" not in codes:
            codes.append("pinpoint_incomplete")
    if not document_id or document_id not in documents:
        codes.append("citation_not_in_bundle")
        return codes, None
    if page is None or paragraph is None or line_start is None or line_end is None:
        return codes, None
    span = resolve_span(documents[document_id], page, paragraph, line_start, line_end)
    if span is None:
        codes.append("pinpoint_not_in_document")
        return codes, None
    return codes, span


def check_sentence(
    sentence: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    *,
    as_of: str,
    stale_after_days: int,
) -> dict[str, Any]:
    """Return the sentence plus one verdict and any other failures."""
    text = str(sentence.get("text") or "")
    codes, span = _citation_failure(sentence, documents)
    if prohibited_codes(text):
        codes.append("prohibited_action")
    if injection_codes(text):
        codes.append("untrusted_instruction")
    citation = sentence.get("citation") if isinstance(sentence.get("citation"), dict) else {}
    document_id = str(citation.get("document_id") or "").strip()
    document = documents.get(document_id)
    if document is not None and "citation_not_in_bundle" not in codes and "pinpoint_not_in_document" not in codes:
        if "pinpoint_incomplete" not in codes and document_block_reason(document, as_of, stale_after_days):
            codes.append("stale_or_superseded")
    if span is None:
        if "citation_missing" not in codes and "pinpoint_incomplete" not in codes:
            if "citation_not_in_bundle" not in codes and "pinpoint_not_in_document" not in codes:
                codes.append("span_does_not_support")
    else:
        folded_sentence = normalise(text)
        folded_span = normalise(span)
        if not folded_sentence or folded_sentence not in folded_span:
            codes.append("span_does_not_support")
    ordered = [code for code in _PRIORITY if code in codes]
    verdict = ordered[0] if ordered else "supported"
    return {
        "sentence_id": sentence.get("sentence_id"),
        "text": text,
        "fact_key": sentence.get("fact_key"),
        "citation": sentence.get("citation") if isinstance(sentence.get("citation"), dict) else None,
        "verdict": verdict,
        "other_failures": ordered[1:],
        "span_resolved": span is not None,
    }


def empty_verdict_counts() -> dict[str, int]:
    return {name: 0 for name in VERDICTS}
