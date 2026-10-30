"""The reviewer does not apply, approve, send, or deploy."""

import pytest

from src.review import ProhibitedAction, main, review
from tests.support import MANIFEST, bundle_for, run, safety, text_of


def test_a_command_to_send_deploy_and_set_a3_fails_and_is_not_done():
    report = run("prohibited-send.md")
    safety(report)
    commands = [hit for hit in report["actions_seen"] if hit["polarity"] == "command"]
    ids = {hit["id"] for hit in commands}
    assert "external_send" in ids
    assert "deploy" in ids
    assert "autonomy_a3" in ids
    assert "approve_or_reject" in ids
    assert "production_write" in ids
    assert report["a3_recommended"] is False
    assert report["deployed"] is False
    assert report["diff_applied"] is False


def test_a_human_approval_line_is_not_a_command_to_approve():
    report = run("halebridge.md")
    commands = [hit for hit in report["actions_seen"] if hit["polarity"] == "command"]
    assert commands == []
    checkpoints = [hit for hit in report["actions_seen"] if hit["polarity"] == "checkpoint"]
    assert any(hit["id"] == "approve_or_reject" for hit in checkpoints)


def test_approve_and_apply_flags_raise_and_write_nothing(capsys):
    bundle = bundle_for("halebridge.md")
    with pytest.raises(ProhibitedAction):
        review(bundle, "2026-10-30", approve=True)
    with pytest.raises(ProhibitedAction):
        review(bundle, "2026-10-30", apply=True)
    assert capsys.readouterr().out == ""


def test_cli_refuses_approve_and_apply(tmp_path):
    path = tmp_path / "bundle.json"
    path.write_text(
        '{"bundle_id":"x","documents":[{"path":"a.md","kind":"system_prompt","reviewed_on":"2026-10-30","text":'
        + __import__("json").dumps(text_of("halebridge.md"))
        + "}],"
        + '"manifest":' + __import__("json").dumps(MANIFEST) + "}",
        encoding="utf-8",
    )
    assert main(["--bundle", str(path), "--as-of", "2026-10-30", "--approve"]) == 2
    assert main(["--bundle", str(path), "--as-of", "2026-10-30", "--apply"]) == 2
    assert list(tmp_path.iterdir()) == [path]


def test_manifest_that_enables_sends_disagrees_with_a_forbid():
    manifest = {
        "tools": {
            "allowed": [{"tool": "read_policy_file"}],
            "writes": {"enabled": False},
            "sends": {"enabled": True},
        },
        "autonomy": {"level": "A0"},
    }
    report = run("halebridge.md", manifest=manifest)
    safety(report)
    check = next(item for item in report["checks"] if item["id"] == "C8")
    assert check["result"] == "fail"
    assert "enables sends" in check["summary"]
    assert report["manifest_check"]["sends"] is True
