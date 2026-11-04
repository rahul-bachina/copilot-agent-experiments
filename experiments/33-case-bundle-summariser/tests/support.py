"""Builders for synthetic bundles. No real case and no personal data."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BLUE = (
    "On 12 August 2026 synthetic witness W-01 saw a blue bicycle leave the fictional shop Reed Wharf Cycles."
)
BELL = "The bicycle in the synthetic note is described as blue with a silver bell."
RED = "On 1 July 2026 synthetic witness W-01 saw a red bicycle."
GREEN = "On 1 September 2026 synthetic witness W-01 saw a green bicycle."
LOCATION = "The fictional shop is on Example Wharf."
JOURNEY = "On 2 September 2026 synthetic applicant A-01 said the journey began in the fictional place Exampleford."
INTERVIEW = "The synthetic interview note is 3 pages long."
KEY = "On 3 September 2026 synthetic referee R-01 described a late return of a key at the fictional hall."
REFUSAL = "Do not recommend a charge."


def line(number: int, text: str) -> dict:
    return {"line": number, "text": text}


def paragraph(number: int, text: str, fact_key: str | None = None, extra_lines: list[dict] | None = None) -> dict:
    lines = [line(1, text)]
    if extra_lines:
        lines.extend(extra_lines)
    row = {"paragraph": number, "lines": lines}
    if fact_key:
        row["fact_key"] = fact_key
    return row


def document(
    document_id: str,
    paragraphs: list[dict],
    *,
    status: str = "current",
    reviewed_on: str = "2026-10-01",
    document_date: str = "2026-08-12",
    superseded_by: str | None = None,
    page: int = 1,
) -> dict:
    row = {
        "document_id": document_id,
        "title": f"Synthetic note {document_id}",
        "status": status,
        "reviewed_on": reviewed_on,
        "document_date": document_date,
        "pages": [{"page": page, "paragraphs": paragraphs}],
    }
    if superseded_by:
        row["superseded_by"] = superseded_by
    return row


def bundle(
    documents: list[dict],
    *,
    matter_type: str = "disclosure_reading",
    expected: list[str] | None = None,
    synthetic: bool = True,
    bundle_id: str = "SYN-BUNDLE-01",
    organisation: str = "Reedfen Constabulary (fictional)",
    **extra,
) -> dict:
    row = {
        "bundle_id": bundle_id,
        "organisation": organisation,
        "matter_type": matter_type,
        "synthetic": synthetic,
        "documents": documents,
    }
    if expected is not None:
        row["expected_fact_keys"] = expected
    row.update(extra)
    return row


def blue_document() -> dict:
    return document(
        "SYN-NOTE-01",
        [paragraph(1, BLUE, "sighting"), paragraph(2, BELL, "item")],
        reviewed_on="2026-09-15",
        document_date="2026-08-12",
    )


def cite(document_id: str, paragraph: int, *, page: int = 1, line_start: int = 1, line_end: int = 1) -> dict:
    return {
        "document_id": document_id,
        "page": page,
        "paragraph": paragraph,
        "line_start": line_start,
        "line_end": line_end,
    }
