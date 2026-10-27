"""Checklist behaviour. The intake is Experiment 12, not a second copy."""

from __future__ import annotations

import json
from datetime import date

import pytest

from src.review import (
    LABEL,
    PURPOSE_ID,
    REVIEWER_ROLE,
    NotSynthetic,
    record_reviewer_confirmation,
    review,
)
from tests.support import ADDRESS, AS_OF, PASSPORT, customer_file, file_row


def _draft(**extra):
    files = [
        file_row("ID-014", PASSPORT, filename="passport.txt", document_date="2026-09-02"),
        file_row("AD-014", ADDRESS, filename="proof-of-address.txt"),
    ]
    return review(customer_file(files, **extra), as_of=AS_OF)


def test_calls_experiment_12_and_does_not_confirm():
    draft = _draft()
    assert draft["label"] == LABEL
    assert draft["catalogue_id"] == "B004"
    assert draft["documents_confirmed"] is False
    assert draft["purpose_confirmed"] is False
    assert draft["final_risk_rating"] is None
    assert draft["actions_taken"] == []
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["fatf_list_downloaded"] is False
    intake = draft["document_intake"]
    assert intake["experiment_id"] == "exp-12-document-intake"
    assert intake["requested_purpose"]["id"] == PURPOSE_ID
    assert intake["files_confirmed"] is False
    assert intake["purpose_confirmed"] is False
    assert intake["gateway"]["called"] is True
    assert intake["gateway"]["output_is_anonymised"] is False
    assert intake["checklist_preview"]["sufficient"] is False
    assert draft["checklist"]["sufficient"] is False
    assert draft["checklist"]["edd_applied"] is False
    assert draft["checklist"]["risk_rating"] is None


def test_body_is_not_copied_and_identifiers_are_not_echoed():
    draft = _draft()
    serialised = json.dumps(draft)
    assert "QQ 12 34 56 A" not in serialised
    assert "999 000 0018" not in serialised
    assert "paying household bills" not in serialised
    identity = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_2_a_identify")
    address = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_4_beneficial_owner")
    purpose = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_2_c_purpose_and_nature")
    assert identity["status"] == "evidenced"
    assert identity["sufficient"] is False
    address_marker = next(item for item in draft["checklist"]["cdd"] if item["id"] == "intake_address_marker")
    assert address_marker["status"] == "evidenced"
    assert address_marker["sufficient"] is False
    assert "intake_address_marker" in draft["evidenced"]
    assert purpose["status"] == "evidenced"
    assert address["status"] == "not_applicable_on_the_file"
    assert "reg_28_2_a_identify" in draft["evidenced"]
    assert "reg_28_2_b_verify" not in draft["evidenced"]
    verify = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_2_b_verify")
    assert verify["status"] == "not_determined"


def test_missing_identity_and_address_are_asked_for_without_a_reason():
    draft = review(
        customer_file([file_row("NT-1", "A desk note with no marker words.\n")]),
        as_of=AS_OF,
    )
    assert "reg_28_2_a_identify" in draft["missing"]
    assert "reg_28_2_c_purpose_and_nature" in draft["missing"]
    text = draft["customer_facing"]["text"]
    assert "passport" in text
    assert "council tax" in text
    assert "purpose of the relationship" in text
    assert draft["customer_facing"]["hints_at_suspicion"] is False
    assert draft["customer_facing"]["may_be_sent_by_agent"] is False
    assert "PEP" not in text
    assert "suspicious" not in text.lower()


