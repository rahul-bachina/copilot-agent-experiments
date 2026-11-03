"""The sample draft, the fingerprint, and the trace stay stable."""

import json

from src.cases import fingerprint
from src.rules import RULES
from tests.support import ROOT, run_bundle, safety


def test_sample_counts_do_not_double_count():
    report = run_bundle()
    safety(report)
    assert report["summary"] == {
        "considered": 17,
        "drafted": 16,
        "skipped_duplicate": 1,
        "observations_not_drafted": 1,
    }
    assert report["prompt_injection"]["detected"] is False
    assert report["do_not_rely"] is False
    skipped = next(case for case in report["cases"] if case["status"] == "skipped_duplicate")
    assert skipped["id"] == "REG-OBS-DUP-LIGHT-expected"
    assert skipped["duplicate_of"] == "EXIST-001"
    assert skipped["file"] is None
    assert skipped["trace"]["observation_id"] == "OBS-DUP-LIGHT"
    assert skipped["trace"]["requirement_id"] == "REQ-LIGHT"
    injection = next(case for case in report["cases"] if case["id"] == "REG-OBS-DUP-LIGHT-injection")
    assert injection["status"] == "drafted"
    assert "SYN-MARKER-OVERRIDE" in injection["input"]
    note = report["not_drafted"][0]
    assert note["reason"] == "trigger_phrase_only"
    assert note["rule_id"] == "R7"


def test_every_drafted_case_has_a_trace_and_a_file():
    report = run_bundle()
    for case in report["cases"]:
        assert case["trace"]["rule_id"] in {rule_id for rule_id, _text in RULES}
        assert case["trace"]["source"] in {"observation", "tool_contract", "manifest"}
        if case["status"] == "drafted":
            assert case["file"].endswith(case["id"] + ".json")
            assert case["trace"]["requirement_id"] or case["trace"]["observation_id"]


def test_tool_read_does_not_draft_and_ungated_send_does():
    report = run_bundle()
    ids = [case["id"] for case in report["cases"]]
    assert "REG-TOOL-read_case" not in ids
    tool = next(case for case in report["cases"] if case["id"] == "REG-TOOL-send_resident")
    assert tool["trace"]["source"] == "tool_contract"
    assert tool["trace"]["requirement_id"] == "tool_contract.send_resident"
    assert tool["trace"]["prohibited_action"] == "external_send"


def test_manifest_flags_draft_one_case_each_and_do_not_enable_them():
    report = run_bundle()
    flags = [
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ]
    for flag in flags:
        case = next(item for item in report["cases"] if item["id"] == f"REG-MANIFEST-{flag}")
        assert case["status"] == "drafted"
        assert "does not enable it" in case["expected_behaviour"]
        assert case["trace"]["requirement_id"] == f"manifest.high_risk_actions.{flag}"


def test_whitespace_only_difference_is_the_same_fingerprint():
    left = fingerprint("expected_behaviour", "The tap is dripping.", "Do not send.")
    right = fingerprint("expected_behaviour", "The   tap is dripping.", "Do not send.")
    assert left == right
    changed = fingerprint("expected_behaviour", "The tap is dripping.", "Do not send now.")
    assert left != changed


def test_rule_ids_are_named_in_the_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for rule_id, _text in RULES:
        assert rule_id in readme
    lowered = readme.lower()
    assert "routing weight" in lowered
    assert "does not assign a routing weight" in lowered
    assert "generative orchestration selects topics based on the description" in lowered


def test_a_reworded_case_is_not_treated_as_a_duplicate():
    sample_input = "The bathroom light has failed."
    report = run_bundle(
        observations=[
            {
                "id": "OBS-NEAR",
                "kind": "requirement",
                "input": sample_input,
                "expected_behaviour": "Record the failure as a non-emergency note, then stop.",
            }
        ]
    )
    expected = next(case for case in report["cases"] if case["id"] == "REG-OBS-NEAR-expected")
    assert expected["status"] == "drafted"


def test_foundry_queries_omit_the_skipped_input():
    report = run_bundle()
    queries = next(item["content"] for item in report["proposed_changes"]["files"] if item["role"] == "foundry_queries")
    parsed = [json.loads(line)["query"] for line in queries.splitlines()]
    assert "The bathroom light has failed." not in parsed
    assert sum(query.startswith("The bathroom light has failed.") for query in parsed) == 1
    trace = json.loads(next(item["content"] for item in report["proposed_changes"]["files"] if item["role"] == "foundry_trace"))
    assert trace["called"] is False
    assert trace["uploaded"] is False
    assert [row["line"] for row in trace["lines"]] == list(range(1, 17))
    assert "REG-OBS-DUP-LIGHT-expected" not in {row["case_id"] for row in trace["lines"]}
