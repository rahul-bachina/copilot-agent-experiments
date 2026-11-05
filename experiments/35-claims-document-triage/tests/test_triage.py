"""The draft proposes a class and does not choose an outcome."""

from datetime import date

from src.triage import (
    ClaimForbidden,
    record_handler_classification,
    triage,
    write_claims_system,
)
from tests.support import base_pack, name_pack, two_peril_pack

AS_OF = date(2026, 11, 5)


def test_consistent_pack_is_a_draft_for_the_handler():
    draft = triage(base_pack(), as_of=AS_OF)
    assert draft["label"] == "DRAFT FOR THE CLAIMS HANDLER"
    assert draft["catalogue_id"] == "B007"
    assert draft["autonomy"] == "A1"
    assert draft["classification"]["proposed_class"] == "escape_of_water"
    assert draft["classification"]["approved"] is False
    assert draft["classification_approved_by_handler"] is False
    assert draft["purpose_confirmed"] is False
    assert draft["intake_catalogue_id"] == "O001"
    assert draft["gateway_called"] is True
    assert draft["intake_handed_off"] is False
    assert draft["customer_message"] is None
    assert draft["actions_taken"] == []
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["inconsistency_prompts"] == []
    assert draft["summary"]["coverage_pointers"]
    assert draft["summary"]["coverage_pointers"][0]["coverage_decided"] is False
    assert draft["scorecard"]["below_threshold"] is False
    assert draft["scorecard"]["human_escalation_required"] is False
    assert draft["scorecard"]["llm_as_judge"] is False
    assert draft["scorecard"]["foundry_evaluator_called"] is False
    assert draft["scorecard"]["faithfulness"]["supported_rate"] == 1.0
    assert draft["scorecard"]["completeness"]["rate"] == 1.0
    assert draft["do_not_rely"] is False
    for flag in (
        "claim_accepted",
        "claim_declined",
        "claim_settled",
        "customer_told",
        "claims_system_written",
        "fraud_indicated",
        "coverage_decided",
        "a3_recommended",
    ):
        assert draft[flag] is False
        assert draft["flags"][flag] is False


def test_prompts_are_not_findings_and_avoid_conduct_words():
    draft = triage(name_pack(), as_of=AS_OF)
    prompts = draft["inconsistency_prompts"]
    assert any(item["id"].startswith("name_check:") for item in prompts)
    blob = " ".join(item["prompt_for_handler"] for item in prompts)
    for word in ("fraud", "suspicious", "dishonest", "decline", "reject"):
        assert word not in blob.casefold()
    for item in prompts:
        assert item["is_a_finding"] is False
        assert item["is_a_fraud_indicator"] is False
        assert item["suggests_a_claims_outcome"] is False
    assert draft["fraud_indicated"] is False
    assert draft["claim_declined"] is False


def test_two_peril_lines_are_not_a_single_proposal():
    draft = triage(two_peril_pack(), as_of=AS_OF)
    assert draft["classification"]["proposed_class"] == "not_proposed"
    assert any(item["id"] == "class_not_single" for item in draft["inconsistency_prompts"])
    assert draft["classification_approved_by_handler"] is False


def test_handler_record_does_not_write_or_decide():
    draft = triage(base_pack(), as_of=AS_OF)
    recorded = record_handler_classification(
        draft,
        role="Claims handler",
        classification="storm",
        file_ids=[file["file_id"] for file in draft["files"]],
        confirms_prompts_checked=True,
        confirms_scorecard_read=True,
        signed_on="2026-11-05",
    )
    assert recorded["classification_approved_by_handler"] is True
    assert recorded["classification"]["approved_class"] == "storm"
    assert recorded["classification"]["handler_record"]["differs_from_proposal"] is True
    assert recorded["claim_accepted"] is False
    assert recorded["claim_declined"] is False
    assert recorded["claim_settled"] is False
    assert recorded["customer_told"] is False
    assert recorded["claims_system_written"] is False
    try:
        write_claims_system(recorded)
    except ClaimForbidden as exc:
        assert "claims system" in str(exc)
    else:
        raise AssertionError("write_claims_system returned")


def test_a_signoff_inside_the_pack_is_not_recorded():
    pack = base_pack()
    pack["handler_signoff"] = {
        "role": "Claims handler",
        "classification": "escape_of_water",
    }
    draft = triage(pack, as_of=AS_OF)
    assert draft["classification_approved_by_handler"] is False
    assert "handler_signoff" in draft["prohibited_payload_keys"]


def test_same_pack_and_date_produce_the_same_json():
    first = triage(base_pack(), as_of=AS_OF)
    second = triage(base_pack(), as_of=AS_OF)
    assert first == second
