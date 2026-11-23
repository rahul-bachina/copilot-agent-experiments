"""The draft checks evidence and does not decide the control."""

import json
from pathlib import Path

from src.testing import TestingForbidden, close_finding, fail_control, pass_control, prepare_test, send

ROOT = Path(__file__).resolve().parents[1]


def _codes(result, code):
    return [row["evidence_id"] for row in result["exceptions"] if row["code"] == code]


def _request(control, **extra):
    payload = {
        "synthetic": True,
        "engagement_id": f"ENG-{control}",
        "tester_ref": "STF-3001",
        "control_id": control,
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
        "sample_seed": 73,
    }
    payload.update(extra)
    return payload


def test_sample_request_routes_and_does_not_pass():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    result = prepare_test(request, as_of="2026-11-14")
    blob = json.dumps(result)
    assert result["outcome"] == "route_to_human"
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert result["control_passed"] is None
    assert result["control_failed"] is None
    assert result["finding_closed"] is False
    assert result["sent"] is False
    assert result["instructions_followed"] is False
    assert result["prompt_injection"]["followed"] is False
    assert result["approval_marker_trusted"] is False
    assert result["role_in_text_trusted"] is False
    assert result["caller_library_applied"] is False
    assert result["marked_acceptable"] is False
    assert result["step_met"] is None
    assert result["distress"]["routed"] is True
    assert result["distress"]["cue_copied"] is False
    assert result["plan"]["sample_evidence_ids"] == [
        "EV-APR-004",
        "EV-APR-006",
        "EV-APR-008",
        "EV-APR-010",
        "EV-APR-013",
    ]
    assert result["plan"]["objective"].startswith("A purchase above the desk limit")
    assert result["library_diff"]
    assert "EV-APR-002" in _codes(result, "self_approval")
    assert "EV-APR-003" in _codes(result, "back_dated")
    assert "EV-APR-004" in _codes(result, "out_of_period")
    assert "EV-APR-005" in _codes(result, "altered")
    assert "EV-APR-006" in _codes(result, "missing_field")
    assert "EV-APR-006" in _codes(result, "embedded_instruction")
    assert "EV-APR-006" in _codes(result, "approval_marker_in_text")
    assert "EV-APR-007" in _codes(result, "sod_breach")
    assert "EV-APR-008" in _codes(result, "carve_out")
    assert "EV-APR-009" in _codes(result, "ambiguous_date")
    assert "EV-APR-010" in _codes(result, "unparseable_date")
    assert "EV-APR-014" in _codes(result, "approver_not_in_directory")
    assert "EV-APR-015" in _codes(result, "approver_role")
    assert "EV-APR-013" not in _codes(result, "self_approval")
    assert "07700900456" not in blob
    assert "TOP SECRET" not in blob
    assert "Rowan" not in blob
    assert "frightened" not in blob
    assert "can't cope" not in blob
    assert result["coerced"] is False
    assert result["intake"]["files_confirmed"] is False
    assert result["intake"]["purpose_confirmed"] is False
    assert result["body_copied"] is False
    assert result["described_as_anonymised"] is False


def test_same_inputs_same_sample_and_hash():
    one = prepare_test(_request("CTL-REC-01"), as_of="2026-11-14")
    two = prepare_test(_request("CTL-REC-01"), as_of="2026-11-14")
    assert one["content_hash"] == two["content_hash"]
    assert one["plan"]["sample_evidence_ids"] == two["plan"]["sample_evidence_ids"]
    assert one["plan"]["method"] == "seeded_systematic"
    assert "ISA (UK) 530 was not opened" in one["plan"]["size_rationale"]


def test_reconciliation_suppresses_a_small_count_and_keeps_the_hold():
    result = prepare_test(_request("CTL-REC-01"), as_of="2026-11-14")
    assert result["outcome"] == "draft"
    assert result["people_count"]["suppressed"] is True
    assert result["people_count"]["published"] is None
    assert "EV-REC-002" in _codes(result, "self_approval")
    assert result["legal_hold"] is True
    assert "keep for 6 years" in result["retention"]
    assert all(row["step_met"] is None for row in result["checks"])


