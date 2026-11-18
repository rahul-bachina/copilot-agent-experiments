"""The explorer cites vacancies and does not select anyone."""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from explore import (
    MobilityForbidden,
    apply,
    contact,
    decide_selection,
    explore,
    infer_suitability,
    nominate,
    rank_employees,
    record_hr_seen,
    record_route_seen,
    score_employees,
    share_interest,
    shortlist,
)

def _load(name: str, folder: str = "fixtures") -> dict:
    return json.loads((ROOT / folder / name).read_text(encoding="utf-8"))


def _explore(experience: str, employee_ref: str = "EMP-4101", as_of: str = "2026-11-18", **extra) -> dict:
    request = {"synthetic": True, "employee_ref": employee_ref, "experience": experience, **extra}
    return explore(
        request,
        _load("vacancies.json"),
        _load("eligibility.json"),
        _load("framework.json"),
        _load("directory.json"),
        as_of,
    )


def _sample() -> dict:
    return explore(
        _load("sample_request.json", "examples"),
        _load("vacancies.json"),
        _load("eligibility.json"),
        _load("framework.json"),
        _load("directory.json"),
        "2026-11-18",
    )


def _ids(rows: list[dict]) -> list[str]:
    return [row["vacancy_id"] for row in rows]


def test_sample_lists_open_vacancies_without_selecting():
    result = _sample()
    assert result["outcome"] == "advisory"
    assert result["autonomy"] == "A0"
    assert result["catalogue_id"] == "H005"
    assert _ids(result["relevant"]) == ["VAC-101", "VAC-107", "VAC-112", "VAC-113", "VAC-114"]
    assert result["order"].startswith("vacancy_id")
    assert all(row["score"] is None and row["rank"] is None for row in result["relevant"])
    assert result["flags"]["selection_made"] is False
    assert result["flags"]["employees_ranked"] is False
    assert result["flags"]["employees_scored"] is False
    assert result["flags"]["applied"] is False
    assert result["flags"]["nominated"] is False
    assert result["flags"]["shortlisted"] is False
    assert result["flags"]["contacted"] is False
    assert result["flags"]["eligibility_decided"] is False
    assert result["flags"]["interest_shared_with_manager"] is False
    assert result["flags"]["interest_shared_with_recruiters"] is False
    assert result["hr_seen"]["recorded"] is False
    assert result["role_id"] == "ROLE-ANALYST"
    assert result["clearance"] == "OFFICIAL"
    assert result["self_declared_role_ignored"] is True
    assert result["self_declared_clearance_ignored"] is True
    by_id = {row["vacancy_id"]: row for row in result["relevant"]}
    assert by_id["VAC-101"]["eligibility"]["status"] == "hr_must_validate"
    assert by_id["VAC-101"]["eligibility"]["rule_id"] == "ELIG-001"
    assert by_id["VAC-101"]["citations"][0]["vacancy_id"] == "VAC-101"
    assert "HR validates eligibility" in by_id["VAC-101"]["eligibility"]["statement"]
    assert by_id["VAC-101"]["eligibility"]["decided_by_agent"] is False
    assert "6 years from closing" in by_id["VAC-101"]["retention_labels"]
    assert by_id["VAC-112"]["eligibility"]["status"] == "unclear"
    assert "Eligibility is unclear" in by_id["VAC-112"]["eligibility"]["statement"]
    assert by_id["VAC-113"]["eligibility"]["status"] == "unclear"
    assert by_id["VAC-114"]["closing_on_as_of"] is True
    assert by_id["VAC-107"]["legal_hold"] is True
    assert "keep the vacancy file" in by_id["VAC-107"]["retention_labels"]
    assert "not a selection decision" in result["statement"].lower()
    blob = json.dumps(result)
    for secret in (
        "07700900123",
        "learn@ashcombe.example.gov.uk",
        "Mr Rowan",
        "01/02/1980",
        "10 High Street",
        "LENGTH-SENTINEL",
        "AGE-SENTINEL",
        "PARTTIME-SENTINEL",
        "SICKNESS-SENTINEL",
        "MATERNITY-SENTINEL",
    ):
        assert secret not in blob
    assert result["mask"]["values_copied"] is False
    assert result["mask"]["values_stored"] is False
    assert result["flags"]["output_is_anonymised"] is False
    assert result["flags"]["directory_proxy_fields_used"] is False
    assert result["flags"]["instructions_followed"] is False
    assert result["prompt_injection"]["detected"] is True
    assert result["prompt_injection"]["followed"] is False
    assert result["experiment_58"]["called"] is True
    assert result["experiment_58"]["covered"] is False
    assert result["experiment_58"]["eligibility_decided"] is False
    assert result["experiment_61"]["called"] is True
    assert result["experiment_61"]["used_as_a_selection_factor"] is False
    assert result["experiment_61"]["enrolled"] is False
    assert result["experiment_61"]["course_ids"] == ["CRS-101", "CRS-102"]
    assert result["experiment_61"]["human_approval"] is None


