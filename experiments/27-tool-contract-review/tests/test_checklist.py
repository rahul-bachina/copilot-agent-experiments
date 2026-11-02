"""Checklist results on synthetic contracts."""

from pathlib import Path

from tests.support import MANIFEST, USE_CASE, result_map, run, safety


def test_readme_lists_every_check():
    from src.checklist import CHECKS

    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    for check in CHECKS:
        assert f"| {check['id']} |" in readme
        assert check["name"] in readme


def test_clean_openapi_meets_the_checklist():
    report = run("clean-openapi.json", extra={"use_case": USE_CASE})
    safety(report)
    assert report["score"]["band"] == "no_gaps"
    assert report["score"]["percent"] == 100.0
    assert report["score"]["points"] == 18
    assert report["blocking"] == []
    assert report["do_not_rely"] is False
    assert report["proposed_diff"]["policy_xml"] is None
    assert report["proposed_diff"]["contract_notes"] == []
    assert report["architecture_cross_check"]["called"] is True
    assert report["architecture_cross_check"]["recommended_autonomy"] == "A0"
    assert report["architecture_cross_check"]["any_option_selected"] is False
    assert report["architecture_cross_check"]["disagreement"] is None
    assert report["manifest_skeleton"]["generated"] is False
    assert report["instruction_review"]["called"] is False


def test_each_gap_is_the_check_it_claims():
    expected = {
        "wildcard.json": {"C1": "fail"},
        "broad-scope.json": {"C1": "fail", "C5": "partial"},
        "unbounded-write.json": {"C4": "fail"},
        "secret-in-spec.json": {"C5": "fail"},
        "apikey-only.json": {"C5": "fail"},
        "special-category.json": {"C6": "fail"},
        "no-rate-limit.json": {"C7": "fail"},
        "renewal-too-long.json": {"C7": "fail"},
        "stack-trace.json": {"C8": "fail"},
        "injection-description.json": {"C9": "fail"},
    }
    write_manifest = {
        "tools": {
            "allowed": [{"tool": "updateCase"}],
            "writes": {"enabled": True},
            "sends": {"enabled": False},
        },
        "autonomy": {"level": "A0"},
    }
    for name, results in expected.items():
        manifest = write_manifest if name == "unbounded-write.json" else MANIFEST
        report = run(name, manifest=manifest)
        safety(report)
        actual = result_map(report)
        for check_id, result in results.items():
            assert actual[check_id] == result, name
        assert report["score"]["band"] == "blocking"


def test_delete_without_a_gate_fails_only_the_gate_when_the_manifest_allows_writes():
    manifest = {
        "tools": {
            "allowed": [{"tool": "deleteCase"}],
            "writes": {"enabled": True},
            "sends": {"enabled": False},
        },
        "autonomy": {"level": "A0"},
    }
    report = run("delete-no-gate.json", manifest=manifest)
    safety(report)
    assert result_map(report)["C3"] == "fail"
    assert result_map(report)["C2"] == "pass"
    assert "deleteCase" in report["checks"][2]["evidence"][0]


def test_delete_against_a_read_manifest_also_fails_consistency():
    report = run("delete-no-gate.json")
    safety(report)
    assert result_map(report)["C2"] == "fail"
    assert result_map(report)["C3"] == "fail"


def test_missing_manifest_is_a_partial_and_the_skeleton_is_not_approved():
    report = run("clean-openapi.json", manifest=None)
    safety(report)
    assert result_map(report)["C2"] == "partial"
    assert report["score"]["band"] == "gaps"
    assert report["manifest_skeleton"]["generated"] is True
    assert report["manifest_skeleton"]["approved"] is False
    assert report["manifest_skeleton"]["autonomy_level"] == "A0"
    assert report["manifest_skeleton"]["may_be_relied_on"] is False


def test_requested_a3_does_not_draft_a_manifest():
    report = run("clean-openapi.json", manifest=None, extra={"requested_autonomy": "A3"})
    safety(report)
    assert report["a3_recommended"] is False
    assert report["manifest_skeleton"]["generated"] is False
    assert report["manifest_skeleton"]["autonomy_level"] is None
    assert any("A3" in error for error in report["manifest_skeleton"]["errors"])


def test_rate_limit_proposal_uses_placeholders_and_is_not_published():
    report = run("no-rate-limit.json")
    safety(report)
    xml = report["proposed_diff"]["policy_xml"]
    assert "<rate-limit " in xml
    assert "SET_BY_API_OWNER" in xml
    assert 'calls="20"' not in xml
    assert "renewal-period" in xml
    assert report["policy_published"] is False


def test_secret_value_is_not_copied_into_the_report():
    report = run("secret-in-spec.json")
    safety(report)
    dumped = str(report)
    assert "sk-test-placeholder-value" not in dumped
    assert result_map(report)["C5"] == "fail"


def test_repository_tool_schemas_are_read_and_not_treated_as_http():
    from src.review import review

    for folder in (
        "25-instruction-quality-reviewer",
        "08-uk-pii-redaction-gateway",
        "12-document-intake",
    ):
        report = review(
            {
                "bundle_id": folder,
                "title": folder,
                "reviewed_on": "2026-11-02",
                "contract_kind": "repo_tools",
                "contract_repo_path": f"experiments/{folder}/schema/tools.json",
                "manifest_repo_path": f"experiments/{folder}/agent-manifest.yaml",
            },
            "2026-11-02",
        )
        safety(report)
        results = result_map(report)
        assert results["C1"] == "pass"
        assert results["C2"] == "partial"
        assert results["C3"] == "pass"
        assert results["C5"] == "partial"
        assert results["C9"] == "partial"
        assert report["score"]["band"] == "gaps"
        assert report["manifest_check"]["parsed"] is True
        assert report["http_contract"] is False
