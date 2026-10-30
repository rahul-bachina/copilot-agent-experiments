"""Checklist results on synthetic instruction files."""

from tests.support import result_map, run, safety


def test_readme_lists_every_check():
    from src.checklist import CHECKS
    from pathlib import Path

    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    for check in CHECKS:
        assert f"| {check['id']} |" in readme
        assert check["name"] in readme


def test_clean_prompt_meets_the_checklist():
    report = run("halebridge.md", extra={"use_case": {
        "case_id": "halebridge-policy",
        "title": "Halebridge policy questions",
        "organisation": {"name": "Halebridge Borough Council", "licences": {"copilot_studio": "yes"}},
        "users": {"audience": "internal_staff", "channel": "teams"},
        "data": {"description": "Published policies", "classification": "official", "volume": "bounded"},
        "actions": {"read": True, "draft": True},
        "risk": {"requested_autonomy": "A0", "named_approver": True, "approver_role": "Agent owner"},
    }})
    safety(report)
    assert report["score"]["band"] == "no_gaps"
    assert report["score"]["percent"] == 100.0
    assert report["score"]["points"] == 18
    assert report["blocking"] == []
    assert report["do_not_rely"] is False
    assert report["proposed_diff"]["diff"] == ""
    assert report["architecture_cross_check"]["called"] is True
    assert report["architecture_cross_check"]["recommended_autonomy"] == "A0"
    assert report["architecture_cross_check"]["any_option_selected"] is False
    assert report["manifest_skeleton"]["generated"] is False


def test_each_gap_is_the_check_it_claims():
    expected = {
        "missing-nongoals.md": {"C1": "partial"},
        "no-approval.md": {"C2": "fail"},
        "no-refusal.md": {"C3": "fail"},
        "prohibited-send.md": {"C4": "fail"},
        "no-injection.md": {"C5": "fail"},
        "partial-injection.md": {"C5": "partial"},
        "obey-document.md": {"C5": "fail"},
        "fill-gaps.md": {"C6": "fail"},
        "no-gdpr.md": {"C7": "fail"},
        "collect-health.md": {"C7": "fail"},
        "tool-mismatch.md": {"C8": "fail"},
        "vague-conflict.md": {"C9": "fail"},
        "unbounded.md": {"C1": "fail"},
    }
    for name, wanted in expected.items():
        report = run(name)
        safety(report)
        actual = result_map(report)
        for check_id, result in wanted.items():
            assert actual[check_id] == result, f"{name} {check_id} was {actual[check_id]}"


def test_a_finding_cites_a_line_and_proposes_a_diff_that_is_not_applied(tmp_path):
    report = run("prohibited-send.md")
    failed = next(check for check in report["checks"] if check["id"] == "C4")
    assert failed["evidence"]
    assert failed["evidence"][0]["line"] > 0
    assert failed["suggested_rewrite"]
    assert "not applied" in report["proposed_diff"]["diff"]
    assert report["diff_applied"] is False
    from pathlib import Path
    disk = Path(__file__).resolve().parents[1] / "fixtures" / "instructions" / "prohibited-send.md"
    before = disk.read_text(encoding="utf-8")
    assert "Send the reply to the resident by email." in before
    assert not (tmp_path / "untouched").exists()
    assert disk.read_text(encoding="utf-8") == before
