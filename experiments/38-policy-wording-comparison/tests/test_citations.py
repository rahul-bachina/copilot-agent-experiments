"""A paraphrase fails. A missing pinpoint fails. A number has to be in the line."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import compare
from tests.support import load_sample

AS_OF = "2026-11-06"
CITATION = {
    "wording_id": "expiring",
    "document_id": "expiring-wording",
    "clause_ref": "2.1",
    "page": 1,
    "paragraph": 6,
    "line_start": 1,
    "line_end": 1,
}


def _proposed(text: str, citation):
    return compare(
        load_sample(),
        as_of=AS_OF,
        proposed_cells=[
            {
                "topic": "limit",
                "subject": "buildings",
                "wording_id": "expiring",
                "text": text,
                "citation": citation,
            }
        ],
    )


def test_a_paraphrase_fails_the_span():
    draft = _proposed("The maximum payable for buildings is GBP 2500000, in other words.", CITATION)
    quote = draft["rows"][0]["cells"][0]["quotes"][0]
    assert quote["verdict"] == "span_does_not_support"
    assert draft["checker_passed"] is False
    assert draft["summary"]["verdict_total"] == draft["summary"]["stated_cell_count"] == 1


def test_a_changed_number_fails_before_the_span():
    draft = _proposed("The maximum payable for buildings is GBP 9999999 any one occurrence.", CITATION)
    assert draft["rows"][0]["cells"][0]["quotes"][0]["verdict"] == "number_or_date_mismatch"
    assert draft["summary"]["failure_count"] == 1


def test_a_missing_citation_is_one_failure():
    draft = _proposed("The maximum payable for buildings is GBP 2500000 any one occurrence.", None)
    quote = draft["rows"][0]["cells"][0]["quotes"][0]
    assert quote["verdict"] == "citation_missing"
    assert quote["other_failures"] == [] or "citation_missing" not in quote["other_failures"]
    assert draft["summary"]["failure_count"] == 1
