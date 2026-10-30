"""Classification draft. The governance team is not recorded as having approved."""

from __future__ import annotations

import json

import pytest

from classify import (
    IntakeForbidden,
    approve_use_case,
    classify,
    provision_agent,
    record_governance_decision,
    reject_use_case,
)


def proposal(**overrides):
    base = {
        "synthetic": True,
        "proposal_id": "SYN-G001-001",
        "organisation": {"name": "Northmere Borough Council", "fictional": True, "kind": "local_authority"},
        "problem": "Officers want a draft hazard category for damp and mould.",
        "users": {"who": "Housing officers", "audience": "internal_staff", "channel": "teams"},
        "data": {
            "involved": "Synthetic repair text.",
            "personal_data": "yes",
            "special_category": "no",
            "criminal_offence_data": "no",
            "classification": "official",
            "volume": "bounded",
        },
        "decisions_affected": {
            "description": "A draft category. An officer decides.",
            "significant_effect": "none",
            "regulated_decision": False,
            "significant_automated_decision": False,
        },
        "autonomy_wanted": "A1",
        "named_human_approver": True,
        "systems_touched": ["dataverse"],
        "public_interaction": "no",
        "significant_influence_on_a_decision_with_public_effect": "no",
        "pattern_hint": "housing_hazard",
    }
    base.update(overrides)
    return base


def _all_no():
    keys = (
        "article_35_3_a",
        "article_35_3_b",
        "article_35_3_c",
        "innovative_technology",
        "denial_of_service",
        "large_scale_profiling",
        "biometric_data",
        "genetic_data",
        "data_matching",
        "invisible_processing",
        "tracking",
        "targeting_children_or_vulnerable",
        "risk_of_physical_harm",
        "wp248_evaluation_or_scoring",
        "wp248_automated_decision_legal_or_similar",
        "wp248_systematic_monitoring",
        "wp248_sensitive_or_highly_personal",
        "wp248_large_scale",
        "wp248_matching_datasets",
        "wp248_vulnerable_data_subjects",
        "wp248_innovative_use",
        "wp248_prevents_rights_or_service",
        "genetic_data_direct_care_by_individual_professional",
    )
    return {key: "no" for key in keys}


def test_sample_shape_is_a_draft_the_governance_team_has_not_approved():
    draft = classify(proposal(), as_of="2026-10-30")
    assert draft["label"] == "DRAFT FOR THE GOVERNANCE TEAM"
    assert draft["catalogue_id"] == "G001"
    assert draft["autonomy"] == "A1"
    assert draft["approved"] is False
    assert draft["use_case_approved"] is False
    assert draft["use_case_rejected"] is False
    assert draft["provisioned"] is False
    assert draft["governance_decision"] is None
    assert draft["actions_taken"] == []
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["classification"]["suggested_autonomy"] == "A0"
    assert draft["classification"]["autonomy_wanted"] == "A1"
    assert draft["classification"]["a3_recommended"] is False
    assert draft["classification"]["a3_out_of_scope"] is False
    assert draft["classification"]["risk_tier"] == "medium"
    assert draft["classification"]["dpia_required"] is None
    assert draft["classification"]["atrs_scope_decided_by_this_tool"] is False
    assert draft["classification"]["resembles"]["catalogue_id"] == "UK01"
    assert draft["classification"]["resembles"]["experiment"] == "05-awaabs-law-hazard-triage"
    point = draft["human_approval_points"][0]
    assert point["action"] == "Approve or change the intake classification"
    assert point["approver"] == "Governance team"
    assert point["recorded_by_this_agent"] is False


def test_consequential_a2_request_is_suggested_and_not_approved():
    decisions = {
        "description": "The agent would refuse a claim.",
        "significant_effect": "legal",
        "regulated_decision": True,
        "significant_automated_decision": False,
        "approve_or_reject": True,
    }
    draft = classify(
        proposal(
            autonomy_wanted="A2",
            decisions_affected=decisions,
            pattern_hint="consumer_duty",
            problem="A handler wants a draft. No damp and mould.",
        ),
        as_of="2026-10-30",
    )
    assert draft["classification"]["suggested_autonomy"] == "A2"
    assert draft["classification"]["risk_tier"] == "high"
    assert draft["approved"] is False
    assert draft["experiment_14"]["platform_selected"] is None
    assert all(option["selected"] is False for option in draft["experiment_14"]["options"])