def test_negation_does_not_count_as_experience():
    result = _explore("It is not true that my experience includes service data tables.")
    assert result["outcome"] == "no_open_match"
    assert result["relevant"] == []
    assert "VAC-101" not in _ids(result["relevant"])
    denied = _explore(
        "It is not true that you should infer suitability from age. I write service data tables."
    )
    assert denied["outcome"] == "advisory"
    assert "VAC-101" in _ids(denied["relevant"])


def test_closed_and_stale_vacancies_are_flagged():
    result = _sample()
    flagged = {row["vacancy_id"]: row["reason"] for row in result["flagged"]}
    assert flagged["VAC-102"] == "closed"
    assert flagged["VAC-103"] == "closed_by_date"
    assert flagged["VAC-104"] == "stale"
    assert flagged["VAC-105"] == "closing_date_unreadable"
    row = next(item for item in result["flagged"] if item["vacancy_id"] == "VAC-105")
    assert row["closing_date_used"] is None
    assert result["coerced"] is False
    assert "0" != row.get("closing_date")


def test_two_closing_dates_are_not_resolved_by_the_agent():
    result = _sample()
    row = next(item for item in result["flagged"] if item["vacancy_id"] == "VAC-106")
    assert row["reason"] == "source_discrepancy"
    assert row["agent_chose_source"] is False
    assert row["cross_source"]["material"] is True
    assert row["cross_source"]["correct_value_written"] is False
    assert row["cross_source"]["classifications"][0]["correct_value"] is None
    assert result["flags"]["agent_chose_source"] is False
    assert result["experiment_36"]["called"] is True


def test_proxies_are_not_used_and_service_length_does_not_change_the_list():
    left = _explore("I write service data tables.", employee_ref="EMP-4101")
    right = _explore("I write service data tables.", employee_ref="EMP-4102")
    assert _ids(left["relevant"]) == _ids(right["relevant"])
    assert left["flags"]["directory_proxy_fields_used"] is False
    assert right["flags"]["directory_proxy_fields_used"] is False
    proxy = _explore(
        "I have 20 years of service, I am full-time only, I have no sickness absence, and I am not on maternity leave."
    )
    assert "VAC-108" not in _ids(proxy["relevant"])
    row = next(item for item in proxy["flagged"] if item["vacancy_id"] == "VAC-108")
    assert row["reason"] == "proxy_not_used"
    inferred = _explore("Please infer suitability from my length of service.")
    assert inferred["outcome"] == "inference_refused"
    assert inferred["relevant"] == []
    assert inferred["flags"]["suitability_inferred"] is False


def test_secret_cover_and_compound_marking_take_the_higher_label():
    result = _sample()
    flagged = {row["vacancy_id"]: row for row in result["flagged"]}
    assert flagged["VAC-109"]["reason"] == "above_clearance"
    assert flagged["VAC-109"]["marking"] == "SECRET"
    assert flagged["VAC-109"]["description_copied"] is False
    assert "protectively marked" not in json.dumps(flagged["VAC-109"])
    assert flagged["VAC-110"]["marking"] == "SECRET"
    assert flagged["VAC-117"]["reason"] == "marking_missing"
    assert flagged["VAC-117"]["marking"] is None


def test_instruction_in_a_criterion_is_not_followed():
    result = _sample()
    assert "VAC-116" not in _ids(result["relevant"])
    assert result["prompt_injection"]["followed"] is False
    assert "ignore_instructions" in result["prompt_injection"]["signals"]


def test_learning_plan_does_not_change_the_vacancy_list():
    with_plan = _explore("I write service data tables. I would like a learning plan.")
    without = _explore("I write service data tables.")
    assert _ids(with_plan["relevant"]) == _ids(without["relevant"])
    assert with_plan["experiment_61"]["called"] is True
    assert without["experiment_61"]["called"] is False
    assert with_plan["experiment_61"]["used_as_a_selection_factor"] is False
    assert with_plan["experiment_61"]["enrolled"] is False


