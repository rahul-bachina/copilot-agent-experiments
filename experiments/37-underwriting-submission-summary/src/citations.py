"""One verdict per stated fact. The cited lines have to contain it.

Support means the fact text, after case and whitespace are folded, is a
contiguous part of the cited lines. A shared word is not enough. A paraphrase
fails. That is stricter than Experiment 29's token check.

Numbers and dates use Experiment 29's boundary check: a number must appear as
its own digit run, and an ISO date must appear as written. A later failure is
listed and is not added to the failure count.

A field with no usable paragraph is not a failed fact. It is "not stated".
"""

from __future__ import annotations

import importlib.util
import re
from datetime import date
from pathlib import Path
from typing import Any

from .injection import injection_codes, prohibited_codes

VERDICTS = (
    "supported",
    "citation_missing",
    "pinpoint_incomplete",
    "citation_not_in_submission",
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
    "citation_not_in_submission",
    "pinpoint_not_in_document",
    "prohibited_action",
    "untrusted_instruction",
    "withheld_identifier",
    "stale_or_superseded",
    "number_or_date_mismatch",
    "span_does_not_support",
)

_PIN_FIELDS = ("document_id", "page", "paragraph", "line_start", "line_end")
_NOT_CURRENT_INTAKE = frozenset({"stale", "missing", "future", "invalid"})


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


def _load_experiment_29():
    """Load Experiment 29's number and date helpers without using its verdict.

    score.py imports tokens by inserting its own directory. The token overlap
    verdict in that module is not used. A paraphrase still fails here.
    """
    score_path = (
        Path(__file__).resolve().parents[2] / "29-groundedness-evaluation" / "src" / "score.py"
    )
    if not score_path.is_file():
        raise RuntimeError(
            "Experiment 29 is not beside this experiment. The number check will not be invented."
        )
    spec = importlib.util.spec_from_file_location("exp29_score_for_b006", score_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Experiment 29 score.py could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("extract_numbers", "extract_dates", "number_in", "normalise"):
        if not hasattr(module, name):
            raise RuntimeError(f"Experiment 29 score.py has no {name}.")
    return module


_EXPERIMENT_29 = None


def experiment_29():
    global _EXPERIMENT_29
    if _EXPERIMENT_29 is None:
        _EXPERIMENT_29 = _load_experiment_29()
    return _EXPERIMENT_29


def document_block_reason(
    document: dict[str, Any],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> str | None:
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


def resolve_span(
    document: dict[str, Any], page: int, paragraph: int, line_start: int, line_end: int
) -> str | None:
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


def _block_to_verdict(reason: str | None) -> str | None:
    if reason is None:
        return None
    if reason == "withheld_identifier":
        return "withheld_identifier"
    if reason in {"not_in_intake", "intake_not_read"}:
        return "stale_or_superseded"
    return "stale_or_superseded"


def numbers_or_dates_mismatch(text: str, span: str) -> bool:
    checker = experiment_29()
    if any(not checker.number_in(number, span) for number in checker.extract_numbers(text)):
        return True
    folded = checker.normalise(span)
    for item in checker.extract_dates(text):
        if checker.normalise(item) not in folded:
            return True
    return False


def check_fact(
    fact: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the fact plus one verdict. other_failures are not a second count."""
    text = str(fact.get("text") or "")
    citation = fact.get("citation") if isinstance(fact.get("citation"), dict) else None
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
                failures.append("citation_not_in_submission")
            else:
                span = resolve_span(document, page, paragraph, line_start, line_end)
                if span is None:
                    failures.append("pinpoint_not_in_document")
                else:
                    block_reason = document_block_reason(
                        document, as_of, stale_after_days, intake_files
                    )
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
        "fact_id": fact.get("fact_id"),
        "field": fact.get("field"),
        "text": text,
        "value": text if verdict == "supported" else text,
        "status": "stated",
        "citation": citation,
        "verdict": verdict,
        "other_failures": other,
        "block_reason": block_reason,
        "experiment_29_number_check": True,
    }


def empty_verdict_counts() -> dict[str, int]:
    return {name: 0 for name in VERDICTS}
