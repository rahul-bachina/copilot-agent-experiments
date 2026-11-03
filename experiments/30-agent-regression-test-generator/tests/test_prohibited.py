"""The generator refuses merge, push, approval, and a write into the agent."""

import json
import subprocess
import sys

import pytest

from src.generate import (
    ProhibitedAction,
    approve_generated_tests,
    assert_out_dir_allowed,
    edit_agent_under_test,
    generate,
    merge_pull_request,
    open_pull_request,
    push_branch,
    write_proposed,
)
from tests.support import ROOT, bundle, minimal, safety


def test_functions_that_would_act_always_raise():
    with pytest.raises(ProhibitedAction):
        merge_pull_request()
    with pytest.raises(ProhibitedAction):
        push_branch()
    with pytest.raises(ProhibitedAction):
        edit_agent_under_test()
    with pytest.raises(ProhibitedAction):
        approve_generated_tests()
    with pytest.raises(ProhibitedAction):
        open_pull_request()


def test_a_request_to_push_main_is_refused_and_not_targeted():
    report = generate(bundle(requested_push_branch="main", requested_merge=True, requested_edit_agent=True), "2026-11-03")
    safety(report)
    assert report["push_request_refused"] is True
    assert report["protected_branch_named"] is True
    assert report["protected_branch_targeted"] is False
    assert report["merge_request_refused"] is True
    assert report["edit_request_refused"] is True
    assert report["summary"]["drafted"] == 16


def test_a_non_protected_branch_is_still_not_pushed():
    report = generate(bundle(requested_push_branch="feature/regression-draft"), "2026-11-03")
    safety(report)
    assert report["push_request_refused"] is True
    assert report["protected_branch_named"] is False


def test_a_climbing_path_is_refused():
    payload = bundle()
    payload["agent_under_test"]["path"] = "../secrets"
    with pytest.raises(ProhibitedAction):
        generate(payload, "2026-11-03")


def test_out_dir_inside_the_agent_path_is_refused(tmp_path):
    report = generate(bundle(), "2026-11-03")
    agent_dir = tmp_path / "agents" / "syn-housing-repairs"
    agent_dir.mkdir(parents=True)
    with pytest.raises(ProhibitedAction):
        write_proposed(agent_dir, report)
    with pytest.raises(ProhibitedAction):
        assert_out_dir_allowed(tmp_path / "main", report["agent_under_test"]["path"])


def test_out_dir_elsewhere_writes_drafts_and_does_not_edit_the_agent(tmp_path):
    report = generate(bundle(), "2026-11-03")
    out = tmp_path / "drafts"
    write_proposed(out, report)
    case = out / "proposed-changes" / "syn-halebridge-repairs" / "cases" / "REG-OBS-FAIL-SEND-expected.json"
    assert case.is_file()
    body = json.loads(case.read_text(encoding="utf-8"))
    assert body["applied"] is False
    assert body["trace"]["requirement_id"] == "REQ-NO-SEND"
    skipped = out / "proposed-changes" / "syn-halebridge-repairs" / "cases" / "REG-OBS-DUP-LIGHT-expected.json"
    assert not skipped.exists()
    assert report["agent_under_test_edited"] is False


def test_cli_flags_exit_without_a_report(tmp_path):
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle()), encoding="utf-8")
    script = ROOT / "src" / "generate.py"
    for flag in ("--merge", "--push", "--approve", "--apply", "--open-pr"):
        completed = subprocess.run(
            [sys.executable, str(script), "--bundle", str(bundle_path), "--as-of", "2026-11-03", flag],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 2
        assert completed.stdout == ""


def test_autonomy_a3_is_not_recommended():
    payload = minimal()
    payload["agent_under_test"]["manifest"] = {
        "autonomy": {"level": "A3"},
        "high_risk_actions": {"external_send": {"enabled": False}},
        "tools": {"writes": {"enabled": False}, "sends": {"enabled": False}},
    }
    report = generate(payload, "2026-11-03")
    safety(report)
    assert report["a3_recommended"] is False
    assert report["manifest_reading"]["a3_requested"] is True
    case = next(item for item in report["cases"] if item["id"] == "REG-MANIFEST-not-a3")
    assert "Do not operate at autonomy A3" in case["expected_behaviour"]
    assert all("Operate this agent at autonomy A3" != item["expected_behaviour"] for item in report["cases"])


def test_skeleton_approval_and_a3_are_refused():
    approve = generate(minimal(request_manifest_skeleton=True, approve_manifest=True), "2026-11-03")
    safety(approve)
    assert approve["manifest_skeleton"]["approved"] is False
    assert approve["manifest_skeleton"]["experiment_03_called"] is False
    a3 = generate(minimal(request_manifest_skeleton=True, skeleton_autonomy="A3"), "2026-11-03")
    safety(a3)
    assert a3["manifest_skeleton"]["approved"] is False
    assert a3["manifest_skeleton"]["experiment_03_called"] is False
    assert a3["a3_recommended"] is False


def test_a_plain_skeleton_request_stays_unapproved():
    report = generate(minimal(request_manifest_skeleton=True, skeleton_autonomy="A1"), "2026-11-03")
    safety(report)
    skeleton = report["manifest_skeleton"]
    assert skeleton["approved"] is False
    assert skeleton["may_be_relied_on"] is False
    assert skeleton["high_risk_actions_enabled"] is False
    assert report["agent_under_test_edited"] is False
