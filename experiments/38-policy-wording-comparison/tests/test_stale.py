"""A stale pin and a stale document are not cleared by the comparison."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import compare
from tests.support import COVERAGE, clause, load_sample, pair

AS_OF = "2026-11-06"


def test_a_stale_endorsement_is_not_quoted():
    draft = compare(load_sample(), as_of=AS_OF)
    assert draft["not_used"][0]["document_id"] == "expiring-old"
    assert "flood_extension" not in {row["subject"] for row in draft["rows"]}
    assert "source_pin_stale" not in draft["do_not_rely_reasons"]
    opened = next(row for row in draft["sources"] if row["id"] == "ia2015-s17")
    assert opened["stale"] is False
    boundary = next(row for row in draft["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False


def test_a_stale_pin_sets_do_not_rely_and_does_not_clear_the_quote():
    payload = pair(
        [clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)],
        [clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)],
    )
    for wording in payload["wordings"]:
        wording["files"][0]["document_date"] = "2027-05-01"
        wording["documents"][0]["reviewed_on"] = "2027-05-01"
    draft = compare(payload, as_of="2027-05-06", stale_after_days=90)
    assert draft["do_not_rely"] is True
    assert "source_pin_stale" in draft["do_not_rely_reasons"]
    assert draft["rows"][0]["cells"][0]["quotes"][0]["verdict"] == "supported"
    assert draft["favourable_to"] is None
    opened = next(row for row in draft["sources"] if row["id"] == "ia2015-s3")
    assert opened["stale"] is True
    unread = next(row for row in draft["sources"] if row["id"] == "prin-2a-1-not-reread")
    assert unread["stale"] is False
    assert unread["reopened_for_this_experiment"] is False
