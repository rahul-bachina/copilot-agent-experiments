"""The summariser cannot contact the customer or change the record."""

import json

from src.summarise import (
    CaseSummaryForbidden,
    accept_summary,
    close_complaint,
    contact_customer,
    decide_outcome,
    offer_redress,
    record_accuracy_check,
    send_external,
    summarise,
    write_case_record,
)
from tests.support import case, event, four_events

AS_OF = "2026-11-09"


def test_direct_actions_raise_and_do_not_return_a_draft():
    for function in (
        contact_customer,
        write_case_record,
        close_complaint,
        offer_redress,
        decide_outcome,
        send_external,
        accept_summary,
    ):
        try:
            function()
        except CaseSummaryForbidden:
            continue
        raise AssertionError(f"{function.__name__} should raise")


def test_a_proposed_contact_fails_and_does_not_set_the_flag():
    draft = summarise(
        case(four_events()),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "fact_key": "next_step",
                "text": "Contact the customer and close the complaint. Offer redress.",
                "citation": {"event_id": "E4", "paragraph": 1, "line_start": 1, "line_end": 1},
            }
        ],
    )
    assert draft["sentences"][0]["verdict"] == "prohibited_action"
    assert draft["customer_contacted"] is False
    assert draft["complaint_closed"] is False
    assert draft["redress_offered"] is False
    assert draft["record_changed"] is False
    assert draft["case_outcome"] is None


def test_accuracy_check_does_not_contact_or_write_and_the_agent_path_cannot_set_it():
    draft = summarise(case(four_events()), AS_OF)
    assert draft["accuracy_checked"] is False
    refused = record_accuracy_check(
        draft,
        {"decision": "contact_customer", "role": "Service representative", "name": "Sam Representative"},
    )
    assert refused["review"]["refused"] is True
    assert refused["review"]["reason"] == "prohibited_decision"
    assert refused["customer_contacted"] is False
    assert refused["accuracy_checked"] is False
    checked = record_accuracy_check(
        draft,
        {
            "role": "Service representative",
            "name": "Sam Representative",
            "sentences": [
                {"sentence_id": row["sentence_id"], "mark": "read"} for row in draft["sentences"]
            ],
        },
    )
    assert checked["accuracy_checked"] is True
    assert checked["human_approval"]["role"] == "Service representative"
    assert checked["customer_contacted"] is False
    assert checked["record_changed"] is False
    assert checked["case_outcome"] is None
    assert checked["actions_taken"] == []


def test_a_gap_cannot_be_marked_accurate():
    draft = summarise(case(four_events()[:3]), AS_OF)
    assert draft["do_not_rely"] is True
    reviewed = record_accuracy_check(
        draft,
        {
            "role": "Service representative",
            "name": "Sam Representative",
            "sentences": [
                {"sentence_id": row["sentence_id"], "mark": "read"} for row in draft["sentences"]
            ],
        },
    )
    assert reviewed["accuracy_checked"] is False
    assert reviewed["review"]["reason"] == "not_a_complete_current_reading"


def test_the_agent_name_cannot_check_accuracy():
    draft = summarise(case(four_events()), AS_OF)
    reviewed = record_accuracy_check(
        draft,
        {
            "role": "Service representative",
            "name": "agent",
            "sentences": [
                {"sentence_id": row["sentence_id"], "mark": "read"} for row in draft["sentences"]
            ],
        },
    )
    assert reviewed["accuracy_checked"] is False
    assert reviewed["review"]["reason"] == "name"


def test_a_non_synthetic_case_is_refused_without_copying_the_text():
    payload = {
        "synthetic": False,
        "case_id": "REAL-1",
        "sector": "housing",
        "events": [event("E1", "2026-10-20", "what_happened", "TOKEN-REAL-CASE-41")],
    }
    draft = summarise(payload, AS_OF)
    assert draft["refused"] is True
    assert draft["reason"] == "not_synthetic"
    assert "TOKEN-REAL-CASE-41" not in json.dumps(draft)
    assert draft["customer_contacted"] is False
    assert draft["record_changed"] is False


def test_unknown_sector_is_refused():
    draft = summarise(case(four_events(), sector="retail"), AS_OF)
    assert draft["refused"] is True
    assert draft["reason"] == "sector_not_in_list"
    assert "Mereford" not in json.dumps(draft)
