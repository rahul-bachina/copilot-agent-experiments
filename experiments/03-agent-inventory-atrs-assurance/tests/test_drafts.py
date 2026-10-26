"""ATRS drafts, playbook rows, DPIA skeleton, DUAA screen, FCA-style inventory."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import load_record  # noqa: E402
from catalogue import ATRS_FIELDS, GAP_TEXT, PLAYBOOK_PRINCIPLES  # noqa: E402
from drafts import draft_atrs, draft_dpia, draft_fca, draft_playbook, screen_duaa  # noqa: E402
from pack import build_pack  # noqa: E402


def test_atrs_field_list_matches_the_v4_workbook_identifiers():
    references = [field.reference for field in ATRS_FIELDS]
    assert len(references) == 56
    assert len(set(references)) == 56
    assert references[0] == "0.1"
    assert "1.1" in references
    assert "2.4.2.1" in references
    assert "2.4.2.1." not in references
    assert references[-1] == "2.5.2"
    names = {field.reference: field.name for field in ATRS_FIELDS}
    assert names["1.1"] == "Name"
    assert names["1.2"] == "Description"
    assert names["2.1.3"] == "Senior responsible owner"
    assert names["2.3.2"] == "Human review"
    assert names["2.4.1.2"] == "System-level input"
    assert names["2.4.4.1"] == "Data sources"
    assert names["2.5.1"] == "Impact assessments"


def test_experiment_01_draft_copies_inventory_and_does_not_submit():
    record = load_record("exp-01-foi-triage")
    atrs = draft_atrs(record)
    by_ref = {field["reference"]: field for field in atrs["fields"]}
    assert by_ref["1.1"]["answer"] == record["name"]
    assert by_ref["1.1"]["answer_state"] == "draft_from_inventory"
    assert by_ref["1.1"]["approved"] is False
    assert by_ref["0.3"]["answer"] == "Pre-deployment"
    assert atrs["approved"] is False
    assert atrs["may_be_emailed"] is False
    assert atrs["submission_status"] == "not_submitted"
    assert atrs["applicability"]["code"] == "public_sector_spoc_must_decide"
    assert atrs["applicability"]["mandatory_scope_decided_by_this_tool"] is False
    assert atrs["applicability"]["may_be_emailed_to_dsit"] is False
    assert atrs["template_version"] == "4.0"


def test_experiment_02_is_not_an_atrs_submission():
    record = load_record("exp-02-consumer-duty-complaint-intake")
    atrs = draft_atrs(record)
    assert atrs["applicability"]["code"] == "not_a_public_sector_body"
    assert atrs["may_be_emailed"] is False
    assert atrs["approved"] is False


def test_unknown_phase_is_not_presented_as_a_completed_field():
    record = load_record("exp-01-foi-triage")
    record["atrs_phase"] = "Idea"
    field = {item["reference"]: item for item in draft_atrs(record)["fields"]}["0.3"]
    assert field["answer"] == GAP_TEXT
    assert field["answer_state"] == "rejected_not_in_template_list"
    assert field["source_value"] == "Idea"


def test_gap_when_the_inventory_is_silent():
    record = load_record("syn-stale-register")
    field = {item["reference"]: item for item in draft_atrs(record)["fields"]}["2.2.2"]
    assert field["answer"] == GAP_TEXT
    assert field["answer_state"] == "gap"
    assert field["grounded_in"] == []


def test_playbook_has_the_ten_published_titles_and_does_not_score_them():
    record = load_record("exp-01-foi-triage")
    playbook = draft_playbook(record)
    assert [row["number"] for row in playbook["principles"]] == list(range(1, 11))
    assert [row["title"] for row in playbook["principles"]] == [item.title for item in PLAYBOOK_PRINCIPLES]
    assert playbook["approved"] is False
    assert all(row["met"] is None for row in playbook["principles"])
    assert all(row["assessment"] == "draft_mapping" for row in playbook["principles"])
    fourth = playbook["principles"][3]
    assert fourth["title"].endswith("right stage")
    assert fourth["heading_variant"].endswith("right stages")


def test_dpia_sign_off_is_blank():
    record = load_record("syn-harbour-benefits")
    dpia = draft_dpia(record)
    assert dpia["signed_off"] is False
    assert dpia["approved"] is False
    assert len(dpia["steps"]) == 7
    assert dpia["steps"][-1]["title"] == "Sign off and record outcomes"
    assert all(value is None for value in dpia["sign_off"].values())
    assert dpia["high_residual_risk_recorded_in_inventory"] is True
    assert "consult the ICO" in dpia["ico_note"]


def test_duaa_screen_for_the_two_starters_does_not_clear_them():
    foi = screen_duaa(load_record("exp-01-foi-triage"))
    firm = screen_duaa(load_record("exp-02-consumer-duty-complaint-intake"))
    assert foi["screen_result"] == "significant_decision_not_recorded"
    assert firm["screen_result"] == "significant_decision_not_recorded"
    assert foi["lawful"] is None
    assert foi["approved"] is False
    assert foi["determination"] == "not_a_legal_determination"
    assert "wider_process_not_screened" in foi["flags"]
    assert "article_22D_regulations_not_read" in foi["flags"]


def test_duaa_restriction_for_the_fictional_scorer():
    screen = screen_duaa(load_record("syn-harbour-benefits"))
    assert screen["screen_result"] == "restriction_may_apply"
    assert "article_22B_1_restriction_may_apply" in screen["flags"]
    assert "article_22B_4_restriction_may_apply" in screen["flags"]
    assert "article_6_public_authority_limit_check" in screen["flags"]
    assert "article_22C_safeguards_incomplete" in screen["flags"]
    assert screen["approved"] is False
    assert screen["lawful"] is None


def test_law_enforcement_regime_is_not_forced_through_article_22a():
    record = load_record("exp-01-foi-triage")
    record["processing_regime"] = "law_enforcement"
    screen = screen_duaa(record)
    assert screen["screen_result"] == "different_regime"
    assert "adverse" in screen["reading"]


def test_fca_style_row_is_not_a_return():
    firm = draft_fca(load_record("exp-02-consumer-duty-complaint-intake"))
    public = draft_fca(load_record("exp-01-foi-triage"))
    assert firm["scheme_status"] == "not_an_fca_prescribed_return"
    assert firm["approved"] is False
    assert firm["experimental_or_production"] == "not_production"
    assert firm["agent_recorded_as_live"] is False
    assert firm["smf_mapping"] == GAP_TEXT
    assert "not an FCA-regulated firm" in public["audience_note"]


def test_pack_for_both_worked_examples_is_a_draft():
    for inventory_id in ("exp-01-foi-triage", "exp-02-consumer-duty-complaint-intake"):
        pack = build_pack(load_record(inventory_id), "2026-10-24")
        assert pack["approved"] is False
        assert pack["may_be_submitted"] is False
        assert pack["may_be_sent"] is False
        assert pack["actions_taken"] == []
        assert pack["stale"] is False
        assert pack["evaluations_included"] == ["G006", "G007"]
        assert pack["evaluations"]["G006"]["cleared"] is False
        assert pack["evaluations"]["G007"]["groundedness_clearance"] is False
        assert pack["evaluations"]["G007"]["threshold_approved_by_evaluation_owner"] is False
        assert pack["evaluations"]["G007"]["unsupported_claim_count"] == 0
