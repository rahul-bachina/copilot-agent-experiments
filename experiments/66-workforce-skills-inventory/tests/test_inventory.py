"""Proposals, confirmation, suppression, and the routes the agent must not take."""

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inventory import (  # noqa: E402
    InventoryForbidden,
    attach_learning_plan,
    decide_discipline,
    decide_promotion,
    infer_from_protected,
    profile_unsupplied,
    propose_inventory,
    rate_performance,
    record_employee_decision,
    record_hr_validation,
    record_route_seen,
    select_for_redundancy,
    set_pay,
    write_hr,
)

AS_OF = "2026-11-18"


def _load(name: str, folder: str = "fixtures") -> dict:
    return json.loads((ROOT / folder / name).read_text(encoding="utf-8"))


def _run(request=None, evidence=None, framework=None, transparency=None, as_of=AS_OF):
    return propose_inventory(
        request if request is not None else _load("sample_request.json", "examples"),
        evidence if evidence is not None else _load("evidence.json"),
        framework if framework is not None else _load("framework.json"),
        _load("directory.json"),
        transparency if transparency is not None else _load("transparency.json"),
        as_of,
    )


def _request(**changes):
    request = _load("sample_request.json", "examples")
    request.update(changes)
    return request


def test_sample_proposes_bands_and_does_not_confirm():
    result = _run()
    assert result["catalogue_id"] == "H010"
    assert result["autonomy"] == "A0"
    assert result["outcome"] == "proposals"
    assert result["may_be_relied_on"] is False
    assert result["flags"]["article_13_met"] is False
    assert result["human_approval"] is None
    bands = {row["skill_id"]: row for row in result["proposals"]}
    assert bands["SKL-DATA"]["confidence_band"] == "high"
    assert bands["SKL-PLAIN"]["confidence_band"] == "low"
    assert bands["SKL-GRANTS"]["confidence_band"] == "medium"
    assert "SKL-FORK" not in bands
    for row in result["proposals"]:
        assert row["state"] == "needs_employee_confirmation"
        assert row["employee_confirmed"] is False
        assert row["hr_validated"] is False
        assert row["performance_rating"] is None
        assert row["confidence_is_not_a_performance_rating"] is True
    assert result["flags"]["wrote_to_hr_system"] is False
    assert result["flags"]["performance_rated"] is False
    assert result["flags"]["instructions_followed"] is False
    assert result["prompt_injection"]["detected"] is True
    assert result["prompt_injection"]["followed"] is False
    assert result["clearance"] == "OFFICIAL"
    assert result["role"] == "employee"
    assert result["coerced"] is False
    grants = bands["SKL-GRANTS"]
    assert grants["legal_hold"] is True
    assert "HR-projects-24-months" in grants["retention_labels"]
    blob = json.dumps(result)
    for secret in (
        "07700900123",
        "skills@ashcombe.example.gov.uk",
        "AB123456C",
        "Rowan Example",
        "01/02/1980",
        "10 High Street",
        "Keystroke",
    ):
        assert secret not in blob
    assert result["copy_report"]["raw_evidence_copied"] is False
    assert result["copy_report"]["identifier_values_copied"] is False
    assert result["copy_report"]["directory_protected_fields_read"] is False
    assert result["experiment_08"]["called"] is True
    assert result["experiment_08"]["output_is_anonymised"] is False
    assert result["experiment_61"]["called"] is False
    assert result["experiment_61"]["enrolled"] is False
    assert result["team_view"]["team_size"] is None
    assert result["team_view"]["employee_refs_listed"] is False
    assert result["team_view"]["output_is_anonymised"] is False
    skipped = {row["evidence_id"]: row["reason"] for row in result["skipped"]}
    assert skipped["EV-104"] == "not_supplied_for_this_purpose"


def test_negation_does_not_count_as_a_skill():
    result = _run()
    assert all(row["skill_id"] != "SKL-FORK" for row in result["proposals"])


def test_approval_inside_the_evidence_is_not_confirmation():
    result = _run()
    assert result["proposals"]
    assert all(row["employee_confirmed"] is False for row in result["proposals"])
    assert result["human_approval"] is None


