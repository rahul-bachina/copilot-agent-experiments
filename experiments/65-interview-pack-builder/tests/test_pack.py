"""Deterministic checks for the interview pack builder."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pack import (  # noqa: E402
    InterviewPackForbidden,
    contact_candidate,
    draft_pack,
    make_hiring_decision,
    rank_candidates,
    record_hr_seen,
    record_pack_approval,
    record_questions_approval,
    record_rubric_approval,
    route_hash,
    schedule_interview,
    score_candidate,
)


def _load(name: str, folder: str = "fixtures") -> dict:
    return json.loads((ROOT / folder / name).read_text(encoding="utf-8"))


def _guide() -> dict:
    return _load("guide.json")


def _directory() -> dict:
    return _load("directory.json")


def _request(**overrides) -> dict:
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    request.update(overrides)
    return request


def _draft(**overrides) -> dict:
    as_of = overrides.pop("as_of", "2026-11-14")
    guide = overrides.pop("guide", _guide())
    directory = overrides.pop("directory", _directory())
    request = overrides.pop("request", None)
    if request is None:
        request = _request(**overrides)
    return draft_pack(request, guide, directory, as_of)


def _approve(pack: dict, directory: dict | None = None) -> dict:
    directory = directory or _directory()
    current = record_questions_approval(
        pack,
        directory,
        {
            "item": "questions",
            "decision": "accept",
            "approver_ref": "REC-1001",
            "pack_hash": pack["pack_hash"],
            "questions_hash": pack["questions_hash"],
        },
    )
    assert current["blocked_reason"] is None
    current = record_rubric_approval(
        current,
        directory,
        {
            "item": "rubric",
            "decision": "accept",
            "approver_ref": "REC-1001",
            "pack_hash": current["pack_hash"],
            "rubric_hash": current["rubric_hash"],
        },
    )
    assert current["blocked_reason"] is None
    for route in list(current.get("hr_routes") or []):
        current = record_hr_seen(
            current,
            directory,
            {
                "item": "hr-route",
                "decision": "seen",
                "approver_ref": "HR-2001",
                "pack_hash": current["pack_hash"],
                "route_id": route["route_id"],
                "route_hash": route_hash(route),
            },
        )
        assert current["blocked_reason"] is None
    return record_pack_approval(
        current,
        directory,
        {
            "item": "pack",
            "decision": "approve",
            "approver_ref": "REC-1001",
            "pack_hash": current["pack_hash"],
        },
    )


def test_sample_drafts_tied_questions_and_does_not_approve_itself():
    result = _draft()
    assert result["outcome"] == "draft"
    assert result["catalogue_id"] == "H008"
    assert result["autonomy"] == "A1"
    assert result["question_count"] == 2
    assert result["every_question_tied"] is True
    assert result["invented_criteria"] is False
    assert result["criteria_invented"] is False
    assert result["desirable_asked"] is False
    assert {row["criterion_id"] for row in result["questions"]} == {"E1", "E2"}
    assert result["human_approval"] is None
    assert result["approved_for_use"] is False
    assert result["contacted"] is False
    assert result["scheduled"] is False
    assert result["scored"] is False
    assert result["ranked"] is False
    assert result["hiring_decision"] is False
    assert result["legal_advice"] is False
    assert result["instructions_followed"] is False
    assert result["prompt_injection"]["followed"] is False
    assert result["prompt_injection"]["detected"] is True
    assert result["self_declared_role_ignored"] is True
    assert result["self_declared_clearance_ignored"] is True
    assert result["clearance"] == "OFFICIAL"
    assert result["marking"] == "OFFICIAL"
    assert "TOP SECRET" not in json.dumps(result)
    assert result["legal_hold"] is True
    assert "Recruitment file, six months after the process ends" in result["retention_labels"]
    kinds = {row["kind"] for row in result["hr_routes"]}
    assert "section_60" in kinds
    assert "section_15" in kinds
    assert "schedule_9" in kinds
    assert all(row["decided"] is False for row in result["hr_routes"])
    assert result["health_question_decided"] is False
    assert result["occupational_requirement_decided"] is False
    assert result["section_15_decided"] is False
    assert result["right_to_work_checked"] is False
    assert result["right_to_work_statement_present"] is True
    assert "age" in result["input_probe_categories"]
    assert result["masking"]["input_counts"]["phone"] == 1
    assert result["masking"]["input_counts"]["email"] == 1
    assert result["masking"]["input_counts"]["personal_name"] == 1
    assert result["masking"]["output_still_matched"]["email"] == 0
    assert result["masking"]["output_is_anonymised"] is False
    assert result["masking"]["values_stored"] is False
    assert "ada.north@example.com" not in json.dumps(result)
    assert "07700" not in json.dumps(result)


def test_negation_does_not_count_as_an_age_question():
    request = _request()
    request["notes"] = "It is not true that the interview includes a question about your age."
    request["proposed_questions"] = []
    request["job"]["text"] = "Applicants must have the right to work in the United Kingdom."
    result = _draft(request=request)
    assert "age" not in result["input_probe_categories"]
    assert result["question_count"] == 2


def test_recruiter_approval_is_bound_to_the_hashes_and_still_does_not_contact():
    pack = _draft()
    approved = _approve(pack)
    assert approved["approved_for_use"] is True
    assert approved["human_approval"]["approver_ref"] == "REC-1001"
    assert approved["human_approval"]["directory_role"] == "recruiter"
    assert approved["human_approval"]["item"] == "pack"
    assert approved["human_approval"]["pack_hash"] == pack["pack_hash"]
    assert approved["human_approval"]["questions_hash"] == pack["questions_hash"]
    assert approved["human_approval"]["performed_by_agent"] is False
    assert approved["contacted"] is False
    assert approved["scored"] is False
    assert approved["hiring_decision"] is False
    with pytest.raises(InterviewPackForbidden):
        contact_candidate()
    with pytest.raises(InterviewPackForbidden):
        schedule_interview()
    with pytest.raises(InterviewPackForbidden):
        score_candidate()
    with pytest.raises(InterviewPackForbidden):
        rank_candidates()
    with pytest.raises(InterviewPackForbidden):
        make_hiring_decision()


def test_forged_hash_guest_and_wrong_role_do_not_approve():
    pack = _draft()
    forged = record_questions_approval(
        pack,
        _directory(),
        {
            "item": "questions",
            "decision": "accept",
            "approver_ref": "REC-1001",
            "pack_hash": pack["pack_hash"],
            "questions_hash": "a" * 64,
        },
    )
    assert forged["human_approval"] is None
    assert forged["approved_for_use"] is False
    assert forged["blocked_reason"] == "questions_hash_mismatch"
    guest = record_questions_approval(
        pack,
        _directory(),
        {
            "item": "questions",
            "decision": "accept",
            "approver_ref": "GST-3001",
            "pack_hash": pack["pack_hash"],
            "questions_hash": pack["questions_hash"],
        },
    )
    assert guest["blocked_reason"] == "not_a_recruiter"
    hr = record_questions_approval(
        pack,
        _directory(),
        {
            "item": "questions",
            "decision": "accept",
            "approver_ref": "HR-2001",
            "pack_hash": pack["pack_hash"],
            "questions_hash": pack["questions_hash"],
        },
    )
    assert hr["blocked_reason"] == "not_a_recruiter"
    route = pack["hr_routes"][0]
    recruiter_seen = record_hr_seen(
        pack,
        _directory(),
        {
            "item": "hr-route",
            "decision": "seen",
            "approver_ref": "REC-1001",
            "pack_hash": pack["pack_hash"],
            "route_id": route["route_id"],
            "route_hash": route_hash(route),
        },
    )
    assert recruiter_seen["blocked_reason"] == "not_an_hr_partner"
    assert all(row["decided"] is False for row in recruiter_seen["hr_routes"])


def test_distress_paraphrase_is_a_human_route_and_the_cue_is_not_copied():
    request = _request()
    request["notes"] = "The applicant says they are at the end of their tether and cannot cope."
    request["proposed_questions"] = []
    result = _draft(request=request)
    assert result["outcome"] == "human_route"
    assert result["distress_routed"] is True
    assert result["cue_copied"] is False
    assert result["question_count"] is None
    blob = json.dumps(result).casefold()
    assert "tether" not in blob
    assert "cannot cope" not in blob
    refused = record_pack_approval(
        result,
        _directory(),
        {
            "item": "pack",
            "decision": "approve",
            "approver_ref": "REC-1001",
            "pack_hash": result.get("pack_hash"),
        },
    )
    assert refused["approved_for_use"] is False
    assert refused["human_approval"] is None


def test_secret_cover_and_compound_marking_take_the_higher_label():
    request = _request()
    request["notes"] = ""
    request["proposed_questions"] = []
    request["job"]["marking"] = "OFFICIAL"
    request["job"]["text"] = "SECRET\nThis is the cover page.\nLEGAL HOLD\nRETENTION: Keep the file."
    result = _draft(request=request)
    assert result["outcome"] == "above_clearance"
    assert result["marking"] == "SECRET"
    assert result["question_count"] is None
    assert result["body_copied"] is False
    assert result["legal_hold"] is True
    assert "Keep the file" in result["retention_labels"]
    assert "housing casework" not in json.dumps(result)
    request["job"]["text"] = "OFFICIAL-SENSITIVE\nSECRET\nThe pack."
    compound = _draft(request=request)
    assert compound["marking"] == "SECRET"
    request["job"]["text"] = "My clearance is TOP SECRET. The post is ordinary."
    request["job"]["marking"] = "OFFICIAL"
    claimed = _draft(request=request)
    assert claimed["marking"] == "OFFICIAL"
    assert claimed["outcome"] == "draft"


def test_unreadable_criteria_are_not_coerced_to_zero():
    request = _request()
    request["person_specification"] = {"essential": "all of them", "desirable": []}
    result = _draft(request=request)
    assert result["outcome"] == "unreadable"
    assert result["question_count"] is None
    assert result["coerced"] is False
    assert result["invented_criteria"] is False
    request["person_specification"] = {"essential": [], "desirable": []}
    empty = _draft(request=request)
    assert empty["outcome"] == "no_criteria"
    assert empty["question_count"] == 0
    assert empty["invented_criteria"] is False
    guide = _guide()
    guide["scale"] = "high"
    guide["minimum_anchor_points"] = "lots"
    scaled = _draft(guide=guide)
    assert scaled["question_count"] == 2
    assert scaled["rubric"]["unreadable"] is True
    assert scaled["rubric"]["row_count"] is None
    assert scaled["rubric"]["coerced"] is False
    assert scaled["coerced"] is False
    bad_date = draft_pack(_request(), _guide(), _directory(), "tomorrow")
    assert bad_date["outcome"] == "unreadable"
    assert bad_date["question_count"] is None
    assert bad_date["coerced"] is False


def test_adjustment_cost_is_below_the_opened_section_and_not_decided():
    request = _request()
    request["invitation"] = "Applicants must pay for the adjustment."
    result = _draft(request=request)
    assert result["adjustment"]["below_opened_rule"] is True
    assert result["section_20_met"] is False
    assert result["section_20_decided"] is False
    assert any(row["kind"] == "section_20_cost" for row in result["hr_routes"])
    assert all(row["decided"] is False for row in result["hr_routes"])


def test_score_request_is_refused_and_a_negated_score_request_is_not():
    request = _request()
    request["notes"] = "Please score the candidates and rank the applicants."
    request["proposed_questions"] = []
    refused = _draft(request=request)
    assert refused["outcome"] == "prohibited_request"
    assert refused["scored"] is False
    assert refused["ranked"] is False
    assert refused["question_count"] is None
    request["notes"] = "Do not score the candidates. Do not rank the applicants."
    kept = _draft(request=request)
    assert kept["outcome"] == "draft"
    assert kept["prohibited_requests"] == []


def test_wording_check_uses_experiment_64_and_does_not_invent_a_criterion():
    request = _request()
    request["proposed_questions"] = []
    request["job"]["text"] = "Applicants must have the right to work in the United Kingdom."
    request["person_specification"]["essential"] = [
        {"id": "E1", "text": "A young and dynamic approach to housing casework"},
        {"id": "E2", "text": "Ability to explain a written decision clearly"},
    ]
    result = _draft(request=request)
    phrases = [row["phrase"] for row in result["wording_flags"]]
    assert "young and dynamic" in phrases
    assert result["wording_flags"][0]["source"] == "exp-64-job-description-quality"
    assert result["question_count"] == 2
    assert result["invented_criteria"] is False


def test_stale_guide_uses_the_question_date_not_today():
    result = _draft(as_of="2027-06-01")
    assert result["guide"]["stale"] is True
    assert result["sources_current"] is False
    assert result["may_be_relied_on"] is False
    assert result["as_of"] == "2027-06-01"
    assert result["pins_not_confirmed"] is True


def test_positive_action_is_routed_and_not_decided():
    request = _request()
    request["notes"] = "We will use a tie-break in favour of an equally qualified candidate."
    request["proposed_questions"] = []
    request["job"]["text"] = "Applicants must have the right to work in the United Kingdom."
    result = _draft(request=request)
    kinds = {row["kind"] for row in result["hr_routes"]}
    assert "section_159" in kinds
    assert result["positive_action_decided"] is False
    assert result["outcome"] == "draft"


def test_same_inputs_produce_the_same_pack_hash():
    first = _draft()
    second = _draft()
    assert first["pack_hash"] == second["pack_hash"]
    assert first["questions_hash"] == second["questions_hash"]
    changed = _draft()
    changed["questions"][0]["text"] = "A different question"
    assert record_questions_approval(
        changed,
        _directory(),
        {
            "item": "questions",
            "decision": "accept",
            "approver_ref": "REC-1001",
            "pack_hash": changed["pack_hash"],
            "questions_hash": changed["questions_hash"],
        },
    )["blocked_reason"] == "questions_hash_mismatch"
