"""Manifest reading, and the unapproved skeleton from Experiment 03's contract."""

from pathlib import Path

from src.manifest_bridge import draft_skeleton
from src.manifest_yaml import load_yaml
from tests.support import ROOT, run, safety

REPO = ROOT.parents[1]


def test_this_manifest_is_a0_and_cannot_write_or_send():
    manifest = load_yaml((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["agent"]["id"] == "exp-25-instruction-quality-reviewer"
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    point = next(item for item in manifest["human_approval"]["approval_points"] if item["action"] == "Approve prompt changes")
    assert point["approver"] == "Agent owner"
    assert point["mandatory"] is True
    for key in ("approve_reject", "regulated_decision", "production_record_change", "external_send", "spend_transact"):
        assert manifest["high_risk_actions"][key]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False


def test_experiment_14_manifest_parses_far_enough_to_compare_tools():
    manifest = load_yaml(
        (REPO / "experiments" / "14-agent-architecture-advisor" / "agent-manifest.yaml").read_text(encoding="utf-8")
    )
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    assert manifest["tools"]["allowed"]


def test_missing_manifest_drafts_an_unapproved_skeleton():
    report = run("halebridge.md", manifest=None)
    safety(report)
    skeleton = report["manifest_skeleton"]
    assert skeleton["generated"] is True
    assert skeleton["approved"] is False
    assert skeleton["may_be_relied_on"] is False
    assert skeleton["validation_passed"] is False or skeleton["experiment_03_called"] is True
    assert skeleton["autonomy_level"] == "A0"
    assert skeleton["high_risk_actions_enabled"] is False
    check = next(item for item in report["checks"] if item["id"] == "C8")
    assert check["result"] == "fail"
    assert any(point["approver"] == "Governance owner" for point in report["human_approval"])


def test_a3_and_approve_do_not_produce_an_approved_manifest():
    refused = draft_skeleton(
        bundle_id="syn-a3",
        title="Synthetic",
        as_of="2026-10-30",
        autonomy_level="A3",
        approve=False,
    )
    assert refused["approved"] is False
    assert refused["yaml"] is None
    assert refused["autonomy_level"] is None
    assert any("A3" in error for error in refused["errors"])
    blocked = draft_skeleton(
        bundle_id="syn-approve",
        title="Synthetic",
        as_of="2026-10-30",
        autonomy_level="A0",
        approve=True,
    )
    assert blocked["approved"] is False
    assert blocked["experiment_03_called"] is False
    assert blocked["yaml"] is None
    assert "cannot mark a manifest approved" in blocked["errors"][0]


def test_tool_schema_has_no_write_and_no_apply():
    import json

    tools = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    by_name = {tool["name"]: tool for tool in tools["tools"]}
    assert by_name["review_instructions"]["writes"] is False
    assert by_name["review_instructions"]["sends"] is False
    assert by_name["review_instructions"]["applies_diff"] is False
    assert by_name["apply_instruction_diff"]["callable_by_agent"] is False
    assert by_name["apply_instruction_diff"]["always_raises"] is True
    assert by_name["deploy_agent"]["always_raises"] is True
    assert by_name["send_findings"]["sends"] is False
    assert by_name["record_owner_approval"]["approver"] == "Agent owner"


def test_same_bundle_produces_the_same_report():
    first = run("halebridge.md")
    second = run("halebridge.md")
    assert first == second