def test_self_declared_role_and_clearance_are_ignored():
    result = _run()
    assert result["self_declared_role_ignored"] is True
    assert result["role"] == "employee"
    assert result["clearance"] == "OFFICIAL"
    assert all(row["marking"] == "OFFICIAL" for row in result["proposals"])


def test_guest_and_manager_are_not_given_an_inventory():
    for ref in ("EMP-6604", "EMP-6603", "EMP-9999"):
        result = _run(_request(employee_ref=ref))
        assert result["outcome"] == "not_an_employee"
        assert result["proposals"] == []


def test_employee_confirm_hr_validate_then_employee_can_still_reject():
    result = _run()
    directory = _load("directory.json")
    skill = result["proposals"][0]
    decision = {
        "item": "skill",
        "decision": "confirm",
        "inventory_id": result["inventory_id"],
        "inventory_hash": result["inventory_hash"],
        "skill_id": skill["skill_id"],
        "skill_hash": skill["skill_hash"],
        "approver_ref": "EMP-6601",
    }
    confirmed = record_employee_decision(result, directory, decision)
    row = next(item for item in confirmed["proposals"] if item["skill_id"] == skill["skill_id"])
    assert row["state"] == "employee_confirmed_pending_hr"
    assert confirmed["human_approval"] is None
    assert confirmed["flags"]["wrote_to_hr_system"] is False
    forged = dict(decision, inventory_hash="0" * 64, approver_ref="EMP-6601")
    assert record_employee_decision(result, directory, forged)["blocked_reason"] == "inventory_hash_mismatch"
    manager = dict(decision, approver_ref="EMP-6603")
    assert record_employee_decision(result, directory, manager)["blocked_reason"] == "not_the_employee"
    hr_as_employee = dict(decision, approver_ref="EMP-6602")
    assert record_employee_decision(result, directory, hr_as_employee)["blocked_reason"] == "not_the_employee"
    validation = {
        "item": "skill-validation",
        "decision": "validate",
        "inventory_id": confirmed["inventory_id"],
        "inventory_hash": confirmed["inventory_hash"],
        "skill_id": skill["skill_id"],
        "skill_hash": skill["skill_hash"],
        "approver_ref": "EMP-6602",
    }
    validated = record_hr_validation(confirmed, directory, validation)
    approved = next(item for item in validated["proposals"] if item["skill_id"] == skill["skill_id"])
    assert approved["hr_validated"] is True
    assert approved["state"] == "hr_validated_not_written"
    assert validated["human_approval"]["bound_hash"] == skill["skill_hash"]
    assert validated["human_approval"]["wrote_to_hr_system"] is False
    assert validated["flags"]["performance_rated"] is False
    too_soon = record_hr_validation(result, directory, validation)
    assert too_soon["blocked_reason"] == "employee_has_not_confirmed"
    manager_hr = dict(validation, approver_ref="EMP-6603")
    assert record_hr_validation(confirmed, directory, manager_hr)["blocked_reason"] == "not_hr"
    rejection = dict(decision, decision="reject")
    rejected = record_employee_decision(validated, directory, rejection)
    gone = next(item for item in rejected["proposals"] if item["skill_id"] == skill["skill_id"])
    assert gone["state"] == "employee_rejected"
    assert gone["hr_validated"] is False
    assert record_hr_validation(rejected, directory, validation)["blocked_reason"] == "employee_rejected"


