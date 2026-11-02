"""Stale review dates and stale pins are marked and not refreshed."""

from tests.support import run, safety


def test_old_contract_review_date_is_stale_and_not_relied_on():
    report = run("clean-openapi.json", reviewed_on="2026-01-01")
    safety(report)
    assert report["do_not_rely"] is True
    assert report["stale"]["contract"]["stale"] is True
    assert report["stale"]["sources_stale"] is False
    assert report["owner_approved"] is False
    assert report["contract_modified"] is False
    assert any(point["action"].startswith("Re-open") for point in report["human_approval"])


def test_missing_review_date_is_stale():
    report = run("clean-openapi.json", reviewed_on=None)
    safety(report)
    assert report["stale"]["contract"]["stale"] is True
    assert report["do_not_rely"] is True


def test_pinned_pages_go_stale_after_the_threshold_and_the_boundary_does_not():
    report = run("clean-openapi.json", as_of="2027-05-01", extra={})
    # reviewed_on defaults to 2026-11-02, which is also older than 90 days on this as-of date
    safety(report)
    assert report["do_not_rely"] is True
    assert report["stale"]["sources_stale"] is True
    opened = [row for row in report["sources"] if row.get("stale_applicable")]
    assert opened and all(row["stale"] is True for row in opened)
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert boundary["stale_applicable"] is False
    assert report["network_called"] is False


def test_fresh_dates_are_not_stale():
    report = run("clean-openapi.json", as_of="2026-11-02")
    safety(report)
    assert report["do_not_rely"] is False
    assert report["stale"]["sources_stale"] is False
    assert all(row["reopened_for_this_experiment"] or not row["stale_applicable"] for row in report["sources"])
