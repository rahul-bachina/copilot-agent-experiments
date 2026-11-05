"""A stale document or a stale pin is still shown as a reason not to rely."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import summarise  # noqa: E402
from tests.support import submission_with  # noqa: E402

LINE = "The proposal describes a commercial warehouse used to store dry goods."


def test_the_last_day_of_the_window_is_current_and_the_next_day_is_not():
    as_of = date(2026, 11, 5)
    current = submission_with([( "risk_description", LINE )])
    current["files"][0]["document_date"] = (as_of - timedelta(days=90)).isoformat()
    current["documents"][0]["reviewed_on"] = current["files"][0]["document_date"]
    draft = summarise(current, as_of=as_of.isoformat(), stale_after_days=90)
    assert draft["sections"]["risk_description"]["status"] == "stated"
    assert draft["facts"][0]["verdict"] == "supported"

    stale = submission_with([("risk_description", LINE)])
    stale["files"][0]["document_date"] = (as_of - timedelta(days=91)).isoformat()
    stale["documents"][0]["reviewed_on"] = stale["files"][0]["document_date"]
    draft = summarise(stale, as_of=as_of.isoformat(), stale_after_days=90)
    assert draft["sections"]["risk_description"]["status"] == "not_stated"
    assert draft["not_used"][0]["reason"] == "intake_date_not_current"
    assert "intake_or_document_not_current" in draft["do_not_rely_reasons"]
    assert draft["coverage_decision"] is None


def test_a_future_review_date_is_not_quoted():
    payload = submission_with([("risk_description", LINE)])
    payload["documents"][0]["reviewed_on"] = "2026-12-01"
    draft = summarise(payload, as_of="2026-11-05")
    assert draft["not_used"][0]["reason"] == "review_date_after_as_of"
    assert draft["sections"]["risk_description"]["status"] == "not_stated"


def test_a_stale_pin_is_marked_and_the_quote_can_still_be_current():
    payload = submission_with([("risk_description", LINE)])
    payload["files"][0]["document_date"] = "2027-02-01"
    payload["documents"][0]["reviewed_on"] = "2027-02-01"
    draft = summarise(payload, as_of="2027-02-10", stale_after_days=90)
    assert draft["facts"][0]["verdict"] == "supported"
    assert "source_pin_stale" in draft["do_not_rely_reasons"]
    opened = [row for row in draft["sources"] if row["id"] == "ia2015-s3"]
    assert opened[0]["stale"] is True
    untouched = [row for row in draft["sources"] if row["id"] == "catalogue-boundary"]
    assert untouched[0]["stale"] is False
    assert draft["checker_passed"] is True
    assert draft["do_not_rely"] is True