def test_a3_is_out_of_scope_and_never_suggested():
    draft = classify(
        proposal(
            autonomy_wanted="A3",
            decisions_affected={
                "description": "The agent would refuse the application.",
                "significant_effect": "legal",
                "regulated_decision": True,
                "significant_automated_decision": True,
                "approve_or_reject": True,
            },
        ),
        as_of="2026-10-30",
    )
    assert draft["classification"]["suggested_autonomy"] in {"A0", "A1", "A2"}
    assert draft["classification"]["suggested_autonomy"] != "A3"
    assert draft["classification"]["a3_requested"] is True
    assert draft["classification"]["a3_out_of_scope"] is True
    assert draft["classification"]["a3_recommended"] is False
    assert draft["experiment_14"]["a3_recommended"] is False
    assert "R13" in draft["experiment_14"]["rules_fired"]
    assert draft["use_case_approved"] is False
    assert draft["provisioned"] is False
    assert any(point["action"].startswith("Decide what to do with a request") for point in draft["human_approval_points"])


def test_special_category_does_not_invent_a_dpia_trigger():
    draft = classify(
        proposal(data={
            "involved": "Synthetic.",
            "personal_data": "yes",
            "special_category": "yes",
            "criminal_offence_data": "no",
            "classification": "official",
        }),
        as_of="2026-10-30",
    )
    assert draft["classification"]["risk_tier"] == "high"
    assert draft["classification"]["dpia_likely_needed"] is None
    assert draft["classification"]["dpia_required"] is None
    assert draft["experiment_19"]["screen_result"] == "insufficient_facts"
    assert draft["experiment_19"]["dpia_required_decided_by_this_tool"] is False


def test_recorded_article_35_answers_are_passed_through():
    answers = _all_no()
    answers["article_35_3_a"] = "yes"
    draft = classify(
        proposal(article_35_answers=answers, article_35_1_view="no"),
        as_of="2026-10-30",
    )
    assert draft["experiment_19"]["called"] is True
    assert draft["experiment_19"]["screen_result"] == "article_35_3_recorded"
    assert draft["classification"]["dpia_likely_needed"] is True
    assert draft["classification"]["dpia_required"] is None


def test_all_recorded_no_answers_are_not_a_determination():
    draft = classify(
        proposal(article_35_answers=_all_no(), article_35_1_view="no"),
        as_of="2026-10-30",
    )
    assert draft["classification"]["dpia_likely_needed"] is False
    assert draft["classification"]["dpia_required"] is None
    assert "not a decision" in draft["experiment_19"]["note"]


def test_private_firm_is_not_given_an_atrs_recommendation():
    draft = classify(
        proposal(organisation={"name": "Northmere Lending", "fictional": True, "kind": "private"}),
        as_of="2026-10-30",
    )
    assert draft["classification"]["atrs_likely_needed"] is False
    assert draft["classification"]["atrs_basis"] == "not_indicated_outside_public_sector"
    assert draft["experiment_03"]["called"] is True
    assert draft["experiment_03"]["applicability_code"] == "sector_not_public"
    assert draft["experiment_03"]["manifest_generator_called"] is False
    assert draft["experiment_03"]["atrs_approved"] is False
    assert draft["atrs"]["may_be_emailed"] is False


def test_department_with_public_interaction_matches_the_recorded_tests_only():
    draft = classify(
        proposal(
            organisation={"name": "Department of Example", "fictional": True, "kind": "government_department"},
            public_interaction="yes",
        ),
        as_of="2026-10-30",
    )
    assert draft["classification"]["atrs_likely_needed"] is True
    assert draft["classification"]["atrs_basis"] == "recorded_facts_match_the_guidance_tests"
    assert draft["atrs"]["scope_decided_by_this_tool"] is False
    assert draft["experiment_03"]["applicability_code"] == "public_sector_spoc_must_decide"
    assert draft["experiment_03"]["mandatory_scope_decided_by_experiment_03"] is False


def test_two_keyword_hits_are_not_ranked():
    draft = classify(
        proposal(
            pattern_hint=None,
            problem="A travel rule exception and a damp and mould report arrived in the same note.",
        ),
        as_of="2026-10-30",
    )
    assert draft["classification"]["resembles"] is None
    ids = {row["catalogue_id"] for row in draft["classification"]["resemble_candidates"]}
    assert "UK01" in ids
    assert "UK05" in ids


def test_live_text_is_not_copied_when_the_proposal_is_not_synthetic():
    token = "LIVE-CASE-TOKEN-77"
    draft = classify(
        {"synthetic": False, "problem": token, "proposal_id": token},
        as_of="2026-10-30",
    )
    assert draft["refused"] is True
    assert draft["classification"] is None
    assert token not in json.dumps(draft)
    assert draft["approved"] is False
    assert draft["provisioned"] is False


def test_prohibited_functions_raise():
    with pytest.raises(IntakeForbidden):
        approve_use_case()
    with pytest.raises(IntakeForbidden):
        reject_use_case()
    with pytest.raises(IntakeForbidden):
        provision_agent()
    with pytest.raises(IntakeForbidden):
        record_governance_decision({"approved": True})


def test_same_inputs_produce_the_same_json():
    first = classify(proposal(), as_of="2026-10-30")
    second = classify(proposal(), as_of="2026-10-30")
    assert first == second