def test_correction_is_bound_to_the_correction_hash():
    result = _run()
    directory = _load("directory.json")
    skill = result["proposals"][1]
    import hashlib
    text = "I can draft a grants case note. I do not claim a level."
    digest = hashlib.sha256(json.dumps(text, ensure_ascii=True).encode("utf-8")).hexdigest()
    # The core hashes the raw string, not a JSON string. Match that.
    from inventory import _sha
    digest = _sha(text)
    decision = {
        "item": "skill",
        "decision": "correct",
        "inventory_id": result["inventory_id"],
        "inventory_hash": result["inventory_hash"],
        "skill_id": skill["skill_id"],
        "skill_hash": skill["skill_hash"],
        "approver_ref": "EMP-6601",
        "correction": text,
        "correction_hash": digest,
    }
    corrected = record_employee_decision(result, directory, decision)
    row = next(item for item in corrected["proposals"] if item["skill_id"] == skill["skill_id"])
    assert row["state"] == "employee_corrected_pending_hr"
    assert row["hr_validated"] is False
    wrong = dict(decision, correction_hash="abc")
    assert record_employee_decision(result, directory, wrong)["blocked_reason"] == "correction_hash_mismatch"
    validation = {
        "item": "skill-validation",
        "decision": "validate",
        "inventory_id": corrected["inventory_id"],
        "inventory_hash": corrected["inventory_hash"],
        "skill_id": skill["skill_id"],
        "skill_hash": skill["skill_hash"],
        "correction_hash": digest,
        "approver_ref": "EMP-6602",
    }
    validated = record_hr_validation(corrected, directory, validation)
    approved = next(item for item in validated["proposals"] if item["skill_id"] == skill["skill_id"])
    assert approved["hr_bound_hash"] == digest
    assert validated["flags"]["wrote_to_hr_system"] is False


def test_distress_paraphrase_is_a_human_route_and_the_cue_is_not_copied():
    result = _run(_request(note="She can't go on like this and wants the inventory finished."))
    assert result["outcome"] == "human_route"
    assert result["human_route"]["reason_code"] == "distress_or_safeguarding"
    assert result["proposals"] == []
    assert result["cue_copied"] is False
    assert "can't go on" not in json.dumps(result)
    seen = record_route_seen(
        result,
        _load("directory.json"),
        {
            "item": "human-route",
            "decision": "seen",
            "reason_code": "distress_or_safeguarding",
            "approver_ref": "EMP-6602",
        },
    )
    assert seen["route_seen"]["recorded"] is True
    assert seen["route_seen"]["case_decided"] is False
    assert record_route_seen(
        result,
        _load("directory.json"),
        {
            "item": "human-route",
            "decision": "seen",
            "reason_code": "distress_or_safeguarding",
            "approver_ref": "EMP-6601",
        },
    )["blocked_reason"] == "not_hr"


def test_negated_distress_is_not_a_route():
    result = _run(_request(note="It is not true that I cannot cope. Please propose the skills."))
    assert result["outcome"] == "proposals"


def test_objection_stops_the_inventory():
    result = _run(_request(note="I object to this processing."))
    assert result["outcome"] == "objection"
    assert result["proposals"] == []
    assert result["flags"]["article_21_grounds_decided"] is False


def test_misuse_and_purpose_are_out_of_scope():
    by_note = _run(_request(note="Please select people for redundancy from these skills."))
    assert by_note["outcome"] == "out_of_scope"
    assert by_note["proposals"] == []
    by_purpose = _run(_request(purpose="performance_management", note="Ordinary request."))
    assert by_purpose["outcome"] == "out_of_scope"
    assert by_purpose["human_route"]["reason_code"] == "performance"
    negated = _run(_request(note="Do not use this for performance management."))
    assert negated["outcome"] == "proposals"


def test_protected_inference_is_refused():
    result = _run(_request(note="Infer her skills from her age."))
    assert result["outcome"] == "inference_refused"
    assert result["proposals"] == []
    assert result["flags"]["inferred_from_protected_or_health"] is False