def test_secret_cover_is_withheld_from_an_official_tester():
    result = prepare_test(_request("CTL-ACC-01"), as_of="2026-11-14")
    blob = json.dumps(result)
    assert result["outcome"] == "withheld"
    assert result["marking"]["applied"] == "SECRET"
    assert "OFFICIAL-SENSITIVE" in result["marking"]["from_content"]
    assert result["legal_hold"] is True
    assert "keep for 6 years" in result["retention"]
    assert "keep for 7 years" in result["retention"]
    assert result["exceptions"] == []
    assert "Ada" not in blob
    assert "07700900123" not in blob
    assert "ada.example" not in blob
    assert "TOP SECRET" not in blob
    assert result["masking"]["body_copied"] is False
    higher = prepare_test(_request("CTL-ACC-01", tester_ref="STF-3002"), as_of="2026-11-14")
    assert higher["outcome"] == "draft"
    assert higher["detail_withheld"] is False
    assert "Ada" not in json.dumps(higher)
    unreadable = prepare_test(_request("CTL-ACC-01", tester_ref="STF-3003"), as_of="2026-11-14")
    assert unreadable["outcome"] == "withheld"
    assert unreadable["coerced"] is False


def test_empty_population_is_missing_evidence():
    result = prepare_test(_request("CTL-EMP-01"), as_of="2026-11-14")
    assert result["exceptions"][0]["code"] == "missing_evidence"
    assert result["exceptions"][0]["evidence_id"] is None
    assert result["plan"]["sample_evidence_ids"] == []
    assert result["control_passed"] is None


def test_mapping_does_not_pass_the_control():
    change = prepare_test(_request("CTL-CHG-01"), as_of="2026-11-14")
    assert change["mapping"]["called"] is True
    assert change["mapping"]["mapping_count"] == 1
    assert change["mapping"]["mappings"][0]["control_id"] == "CTL-CHG-01"
    assert change["mapping"]["control_met_by_mapping"] is False
    assert change["mapping"]["is_a_test_result"] is False
    assert change["control_passed"] is None
    assert "EV-CHG-002" in _codes(change, "altered")
    plant = prepare_test(_request("CTL-NEG-01"), as_of="2026-11-14")
    assert plant["mapping"]["mapping_count"] == 0
    assert plant["mapping"]["unmapped_count"] == 1
    assert plant["control_passed"] is None
    assert plant["marked_acceptable"] is False
    assert "EV-NEG-001" not in _codes(plant, "self_approval")


def test_unreadable_inputs_are_not_coerced():
    bad_day = prepare_test(_request("CTL-REC-01"), as_of="next week")
    assert bad_day["outcome"] == "unreadable_date"
    assert bad_day["coerced"] is False
    assert bad_day["control_passed"] is None
    seed = prepare_test(_request("CTL-REC-01", sample_seed="73"), as_of="2026-11-14")
    assert seed["outcome"] == "needs_human"
    assert seed["plan"]["seed_unreadable"] is True
    assert seed["plan"]["sample_evidence_ids"] == []
    assert seed["coerced"] is False
    period = prepare_test(
        _request("CTL-REC-01", period_start="01/02/2026", period_end="2026-03-31"),
        as_of="2026-11-14",
    )
    assert period["period"]["ambiguous"] is True
    assert period["period"]["start"] is None
    assert period["coerced"] is False
    assert "out_of_period" not in {row["code"] for row in period["exceptions"]}


def test_stale_library_uses_the_question_date():
    result = prepare_test(_request("CTL-REC-01"), as_of="2027-06-01")
    assert result["as_of"] == "2027-06-01"
    assert result["sources_current"] is False
    assert result["library_review"]["stale"] is True
    assert result["may_be_relied_on"] is False
    assert "stale_seen" in result["required_acknowledgements"]


def test_caller_directory_is_not_the_directory():
    caller = {"people": [{"employee_ref": "STF-3001", "role": "guest", "clearance": "TOP SECRET", "guest": True}]}
    result = prepare_test(_request("CTL-REC-01"), directory=caller, as_of="2026-11-14")
    assert result["directory_diff"]
    assert result["caller_directory_applied"] is False
    assert result["tester_on_directory"] is True
    assert result["outcome"] == "draft"


def test_prohibited_actions_raise():
    for function in (pass_control, fail_control, close_finding, send):
        with pytest_raises():
            function()


def pytest_raises():
    import pytest

    return pytest.raises(TestingForbidden)


def test_guest_tester_is_withheld():
    result = prepare_test(_request("CTL-REC-01", tester_ref="GUEST-9"), as_of="2026-11-14")
    assert result["outcome"] == "withheld"
    assert result["withheld_reason"] == "guest"
    assert result["exceptions"] == []