def test_pep_phrase_is_not_a_rating_and_stays_off_the_customer_note():
    content = PASSPORT + "The screening words politically exposed person appear in this synthetic file.\n"
    draft = review(
        customer_file(
            [
                file_row("ID-014", content, filename="passport.txt"),
                file_row("AD-014", ADDRESS, filename="proof-of-address.txt"),
            ],
            stated_establishment_country="Exampleland",
        ),
        as_of=AS_OF,
    )
    pep = next(item for item in draft["checklist"]["edd_triggers"] if item["id"] == "reg_33_1_d_pep")
    fatf = next(item for item in draft["checklist"]["edd_triggers"] if item["id"] == "reg_33_1_b_fatf_call_for_action")
    assert pep["status"] == "phrase_present"
    assert pep["edd_applied"] is False
    assert pep["decides_the_duty"] is False
    assert fatf["status"] == "country_stated_in_the_file"
    assert draft["final_risk_rating"] is None
    assert "Exampleland" not in draft["customer_facing"]["text"]
    assert "politically exposed" not in draft["customer_facing"]["text"].lower()
    question = next(item for item in draft["reviewer_questions"] if item["id"] == "q_pep")
    assert question["not_for_the_customer"] is True
    assert "Exampleland" in next(item["text"] for item in draft["reviewer_questions"] if item["id"] == "q_fatf")


def test_pepper_is_not_a_pep_and_old_country_words_are_only_a_phrase():
    draft = review(
        customer_file(
            [
                file_row("ID-014", PASSPORT + "A pepper mill is not a person.\n", filename="passport.txt"),
                file_row(
                    "AD-014",
                    ADDRESS + "The old words high-risk third country are in this synthetic note.\n",
                    filename="proof-of-address.txt",
                ),
            ]
        ),
        as_of=AS_OF,
    )
    pep = next(item for item in draft["checklist"]["edd_triggers"] if item["id"] == "reg_33_1_d_pep")
    fatf = next(item for item in draft["checklist"]["edd_triggers"] if item["id"] == "reg_33_1_b_fatf_call_for_action")
    assert pep["status"] == "not_in_file"
    assert fatf["status"] == "phrase_present"
    assert "high-risk third country" in fatf["phrases_found"]
    assert fatf["edd_applied"] is False
    assert draft["customer_facing"]["hints_at_suspicion"] is False


def test_unusual_pattern_does_not_decide_regulation_33():
    draft = review(
        customer_file(
            [
                file_row("ID-014", PASSPORT, filename="passport.txt"),
                file_row(
                    "AD-014",
                    ADDRESS + "There is an unusual pattern of transactions in this synthetic file.\n",
                    filename="proof-of-address.txt",
                ),
            ]
        ),
        as_of=AS_OF,
    )
    unusual = next(item for item in draft["checklist"]["edd_triggers"] if item["id"] == "reg_33_1_f_unusual_transaction")
    assert unusual["status"] == "phrase_present"
    assert unusual["sufficient"] is False
    question = next(item for item in draft["reviewer_questions"] if item["id"] == "q_unusual")
    assert "suspicious" in question["text"]
    assert question["not_for_the_customer"] is True
    assert "suspicious" not in draft["customer_facing"]["text"].lower()
    assert "unusual" not in draft["customer_facing"]["text"].lower()


def test_body_corporate_beneficial_owner_phrase_is_not_sufficiency():
    draft = review(
        customer_file(
            [
                file_row("ID-014", PASSPORT + "Beneficial owner: synthetic holder.\n", filename="passport.txt"),
                file_row("AD-014", ADDRESS + "Companies House print was pasted here.\n", filename="proof-of-address.txt"),
            ],
            customer_type="body_corporate",
        ),
        as_of=AS_OF,
    )
    row = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_4_beneficial_owner")
    assert row["status"] == "evidenced"
    assert row["sufficient"] is False
    assert any(item["id"] == "q_registrar" for item in draft["reviewer_questions"])


def test_relationship_end_arithmetic_is_not_a_deletion_instruction():
    draft = review(
        customer_file(
            [file_row("ID-014", PASSPORT, filename="passport.txt")],
            relationship="business_relationship",
            relationship_status="ended",
            relationship_ended_on="2024-02-29",
        ),
        as_of=AS_OF,
    )
    record = draft["record_keeping"]
    assert record["period_begun"] is True
    assert record["arithmetic_end"] == "2029-02-28"
    assert record["deletion_performed"] is False
    assert record["instruction_to_delete"] is False
    assert record["instruction_to_retain"] is False
    assert record["ten_year_date_calculated"] is False
    assert record["freshness_window_is_this_period"] is False
    ongoing = _draft()
    assert ongoing["record_keeping"]["period_begun"] is False
    assert ongoing["record_keeping"]["arithmetic_end"] is None