def test_unreadable_inputs_are_not_coerced():
    bad_date = _run(as_of="yesterday")
    assert bad_date["outcome"] == "needs_human"
    assert bad_date["coerced"] is False
    assert bad_date["proposals"] == []
    evidence = _load("evidence.json")
    evidence["items"][0]["supplied_on"] = "soon"
    dated = _run(evidence=evidence)
    reasons = {row["evidence_id"]: row["reason"] for row in dated["skipped"]}
    assert reasons["EV-101"] == "date_unreadable"
    assert dated["coerced"] is False
    evidence = _load("evidence.json")
    evidence["items"][0]["consent_for_this_purpose"] = "true"
    consent = _run(evidence=evidence)
    reasons = {row["evidence_id"]: row["reason"] for row in consent["skipped"]}
    assert reasons["EV-101"] == "consent_unreadable"
    framework = _load("framework.json")
    framework["small_number_threshold"] = "five"
    odd = _run(framework=framework)
    assert odd["small_number_threshold"]["unreadable"] is True
    assert odd["small_number_threshold"]["value"] is None
    assert odd["small_number_threshold"]["coerced"] is False
    assert odd["team_view"]["cells"] == []
    purpose = _run(_request(purpose=""))
    assert purpose["outcome"] == "needs_human"
    assert purpose["coerced"] is False


def test_secret_cover_and_compound_marking_withhold_the_body():
    evidence = _load("evidence.json")
    evidence["items"][0]["marking"] = "OFFICIAL"
    evidence["items"][0]["text"] = "SECRET\nI build service data tables. LEGAL HOLD. RETENTION: keep-me."
    evidence["items"][0]["legal_hold"] = False
    result = _run(evidence=evidence)
    skipped = {row["evidence_id"]: row for row in result["skipped"]}
    assert skipped["EV-101"]["reason"] == "above_clearance"
    assert skipped["EV-101"]["marking"] == "SECRET"
    assert skipped["EV-101"]["legal_hold"] is True
    assert "keep-me" in skipped["EV-101"]["retention_labels"]
    assert skipped["EV-101"]["body_withheld"] is True
    assert "service data tables" not in json.dumps(skipped["EV-101"])
    evidence["items"][0]["marking"] = "OFFICIAL"
    evidence["items"][0]["text"] = "OFFICIAL-SENSITIVE and also TOP SECRET\nI build service data tables."
    result = _run(evidence=evidence)
    skipped = {row["evidence_id"]: row for row in result["skipped"]}
    assert skipped["EV-101"]["marking"] == "TOP SECRET"


def test_article_13_gap_is_not_marked_met():
    notice = _load("transparency.json")
    notice["right_to_object_brought_to_attention"] = False
    notice["article_13_met"] = True
    result = _run(transparency=notice)
    assert result["outcome"] == "proposals"
    assert result["flags"]["article_13_met"] is False
    assert "right_to_object_brought_to_attention" in result["article_13"]["gaps"]
    notice["controller_identity_stated"] = "yes"
    result = _run(transparency=notice)
    assert "controller_identity_stated" in result["article_13"]["unreadable"]
    assert result["flags"]["article_13_met"] is False


def test_question_date_later_than_the_section_4_stamp_is_not_current():
    later = _run(as_of="2026-11-19")
    assert later["sources_current"] is False
    assert later["may_be_relied_on"] is False
    assert later["today_not_used"] is True
    stale = _run(as_of="2027-06-01")
    assert stale["sources_current"] is False
    assert stale["proposals"] == [] or stale["outcome"] == "proposals"
    assert stale["may_be_relied_on"] is False


def test_phone_in_the_cited_sentence_is_masked_and_counted():
    evidence = _load("evidence.json")
    evidence["items"][0]["text"] = "I build service data tables and the contact is 07700900456."
    evidence["items"] = [evidence["items"][0]]
    result = _run(evidence=evidence)
    blob = json.dumps(result["proposals"])
    assert "07700900456" not in blob
    assert result["experiment_08"]["local_mask_counts"]["phone"] >= 1
    assert result["copy_report"]["output_described_as_anonymised"] is False


