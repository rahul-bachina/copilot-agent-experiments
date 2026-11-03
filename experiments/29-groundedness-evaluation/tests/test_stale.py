"""Stale passages and stale pins are flagged. The catalogue row is not stale-tested."""

from tests.support import sample_report


def test_a_2024_review_date_flags_the_claim_and_does_not_release():
    draft = sample_report()
    # The sample passages were reviewed on 1 September 2026. Move the as-of date
    # past the draft 180-day window. 1 May 2027 is 242 days later.
    later = sample_report(as_of="2027-05-01")
    assert later["passages_stale"] is True
    assert later["summary"]["stale_claim_count"] == 3
    assert later["summary"]["verdicts"]["supported"] == 3
    assert later["summary"]["verdict_total"] == 3
    assert later["draft_bar_met"] is False
    assert later["do_not_rely"] is True
    assert later["release_decision"] is None
    assert draft["do_not_rely"] is False


def test_pin_staleness_does_not_change_the_claim_verdicts():
    draft = sample_report(as_of="2027-02-15")
    assert draft["pins_stale"] is True
    assert draft["passages_stale"] is False
    assert draft["summary"]["stale_claim_count"] == 0
    assert draft["summary"]["verdicts"]["supported"] == 3
    assert draft["do_not_rely"] is True
    boundary = next(row for row in draft["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert boundary["stale_applicable"] is False
    opened = [row for row in draft["sources"] if row["stale_applicable"]]
    assert opened and all(row["stale"] is True for row in opened)