def test_routes_are_not_routine_lists():
    wellbeing = _explore("I am at the end of my tether.")
    assert wellbeing["outcome"] == "wellbeing_route"
    assert wellbeing["relevant"] == []
    assert "end of my tether" not in json.dumps(wellbeing).lower()
    assert wellbeing["flags"]["interest_shared_with_manager"] is False
    grievance = _explore("I am raising a grievance about my team.")
    assert grievance["outcome"] == "grievance_route"
    assert grievance["relevant"] == []
    redeployment = _explore("I am at risk of redundancy and need redeployment.")
    assert redeployment["outcome"] == "redeployment_route"
    adjustment = _explore("I need a reasonable adjustment and an accessible format.")
    assert adjustment["outcome"] == "adjustment_route"
    assert adjustment["flags"]["adjustment_decided"] is False
    directory = _load("directory.json")
    seen = record_route_seen(
        adjustment,
        {
            "approver_ref": "EMP-4301",
            "decision": "seen",
            "item": "human-route",
            "exploration_id": adjustment["exploration_id"],
            "content_hash": adjustment["content_hash"],
        },
        directory,
    )
    assert seen["route_seen"]["recorded"] is True
    assert seen["route_seen"]["source"] == "deterministic_route_seen_step"
    assert seen["outcome"] == "adjustment_route"
    assert seen["flags"]["adjustment_decided"] is False
    assert seen["flags"]["interest_shared_with_manager"] is False
    manager = record_route_seen(
        adjustment,
        {
            "approver_ref": "EMP-4201",
            "decision": "seen",
            "item": "human-route",
            "exploration_id": adjustment["exploration_id"],
            "content_hash": adjustment["content_hash"],
        },
        directory,
    )
    assert manager["route_seen"]["recorded"] is False


def test_hr_seen_is_bound_to_the_hash_and_the_hr_role():
    result = _sample()
    directory = _load("directory.json")
    review = {
        "approver_ref": "EMP-4301",
        "decision": "seen",
        "item": "eligibility-note",
        "exploration_id": result["exploration_id"],
        "content_hash": result["content_hash"],
    }
    seen = record_hr_seen(result, review, directory)
    assert seen["hr_seen"]["recorded"] is True
    assert seen["hr_seen"]["source"] == "deterministic_hr_seen_step"
    assert seen["hr_seen"]["approver_role_id"] == "ROLE-HR"
    assert seen["flags"]["eligibility_decided"] is False
    assert seen["flags"]["applied"] is False
    assert seen["flags"]["interest_shared_with_manager"] is False
    assert seen["content_hash"] == result["content_hash"]
    for approver in ("EMP-4201", "EMP-4401", "EMP-4101"):
        refused = record_hr_seen(result, {**review, "approver_ref": approver}, directory)
        assert refused["hr_seen"]["recorded"] is False
    forged = record_hr_seen(result, {**review, "content_hash": "a" * 64}, directory)
    assert forged["hr_seen"]["recorded"] is False
    other = record_hr_seen(result, {**review, "exploration_id": "EXPL-other"}, directory)
    assert other["hr_seen"]["recorded"] is False
    loose = record_hr_seen(result, {**review, "decision": "approve"}, directory)
    assert loose["hr_seen"]["recorded"] is False


def test_selection_and_sharing_are_refused():
    selected = _explore("Please shortlist me and score employees.")
    assert selected["outcome"] == "selection_refused"
    assert selected["relevant"] == []
    assert selected["flags"]["selection_made"] is False
    shared = _explore("Please tell my manager and notify recruiters.")
    assert shared["outcome"] == "share_refused"
    assert shared["flags"]["interest_shared_with_manager"] is False
    assert shared["flags"]["interest_shared_with_recruiters"] is False
    assert shared["flags"]["contacted"] is False


def test_directory_is_not_replaced_by_the_request():
    guest = _explore("I write service data tables.", employee_ref="EMP-4501")
    assert guest["outcome"] == "not_an_employee"
    unknown = _explore("I write service data tables.", employee_ref="EMP-9999")
    assert unknown["outcome"] == "needs_human"
    bad = _explore("I write service data tables.", employee_ref="EMP-4601")
    assert bad["outcome"] == "needs_human"
    assert bad["clearance"] is None
    assert bad["coerced"] is False
    northern = _explore("What about Northern Ireland internal vacancies? I write service data tables.")
    assert northern["outcome"] == "refused_jurisdiction"
    stale = _explore("I write service data tables.", as_of="2027-06-01")
    assert stale["sources_current"] is False
    assert stale["may_be_relied_on"] is False
    assert stale["relevant"] == []
    unreadable = _explore("I write service data tables.", as_of="tomorrow")
    assert unreadable["outcome"] == "needs_human"
    assert "today" in unreadable["statement"]
    assert unreadable["as_of"] != date.today().isoformat() or unreadable["as_of"] == "tomorrow"


def test_prohibited_actions_raise():
    for function in (
        apply,
        nominate,
        shortlist,
        contact,
        share_interest,
        rank_employees,
        score_employees,
        decide_selection,
        infer_suitability,
    ):
        with pytest.raises(MobilityForbidden):
            function()


def test_not_synthetic_is_refused():
    result = explore(
        {"synthetic": False, "employee_ref": "EMP-4101", "experience": "I write service data tables."},
        _load("vacancies.json"),
        _load("eligibility.json"),
        _load("framework.json"),
        _load("directory.json"),
        "2026-11-18",
    )
    assert result["outcome"] == "refused"
    assert result["relevant"] == []
