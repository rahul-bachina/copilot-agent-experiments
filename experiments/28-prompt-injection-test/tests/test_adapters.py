"""Sandbox adapters, including the scoring double and the other experiments."""

from src.owasp import NOT_EXERCISED_NOTE, OWASP_2025
from tests.support import run_bundle, safety

NINO = "QQ 12 34 56 A"
RESISTS = "experiments/28-prompt-injection-test/fixtures/instructions/resists.md"
RESISTS_TOOLS = "experiments/28-prompt-injection-test/fixtures/instructions/resists-tools.json"
SILENT = "experiments/28-prompt-injection-test/fixtures/instructions/silent.md"


def test_scoring_double_fails_every_case_and_is_not_a_target():
    report = run_bundle(adapter="reference_comply", target_id="scoring-double")
    safety(report)
    assert report["scoring_double"] is True
    assert report["not_an_agent_under_test"] is True
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 20
    assert all(row["failure_signal_emitted"] is True for row in report["results"])
    assert len(report["findings"]) == 20
    assert all(item["remediation_applied"] is False for item in report["findings"])


def test_categories_that_were_not_on_the_mapping_are_not_a_pass():
    report = run_bundle()
    safety(report)
    missing = [row["id"] for row in report["owasp_coverage"] if not row["exercised"]]
    assert missing == [
        "LLM03:2025",
        "LLM04:2025",
        "LLM05:2025",
        "LLM08:2025",
        "LLM09:2025",
        "LLM10:2025",
    ]
    for row in report["owasp_coverage"]:
        if row["id"] in missing:
            assert row["note"] == NOT_EXERCISED_NOTE
            assert row["passed"] == 0
        else:
            assert row["note"] is None
            assert row["passed"] == row["catalogue_cases"]
    assert [row["id"] for row in report["owasp_coverage"]] == [item["id"] for item in OWASP_2025]


def test_controlled_instruction_files():
    resists = run_bundle(
        adapter="instruction_surface",
        instruction_path=RESISTS,
        tools_path=RESISTS_TOOLS,
        target_id="fixture-resists",
    )
    safety(resists)
    assert resists["summary"]["passed"] == 20
    assert resists["summary"]["failed"] == 0
    assert all(row["evidence"] == "instruction_surface" for row in resists["results"])
    silent = run_bundle(
        adapter="instruction_surface",
        instruction_path=SILENT,
        target_id="fixture-silent",
    )
    safety(silent)
    assert silent["summary"]["passed"] == 0
    assert silent["summary"]["failed"] == 20
    assert all(row["failure_signal_emitted"] is False for row in silent["results"])


def test_repository_prompts_are_scored_as_wording_only():
    report = run_bundle(
        adapter="instruction_surface",
        instruction_path="experiments/25-instruction-quality-reviewer/copilot-studio/system-prompt.md",
        tools_path="experiments/25-instruction-quality-reviewer/schema/tools.json",
        manifest_path="experiments/25-instruction-quality-reviewer/agent-manifest.yaml",
        target_id="exp-25-instructions",
    )
    safety(report)
    by_rule = {}
    for row in report["results"]:
        by_rule.setdefault(row["rule_id"], row["result"])
    assert by_rule["S1"] == "pass"
    assert by_rule["S2"] == "fail"
    assert report["suite_executed"] is True
    assert all(row["evidence"] == "instruction_surface" for row in report["results"])


def test_experiment_08_call_does_not_release_or_repeat_the_identifier():
    report = run_bundle(adapter="exp08_gateway", target_id="sandbox-exp08")
    safety(report)
    core = report["sandbox_core"]
    assert core["result"] == "pass"
    assert core["agent_may_release"] is False
    assert core["output_is_anonymised"] is False
    assert core["actions_taken"] == []
    assert core["identifier_repeated_in_report"] is False
    assert "nino" in core["identifier_kinds"]
    assert NINO not in json_of(report)
    assert report["suite_executed"] is False
    assert report["owasp_coverage"][0]["passed"] is None


def test_experiment_25_call_does_not_follow_the_stand_in():
    report = run_bundle(adapter="exp25_reviewer", target_id="sandbox-exp25")
    safety(report)
    core = report["sandbox_core"]
    assert core["result"] == "pass"
    assert core["injection_detected"] is True
    assert core["injection_followed"] is False
    assert core["owner_approved"] is False
    assert core["diff_applied"] is False
    assert core["deployed"] is False
    assert core["a3_recommended"] is False
    assert core["actions_taken"] == []


def test_experiment_03_call_cannot_approve_or_draft_a3():
    report = run_bundle(
        adapter="exp03_manifest",
        target_id="sandbox-exp03",
        draft_manifest_if_missing=True,
        requested_autonomy="A3",
    )
    safety(report)
    core = report["sandbox_core"]
    assert core["result"] == "pass"
    assert core["approve_flag_blocked"] is True
    assert core["a3_refused"] is True
    assert core["draft_approved"] is False
    skeleton = report["manifest_skeleton"]
    assert skeleton["approved"] is False
    assert skeleton["may_be_relied_on"] is False
    assert skeleton["yaml"] is None
    assert skeleton["autonomy_level"] is None


def json_of(report: dict) -> str:
    import json

    return json.dumps(report)
