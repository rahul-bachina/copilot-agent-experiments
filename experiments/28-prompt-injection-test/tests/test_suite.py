"""Suite 2026.1 stays a labelled synthetic catalogue."""

import base64
import codecs
import json

from src.owasp import CLASS_TO_OWASP, OWASP_2025
from src.suite import MARKER, SUITE_VERSION, build_suite, encode_marker
from tests.support import ROOT


def test_suite_version_and_count_are_stable():
    suite = build_suite()
    assert suite["suite_version"] == "2026.1"
    assert suite["case_count"] == 20
    assert len(suite["cases"]) == 20
    assert suite["not_for_production"] is True
    ids = [case["case_id"] for case in suite["cases"]]
    assert ids == [f"PI-{SUITE_VERSION}-{number:02d}" for number in range(1, 21)]
    assert len(set(ids)) == 20


def test_failure_signal_is_not_inside_the_probe():
    for case in build_suite()["cases"]:
        assert case["fixture_label"] == "SYNTHETIC TEST FIXTURE"
        assert case["failure_signal"] not in case["probe"]
        assert case["owasp_ids"] == [CLASS_TO_OWASP[case["class"]]]
        assert case["expected_safe"]["emit_failure_signal"] is False
        assert case["expected_safe"]["take_action"] is False


def test_channels_and_classes_match_the_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    classes = {case["class"] for case in build_suite()["cases"]}
    assert classes == {
        "instruction_override",
        "data_exfiltration",
        "tool_misuse",
        "prohibited_action",
        "system_prompt_disclosure",
        "encoding",
    }
    for name in classes:
        assert name in readme
    for rule in ("S1", "S2", "S3", "S4", "S5", "S6"):
        assert rule in readme
    channels = {case["channel"] for case in build_suite()["cases"]}
    assert channels == {"direct", "document", "email", "web", "tool_output"}


def test_encoding_cases_transform_only_the_marker():
    encoded = [case for case in build_suite()["cases"] if case["class"] == "encoding"]
    assert [case["encoding"] for case in encoded] == ["base64", "reversed", "rot13"]
    assert encode_marker("base64") == base64.b64encode(MARKER.encode("utf-8")).decode("ascii")
    assert encode_marker("reversed") == MARKER[::-1]
    assert encode_marker("rot13") == codecs.encode(MARKER, "rot13")
    for case in encoded:
        assert case["encoded_marker"] in case["probe"]
        assert MARKER not in case["probe"]
        assert case["encoded_marker"] != MARKER
        assert case["channel"] == "direct"


def test_committed_suite_matches_the_generator():
    path = ROOT / "fixtures" / "suite-2026.1.json"
    assert json.loads(path.read_text(encoding="utf-8")) == build_suite()


def test_owasp_titles_are_the_listing_headings():
    assert [row["id"] + " " + row["name"] for row in OWASP_2025] == [
        "LLM01:2025 Prompt Injection",
        "LLM02:2025 Sensitive Information Disclosure",
        "LLM03:2025 Supply Chain",
        "LLM04:2025 Data and Model Poisoning",
        "LLM05:2025 Improper Output Handling",
        "LLM06:2025 Excessive Agency",
        "LLM07:2025 System Prompt Leakage",
        "LLM08:2025 Vector and Embedding Weaknesses",
        "LLM09:2025 Misinformation",
        "LLM10:2025 Unbounded Consumption",
    ]
