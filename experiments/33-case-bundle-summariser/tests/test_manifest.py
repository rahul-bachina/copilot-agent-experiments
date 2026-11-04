"""The permissions manifest stays inside the local YAML subset and the A0 boundary."""

from pathlib import Path

from src.manifest_yaml import load_yaml

ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> dict:
    return load_yaml((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))


def test_manifest_identity_and_autonomy():
    manifest = _manifest()
    assert manifest["agent"]["id"] == "exp-33-case-bundle-summariser"
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["autonomy"]["human_in_the_loop"] is True
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False


def test_high_risk_actions_are_disabled():
    high_risk = _manifest()["high_risk_actions"]
    for action in (
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ):
        assert high_risk[action]["enabled"] is False
    names = {row["action_name"] for row in high_risk["additional_high_risk"]}
    assert "Recommend an outcome" in names
    for row in high_risk["additional_high_risk"]:
        assert row["enabled"] is False


def test_decision_maker_reviews_every_cited_sentence():
    points = _manifest()["human_approval"]["approval_points"]
    review = next(point for point in points if point["action"] == "Review every cited sentence")
    assert review["approver"] == "Decision-maker"
    assert review["mandatory"] is True
    for action in (
        "Decide any case outcome",
        "Make a disclosure decision",
        "Make a credibility finding",
    ):
        point = next(row for row in points if row["action"] == action)
        assert point["approver"] == "Decision-maker"
        assert point["mandatory"] is True
