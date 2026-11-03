"""A stale pin is marked. The generator does not clear it and does not approve."""

from tests.support import run_bundle, safety


def test_pages_opened_on_3_november_2026_are_fresh_on_that_day():
    report = run_bundle(as_of="2026-11-03")
    safety(report)
    assert report["do_not_rely"] is False
    opened = [row for row in report["sources"] if row["stale_applicable"]]
    assert len(opened) == 5
    assert all(row["stale"] is False for row in opened)
    assert all(row["reopened_for_this_experiment"] is True for row in opened)
    assert all(row["last_verified"] == "2026-11-03" for row in opened)
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert boundary["stale_applicable"] is False
    assert boundary["reopened_for_this_experiment"] is False


def test_an_old_as_of_date_marks_the_pins_and_still_does_not_approve():
    report = run_bundle(as_of="2027-05-03", stale_after_days=90)
    safety(report)
    assert report["do_not_rely"] is True
    opened = [row for row in report["sources"] if row["stale_applicable"]]
    assert opened and all(row["stale"] is True for row in opened)
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert report["summary"]["drafted"] == 16
    assert report["maintainer_approved"] is False
    assert report["foundry_evaluation_called"] is False
