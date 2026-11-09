"""One verdict per summary sentence. The cited lines have to contain it.

Support means the sentence, after case and whitespace are folded, is a
contiguous part of the cited lines. A shared word is not enough. A paraphrase
fails. That is the same support rule as Experiment 33, applied to an event,
a paragraph, and a line rather than a document page.

Stale and superseded events fail the sentence even when the words match.
A sentence that copies a line Experiment 08 flagged is not supported.
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
    "citation_not_in_case",
    "pinpoint_not_in_event",
    "prohibited_action",
    "untrusted_instruction",
    "identifier_withheld",
    "stale_or_superseded",
    "span_does_not_support",
)

_PRIORITY = (
    "citation_missing",
    "pinpoint_incomplete",
    "citation_not_in_case",
    "pinpoint_not_in_event",
    "prohibited_action",
    "untrusted_instruction",
    "identifier_withheld",
    "stale_or_superseded",
    "span_does_not_support",
)

_PIN_FIELDS = ("event_id", "paragraph", "line_start", "line_end")


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


def event_block_reason(event: dict[str, Any], as_of: str, stale_after_days: int) -> str | None:
    """Why a whole event must not be quoted. None means it may be quoted."""
    status = event.get("status") or "current"
    if status != "current":
        return "superseded" if status == "superseded" else "status_not_current"
    if event.get("superseded_by"):
        return "superseded"
    recorded = event.get("recorded_on")
    try:
        recorded_on = date.fromisoformat(str(recorded))
        as_of_date = date.fromisoformat(as_of)
    except (TypeError, ValueError):
        return "recorded_date_missing_or_invalid"
    age = (as_of_date - recorded_on).days
    if age < 0:
        return "recorded_date_after_as_of"
    if age > stale_after_days:
        return "stale"
    return None


def index_events(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for event in events:
        event_id = str(event.get("event_id") or "").strip()
        if not event_id:
            raise ValueError("An event has no event_id.")
        if event_id in index:
            raise ValueError("Duplicate event id.")
        index[event_id] = event
    return index


def resolve_span(event: dict[str, Any], paragraph: int, line_start: int, line_end: int) -> str | None:
    if line_end < line_start:
        return None
    for para in event.get("paragraphs") or []:
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


def cited_lines_withheld(
    citation: dict[str, Any],
    withheld: set[tuple[str, int, int]],
) -> bool:
    event_id = str(citation.get("event_id") or "").strip()
    paragraph = _as_int(citation.get("paragraph"))
    line_start = _as_int(citation.get("line_start"))
    line_end = _as_int(citation.get("line_end"))
    if paragraph is None or line_start is None or line_end is None or line_end < line_start:
        return False
    for number in range(line_start, line_end + 1):
        if (event_id, paragraph, number) in withheld:
            return True
    return False


def _citation_failure(
    sentence: dict[str, Any],
    events: dict[str, dict[str, Any]],
) -> tuple[list[str], str | None]:
    citation = sentence.get("citation", "MISSING")
    if citation is None or citation == {} or citation == "MISSING":
        return ["citation_missing"], None
    if not isinstance(citation, dict):
        return ["pinpoint_incomplete"], None
    codes: list[str] = []
    if any(citation.get(field) in (None, "") for field in _PIN_FIELDS):
        codes.append("pinpoint_incomplete")
    event_id = str(citation.get("event_id") or "").strip()
    paragraph = _as_int(citation.get("paragraph"))
    line_start = _as_int(citation.get("line_start"))
    line_end = _as_int(citation.get("line_end"))
    if paragraph is None or line_start is None or line_end is None or not event_id:
        if "pinpoint_incomplete" not in codes:
            codes.append("pinpoint_incomplete")
    if not event_id or event_id not in events:
        codes.append("citation_not_in_case")
        return codes, None
    if paragraph is None or line_start is None or line_end is None:
        return codes, None
    span = resolve_span(events[event_id], paragraph, line_start, line_end)
    if span is None:
        codes.append("pinpoint_not_in_event")
        return codes, None
    return codes, span


def check_sentence(
    sentence: dict[str, Any],
    events: dict[str, dict[str, Any]],
    *,
    as_of: str,
    stale_after_days: int,
    withheld: set[tuple[str, int, int]],
    sentence_has_identifier: bool,
) -> dict[str, Any]:
    """Return the sentence plus one verdict and any other failures."""
    text = str(sentence.get("text") or "")
    codes, span = _citation_failure(sentence, events)
    if prohibited_codes(text):
        codes.append("prohibited_action")
    if injection_codes(text):
        codes.append("untrusted_instruction")
    citation = sentence.get("citation") if isinstance(sentence.get("citation"), dict) else {}
    if sentence_has_identifier or cited_lines_withheld(citation, withheld):
        codes.append("identifier_withheld")
    event_id = str(citation.get("event_id") or "").strip()
    event = events.get(event_id)
    if event is not None and "citation_not_in_case" not in codes and "pinpoint_not_in_event" not in codes:
        if "pinpoint_incomplete" not in codes and event_block_reason(event, as_of, stale_after_days):
            codes.append("stale_or_superseded")
    if span is None:
        if "citation_missing" not in codes and "pinpoint_incomplete" not in codes:
            if "citation_not_in_case" not in codes and "pinpoint_not_in_event" not in codes:
                codes.append("span_does_not_support")
    else:
        folded_sentence = normalise(text)
        folded_span = normalise(span)
        if not folded_sentence or folded_sentence not in folded_span:
            codes.append("span_does_not_support")
    ordered = [code for code in _PRIORITY if code in codes]
    verdict = ordered[0] if ordered else "supported"
    shown = text
    if "identifier_withheld" in ordered:
        shown = "[not copied: a UK identifier was in this sentence]"
    return {
        "sentence_id": sentence.get("sentence_id"),
        "text": shown,
        "fact_key": sentence.get("fact_key"),
        "citation": citation if citation else None,
        "verdict": verdict,
        "other_failures": ordered[1:],
        "span_resolved": span is not None and "identifier_withheld" not in ordered,
    }


def empty_verdict_counts() -> dict[str, int]:
    return {name: 0 for name in VERDICTS}