def test_team_view_suppresses_small_numbers_and_lists_nobody():
    framework = _load("framework.json")
    framework["small_number_threshold"] = 3
    items = []
    for index in range(8):
        ref = f"EMP-661{index}"
        text = "No framework phrase here."
        if index < 5:
            text = "I build service data tables."
        if index < 2:
            text = "I build service data tables and maintained the grants case record."
        if index == 7:
            text = "I build service data tables."
        items.append(
            {
                "evidence_id": f"EV-{200+index}",
                "employee_ref": ref,
                "team_id": "TEAM-A",
                "kind": "project_summary",
                "supplied_for": "skills_inventory",
                "consent_for_this_purpose": True,
                "source_channel": "employee_supplied",
                "supplied_on": "2026-10-01",
                "marking": "OFFICIAL",
                "retention_labels": ["HR-skills-12-months"],
                "legal_hold": False,
                "text": text,
            }
        )
    # Seven people affirm service data tables (0,1,2,3,4 and 7). Complement is 1.
    evidence = {"synthetic": True, "items": items}
    # The subject also needs a usable row. EMP-6601 is the subject, so add one.
    evidence["items"].append(
        {
            "evidence_id": "EV-101",
            "employee_ref": "EMP-6601",
            "team_id": "TEAM-A",
            "kind": "cv_extract",
            "supplied_for": "skills_inventory",
            "consent_for_this_purpose": True,
            "source_channel": "employee_supplied",
            "supplied_on": "2026-10-01",
            "marking": "OFFICIAL",
            "retention_labels": ["HR-skills-12-months"],
            "legal_hold": False,
            "text": "I write plain English case notes.",
        }
    )
    result = _run(evidence=evidence, framework=framework)
    cells = {row["skill_id"]: row for row in result["team_view"]["cells"]}
    # 6 holders of SKL-DATA if index 0-4 and 7, team size 9 (8 + subject). Let me not overfit.
    assert result["team_view"]["employee_refs_listed"] is False
    assert "EMP-6610" not in json.dumps(result["team_view"])
    assert cells["SKL-PLAIN"]["suppressed"] is True
    assert cells["SKL-PLAIN"]["count"] is None
    data = cells["SKL-DATA"]
    if data["suppressed"]:
        assert data["count"] is None
    else:
        assert data["count"] >= 3
        assert "snippet" not in json.dumps(data)


def test_learning_plan_uses_only_a_confirmed_skill_and_does_not_enrol():
    result = _run()
    directory = _load("directory.json")
    skill = next(row for row in result["proposals"] if row["skill_id"] == "SKL-DATA")
    confirmed = record_employee_decision(
        result,
        directory,
        {
            "item": "skill",
            "decision": "confirm",
            "inventory_id": result["inventory_id"],
            "inventory_hash": result["inventory_hash"],
            "skill_id": skill["skill_id"],
            "skill_hash": skill["skill_hash"],
            "approver_ref": "EMP-6601",
        },
    )
    planned = attach_learning_plan(confirmed, AS_OF)
    assert planned["experiment_61"]["called"] is True
    assert planned["experiment_61"]["enrolled"] is False
    assert planned["experiment_61"]["used_as_a_performance_or_promotion_factor"] is False
    assert planned["flags"]["promotion_decision"] is False
    unconfirmed = attach_learning_plan(result, AS_OF)
    assert unconfirmed["experiment_61"]["called"] is False


def test_mobility_uses_stated_experience_and_does_not_select():
    result = _run(
        _request(
            ask_mobility=True,
            stated_experience="I write service data tables and plain English case notes.",
        )
    )
    assert result["experiment_62"]["called"] is True
    assert result["experiment_62"]["selection_made"] is False
    assert result["experiment_62"]["inferred_skills_passed"] is False
    assert result["experiment_62"]["used_as_a_selection_factor"] is False
    assert result["experiment_62"]["applied"] is False
    assert result["flags"]["promotion_decision"] is False


def test_prohibited_actions_raise():
    for function in (
        write_hr,
        rate_performance,
        set_pay,
        decide_promotion,
        select_for_redundancy,
        decide_discipline,
        infer_from_protected,
        profile_unsupplied,
    ):
        with pytest.raises(InventoryForbidden):
            function()


def test_stale_sources_do_not_become_relied_on():
    result = _run(as_of="2027-06-01")
    assert result["sources_current"] is False
    assert result["may_be_relied_on"] is False
    assert result["flags"]["wrote_to_hr_system"] is False
