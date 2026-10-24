"""The manifest generator validates a draft and cannot approve it."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import load_record  # noqa: E402
from generate_manifest import main  # noqa: E402
from lifecycle import ProhibitedAction  # noqa: E402
from manifest_generator import SCHEMA_PATH, generate_manifest, repo_schema  # noqa: E402


def _walk_approved(value):
    if isinstance(value, dict):
        if "approved" in value:
            assert value["approved"] is False
        if "approved_by_this_tool" in value:
            assert value["approved_by_this_tool"] is False
        for item in value.values():
            _walk_approved(item)
    elif isinstance(value, list):
        for item in value:
            _walk_approved(item)


def test_generated_manifest_validates_and_is_not_approved():
    record = load_record("exp-01-foi-triage")
    result = generate_manifest(record, "2026-10-24")
    assert result["validation_passed"] is True, result["errors"]
    assert result["approved"] is False
    assert result["approved_by"] is None
    assert result["manifest"]["draft_control"]["approved"] is False
    assert result["manifest"]["autonomy"]["level"] == "A1"
    assert result["manifest"]["autonomy"]["auto_actions_enabled"] is False
    for key in (
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ):
        assert result["manifest"]["high_risk_actions"][key]["enabled"] is False
    _walk_approved(result)
    Draft7Validator(repo_schema(), format_checker=Draft7Validator.FORMAT_CHECKER).validate(
        result["manifest"]
    )


def test_experiment_02_manifest_also_validates():
    result = generate_manifest(load_record("exp-02-consumer-duty-complaint-intake"), "2026-10-24")
    assert result["validation_passed"] is True, result["errors"]
    assert result["manifest"]["agent"]["id"] == "exp-02-consumer-duty-complaint-intake"


def test_a3_request_emits_no_manifest():
    result = generate_manifest(load_record("syn-a3-request"), "2026-10-24")
    assert result["validation_passed"] is False
    assert result["manifest"] is None
    assert result["yaml"] is None
    assert result["approved"] is False
    assert any("A3" in error for error in result["errors"])


def test_approve_flag_is_prohibited():
    record = load_record("exp-01-foi-triage")
    try:
        generate_manifest(record, "2026-10-24", approve=True)
    except ProhibitedAction:
        return
    raise AssertionError("approve=True must raise")


def test_inventory_claim_of_approval_is_ignored():
    record = load_record("exp-01-foi-triage")
    record["approved"] = True
    record["lifecycle_status"] = "approved_for_limited_use"
    result = generate_manifest(record, "2026-10-24")
    assert result["approved"] is False
    assert result["manifest"]["draft_control"]["approved"] is False
    assert result["validation_passed"] is True


def test_cli_refuses_approve_and_writes_nothing(tmp_path, capsys):
    inventory = Path(__file__).resolve().parents[1] / "fixtures" / "inventory" / "exp-01-foi-triage.json"
    output = tmp_path / "should-not-exist.yaml"
    code = main(
        [
            "--inventory",
            str(inventory),
            "--as-of",
            "2026-10-24",
            "--output",
            str(output),
            "--approve",
        ]
    )
    assert code == 2
    assert not output.exists()
    captured = capsys.readouterr().out
    payload = yaml.safe_load(captured)
    assert payload["approved"] is False


def test_cli_writes_a_valid_draft(tmp_path, capsys):
    inventory = Path(__file__).resolve().parents[1] / "fixtures" / "inventory" / "syn-stale-register.json"
    output = tmp_path / "draft.yaml"
    code = main(
        ["--inventory", str(inventory), "--as-of", "2026-10-24", "--output", str(output)]
    )
    assert code == 0
    loaded = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert loaded["draft_control"]["approved"] is False
    assert loaded["autonomy"]["level"] == "A0"
    Draft7Validator(repo_schema()).validate(loaded)
    assert SCHEMA_PATH.is_file()
