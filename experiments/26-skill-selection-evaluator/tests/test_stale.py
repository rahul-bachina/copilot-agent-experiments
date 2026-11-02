"""A stale pin or a stale skill date is marked. The route is still computed."""

from src.report import evaluate

from tests.support import bundle, run, safety


def test_fresh_sample_is_inside_the_threshold():
    report = run("2026-11-02")
    safety(report)
    assert report["do_not_rely"] is False
    assert report["stale"]["sources_stale"] is False
    assert report["stale"]["skills_stale"] is False
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert boundary["reopened_for_this_experiment"] is False
    opened = [row for row in report["sources"] if row["stale_applicable"]]
    assert opened
    assert all(row["stale"] is False for row in opened)
    assert all(row["reopened_for_this_experiment"] is False for row in opened)
    assert report["agreement"]["percent"] == 100.0


def test_old_as_of_marks_the_pin_and_the_skills():
    report = run("2027-04-01")
    safety(report)
    assert report["do_not_rely"] is True
    assert report["stale"]["sources_stale"] is True
    assert report["stale"]["skills_stale"] is True
    opened = [row for row in report["sources"] if row["stale_applicable"]]
    assert all(row["stale"] is True for row in opened)
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert report["skills_edited"] is False
    assert report["diff_applied"] is False
    approvers = [point["action"] for point in report["human_approval"]]
    assert "Re-open a pinned page or a review date before relying on a citation" in approvers


def test_missing_skill_review_date_is_stale_and_routing_still_runs():
    payload = bundle()
    payload["skills"] = [
        {
            "id": "book-bulk-collection",
            "description": "Arrange a bulky waste collection, including the collection date and the items list.",
            "triggers": ["bulky waste"],
        }
    ]
    payload["utterances"] = [
        {
            "id": "bulk",
            "text": "Please book a bulky waste collection.",
            "expected": "skill:book-bulk-collection",
        }
    ]
    payload.pop("use_case", None)
    report = evaluate(payload, "2026-11-02")
    safety(report)
    assert report["stale"]["skills"][0]["stale"] is True
    assert report["stale"]["skills"][0]["reason"] == "No review date was supplied."
    assert report["do_not_rely"] is True
    assert report["utterances"][0]["predicted"] == "skill:book-bulk-collection"
    assert report["maintainer_validated"] is False