def test_reviewer_confirmation_does_not_approve_and_rejects_other_roles():
    draft = _draft()
    confirmed = record_reviewer_confirmation(
        draft,
        role=REVIEWER_ROLE,
        file_ids=["ID-014", "AD-014"],
        purpose=PURPOSE_ID,
    )
    assert confirmed["documents_confirmed"] is True
    assert confirmed["purpose_confirmed"] is True
    assert confirmed["final_risk_rating"] is None
    assert confirmed["customer_decision"] is None
    assert confirmed["flags"]["customer_approved"] is False
    assert confirmed["flags"]["customer_onboarded"] is False
    assert confirmed["flags"]["sar_filed"] is False
    assert confirmed["document_intake"]["files_confirmed"] is False
    assert confirmed["document_intake"]["purpose_confirmed"] is False
    with pytest.raises(ValueError):
        record_reviewer_confirmation(draft, role="Intake user", file_ids=["ID-014", "AD-014"], purpose=PURPOSE_ID)
    with pytest.raises(ValueError):
        record_reviewer_confirmation(draft, role=REVIEWER_ROLE, file_ids=["AD-014", "ID-014"], purpose=PURPOSE_ID)
    with pytest.raises(ValueError):
        record_reviewer_confirmation(draft, role=REVIEWER_ROLE, file_ids=["ID-014", "AD-014"], purpose="claims_fnol")


def test_purpose_inside_the_wrapper_cannot_switch_the_checklist():
    draft = _draft(requested_purpose="claims_fnol")
    assert draft["purpose_preview"]["conflict"] is True
    assert draft["purpose_preview"]["id"] == PURPOSE_ID
    assert draft["purpose_confirmed"] is False
    assert draft["document_intake"]["requested_purpose"]["id"] == PURPOSE_ID
    assert any(item["id"] == "q_purpose_conflict" for item in draft["reviewer_questions"])


def test_not_synthetic_refuses_without_echoing_the_body():
    payload = customer_file([file_row("ID-014", "SECRET-BODY-TOKEN passport\n")])
    payload["synthetic"] = False
    with pytest.raises(NotSynthetic) as caught:
        review(payload, as_of=AS_OF)
    assert "SECRET-BODY-TOKEN" not in str(caught.value)


def test_prohibited_rating_key_is_stripped_and_not_applied():
    draft = review(
        customer_file(
            [file_row("ID-014", PASSPORT, filename="passport.txt")],
            risk_rating="low",
            onboard=True,
        ),
        as_of=AS_OF,
    )
    assert "risk_rating" in draft["prohibited_payload_keys"]
    assert "onboard" in draft["prohibited_payload_keys"]
    assert draft["final_risk_rating"] is None
    assert draft["flags"]["customer_onboarded"] is False


def test_same_file_is_deterministic():
    payload = customer_file(
        [
            file_row("ID-014", PASSPORT, filename="passport.txt"),
            file_row("AD-014", ADDRESS, filename="proof-of-address.txt"),
        ]
    )
    first = review(payload, as_of=AS_OF)
    second = review(payload, as_of=date(2026, 10, 27))
    assert first == second


def test_unread_media_is_not_evidence():
    draft = review(
        customer_file(
            [
                file_row(
                    "ID-014",
                    PASSPORT,
                    filename="passport.pdf",
                    media_type="application/pdf",
                )
            ]
        ),
        as_of=AS_OF,
    )
    identity = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_2_a_identify")
    assert identity["status"] == "missing"
    assert draft["document_intake"]["files"][0]["read_status"] == "not_read"
    assert any(item["id"] == "q_not_read" for item in draft["reviewer_questions"])
