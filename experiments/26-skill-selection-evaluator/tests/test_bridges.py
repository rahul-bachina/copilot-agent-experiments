"""Experiments 25, 14, and 03 are called where they fit, and they cannot approve."""

from src.report import evaluate

from tests.support import bundle, run, safety


def test_sample_calls_experiment_25_and_14_and_not_a_replacement_manifest():
    report = run()
    safety(report)
    assert report["instruction_reviews"]
    assert all(row["called"] is True and row["experiment"] == "25" for row in report["instruction_reviews"])
    assert all(row["error"] is None for row in report["instruction_reviews"])
    vague = next(row for row in report["instruction_reviews"] if row["path"].endswith("vague-helper/SKILL.md"))
    assert vague["band"] != "no_gaps"
    architecture = report["architecture_cross_check"]
    assert architecture["called"] is True
    assert architecture["experiment"] == "14"
    assert architecture["platform_selected"] is None
    assert architecture["recommended_autonomy"] in {"A0", "A1", "A2"}
    assert report["manifest_skeleton"]["generated"] is False
    assert report["manifest_skeleton"]["approved"] is False
    assert report["manifest_skeleton"]["experiment_03_called"] is False


def test_missing_manifest_uses_an_unapproved_skeleton():
    payload = bundle()
    payload.pop("manifest")
    report = evaluate(payload, "2026-11-02")
    safety(report)
    skeleton = report["manifest_skeleton"]
    assert skeleton["generated"] is True
    assert skeleton["approved"] is False
    assert skeleton["may_be_relied_on"] is False
    assert skeleton["autonomy_level"] == "A0"
    assert skeleton["generator"] in {"local-stand-in", "experiment-03"}
    if skeleton["generator"] == "local-stand-in":
        assert skeleton["validation_passed"] is False
    approvers = [point["approver"] for point in report["human_approval"]]
    assert "Governance owner" in approvers


def test_a_request_for_autonomy_a3_does_not_become_the_recommendation():
    payload = bundle()
    payload["use_case"] = {
        "case_id": "northfen-a3",
        "title": "Northfen asked for A3",
        "organisation": {"name": "Northfen Borough Council", "licences": {"copilot_studio": "yes"}},
        "users": {"audience": "internal_staff", "channel": "teams"},
        "data": {"description": "Synthetic", "classification": "synthetic", "volume": "bounded"},
        "actions": {"read": True, "external_send": True, "approve_or_reject": True},
        "risk": {"requested_autonomy": "A3", "named_approver": False},
    }
    report = evaluate(payload, "2026-11-02")
    safety(report)
    assert report["a3_recommended"] is False
    assert report["architecture_cross_check"]["a3_recommended"] is False
    assert report["architecture_cross_check"]["recommended_autonomy"] in {"A0", "A1", "A2"}
    assert report["deployed"] is False
