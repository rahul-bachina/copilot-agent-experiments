"""Review dates and pinned pages go stale. The reviewer does not refresh them."""

from tests.support import AS_OF, run, safety


def test_an_old_review_date_is_stale_and_the_score_is_unchanged():
    fresh = run("halebridge.md")
    stale = run("halebridge.md", reviewed_on="2026-01-01")
    safety(stale)
    assert fresh["do_not_rely"] is False
    assert stale["do_not_rely"] is True
    assert stale["stale"]["documents_stale"] is True
    assert stale["stale"]["sources_stale"] is False
    assert stale["score"] == fresh["score"]
    assert any(point["approver"] == "Agent owner" and "review date" in point["action"] for point in stale["human_approval"])


def test_pinned_pages_go_stale_and_the_catalogue_boundary_does_not():
    report = run("halebridge.md", as_of="2027-04-01")
    safety(report)
    assert report["do_not_rely"] is True
    assert report["stale"]["sources_stale"] is True
    stale_ids = {row["id"] for row in report["sources"] if row["stale"]}
    fresh_ids = {row["id"] for row in report["sources"] if not row["stale"]}
    assert "cs-harnesses-overview" in stale_ids
    assert "catalogue-boundary" in fresh_ids
    assert all(row["reopened_for_this_experiment"] is False for row in report["sources"])
    assert report["network_called"] is False


def test_a_missing_review_date_is_stale():
    report = run("halebridge.md", reviewed_on=None)
    safety(report)
    assert report["stale"]["documents"][0]["stale"] is True
    assert report["do_not_rely"] is True
    assert report["as_of"] == AS_OF
