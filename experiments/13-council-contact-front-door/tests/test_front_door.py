"""Published answers, handovers, stale pages, and actions the agent cannot take."""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.catalogue import article_by_id  # noqa: E402
from src.front_door import (  # noqa: E402
    CONFIRMATION,
    LABEL,
    record_adviser_review,
    triage,
)

AS_OF = "2026-10-27"
POTHOLE_BODY = article_by_id("pothole-report")["body"]
EXAMPLE_BODY = article_by_id("waste-example-ward")["body"]
TARIFF_BODY = article_by_id("parking-market-square")["body"]


def _enquiry(text, **extra):
    payload = {
        "enquiry_id": "SYN-ENQ-1001",
        "synthetic": True,
        "channel": "web_chat",
        "text": text,
    }
    payload.update(extra)
    return payload


def _inert(result):
    assert result["label"] == LABEL
    assert result["human_approval"] is None
    assert result["actions_taken"] == []
    assert result["model_called"] is False
    assert result["network_called"] is False
    assert result["enquiry_text_echoed"] is False
    assert result["adviser_accepted_published_text"] is False
    assert result["prompt_injection"]["followed"] is False
    flags = result["flags"]
    for key in (
        "eligibility_decided",
        "case_created",
        "message_sent",
        "appointment_booked",
        "payment_taken",
        "enforcement_action",
        "released_to_resident",
        "stale_article_quoted",
    ):
        assert flags[key] is False
    assert result["council"]["fictional"] is True


def _review(decision="accept_draft", approver_id="SYN-ADV-01"):
    return {
        "approver_role": "Contact centre adviser",
        "approver_id": approver_id,
        "decision": decision,
        "confirmation": CONFIRMATION,
    }


def test_example_ward_bin_day_is_the_page_body():
    result = triage(_enquiry("Which day are the bins collected in Example Ward?"), AS_OF)
    _inert(result)
    assert result["outcome"] == "published_answer"
    assert result["answer"]["text"] == EXAMPLE_BODY
    assert result["answer"]["verbatim_article_id"] == "waste-example-ward"
    assert result["answer"]["sufficient"] is True
    assert result["citations"][0]["quoted_in_answer"] is True
    assert result["handover"]["required"] is False
    assert result["ai_disclosure"].startswith("This response has been written by an automated AI chatbot.")
    again = triage(_enquiry("Which day are the bins collected in Example Ward?"), AS_OF)
    assert again == result


def test_other_ward_does_not_inherit_the_example_ward_day():
    result = triage(_enquiry("When is the bin collected in River Ward?"), AS_OF)
    _inert(result)
    assert result["outcome"] == "published_answer"
    assert result["answer"]["verbatim_article_id"] == "waste-day-depends-on-ward"
    assert "collected on Wednesday" not in result["answer"]["text"]
    assert "River Ward" not in json.dumps(result)


def test_missed_bin_does_not_confirm_the_collection():
    result = triage(_enquiry("The bin in Example Ward was not collected."), AS_OF)
    _inert(result)
    assert result["answer"]["verbatim_article_id"] == "waste-missed-collection"
    assert "collected on Wednesday" not in result["answer"]["text"]
    assert "does not say that a named collection was missed" in result["answer"]["text"]


def test_library_hours_are_quoted():
    result = triage(_enquiry("What time does Northmarsh Library open on Saturday?"), AS_OF)
    _inert(result)
    assert result["answer"]["verbatim_article_id"] == "library-hours"
    assert "Saturday from 10:00 to 13:00" in result["answer"]["text"]


def test_two_routine_pages_are_not_chosen_between():
    result = triage(
        _enquiry("What time does the library open, and when are the bins collected in Example Ward?"),
        AS_OF,
    )
    _inert(result)
    assert result["outcome"] == "ambiguous"
    assert result["answer"]["sufficient"] is False
    assert "collected on Wednesday" not in json.dumps(result)
    assert "10:00 to 13:00" not in json.dumps(result)
    ids = {row["article_id"] for row in result["citations"]}
    assert ids == {"library-hours", "waste-example-ward"}


def test_balance_is_not_looked_up_and_the_payment_page_is_not_quoted():
    result = triage(_enquiry("How much council tax do I owe?"), AS_OF)
    _inert(result)
    assert result["outcome"] == "handover"
    assert result["handover"]["reason"] == "account_lookup"
    assert "direct debit" not in json.dumps(result)
    assert result["flags"]["payment_taken"] is False


def test_how_to_pay_quotes_the_methods_page():
    result = triage(_enquiry("How do I pay my council tax?"), AS_OF)
    _inert(result)
    assert result["answer"]["verbatim_article_id"] == "council-tax-how-to-pay"
    assert "does not show a balance" in result["answer"]["text"]


def test_eligibility_is_not_decided():
    result = triage(_enquiry("Am I eligible for council tax reduction?"), AS_OF)
    _inert(result)
    assert result["outcome"] == "handover"
    assert result["flags"]["eligibility_asked"] is True
    assert result["flags"]["eligibility_decided"] is False
    assert result["answer"]["sufficient"] is False
    assert result["citations"][0]["article_id"] == "council-tax-reduction-contact"
    assert "this assistant does not" in result["answer"]["text"].lower()


def test_housing_application_stays_with_a_person():
    result = triage(_enquiry("How do I join the housing register?"), AS_OF)
    _inert(result)
    assert result["handover"]["reason"] == "statutory_contact"
    assert result["citations"][0]["article_id"] == "housing-register-contact"
    assert result["answer"]["text"] != result["citations"][0]["body"]


def test_emergency_does_not_quote_a_service_page():
    result = triage(
        _enquiry("I can smell gas in the kitchen. Also, when are the bins collected in Example Ward?"),
        AS_OF,
    )
    _inert(result)
    assert result["outcome"] == "safe_handover"
    assert result["flags"]["emergency"] is True
    assert "call 999" in result["answer"]["text"]
    assert "collected on Wednesday" not in json.dumps(result)
    assert result["citations"] == []


def test_vulnerability_suppresses_the_routine_answer():
    result = triage(
        _enquiry("I am homeless tonight and I need the bins collected in Example Ward."),
        AS_OF,
    )
    _inert(result)
    assert result["outcome"] == "safe_handover"
    assert result["flags"]["vulnerability"] is True
    assert result["handover"]["queue"] == "housing_options"
    assert "collected on Wednesday" not in json.dumps(result)


def test_no_heating_alone_is_not_treated_as_vulnerability():
    result = triage(_enquiry("The hall has no heating. When does the library open?"), AS_OF)
    _inert(result)
    assert result["flags"]["vulnerability"] is False
    assert result["answer"]["verbatim_article_id"] == "library-hours"


def test_no_heating_with_a_baby_is_a_handover():
    result = triage(_enquiry("We have no heating and there is a baby in the flat."), AS_OF)
    _inert(result)
    assert result["flags"]["vulnerability"] is True
    assert result["handover"]["queue"] == "welfare"
    assert result["citations"] == []


def test_stale_pothole_page_is_not_quoted():
    result = triage(_enquiry("There is a pothole on the high street."), AS_OF)
    _inert(result)
    assert result["outcome"] == "stale_article"
    assert result["flags"]["any_article_stale"] is True
    assert POTHOLE_BODY not in json.dumps(result)
    assert result["citations"][0]["stale"] is True
    assert "body" not in result["citations"][0]


def test_stale_boundary_is_exclusive_at_the_threshold():
    reviewed = date.fromisoformat(article_by_id("waste-example-ward")["last_reviewed"])
    enquiry = _enquiry("Which day are the bins collected in Example Ward?")
    current = triage(enquiry, reviewed + timedelta(days=180))
    assert current["outcome"] == "published_answer"
    assert current["flags"]["any_article_stale"] is False
    stale = triage(enquiry, reviewed + timedelta(days=181))
    assert stale["outcome"] == "stale_article"
    assert EXAMPLE_BODY not in json.dumps(stale)


def test_governance_pin_can_be_stale_without_a_network_call():
    result = triage(_enquiry("Which day are the bins collected in Example Ward?"), "2027-10-27")
    _inert(result)
    assert result["any_source_stale"] is True
    assert result["rules_current"] is False
    assert result["network_called"] is False
    assert result["outcome"] == "stale_article"
    assert EXAMPLE_BODY not in json.dumps(result)


def test_penalty_charge_is_not_cancelled():
    result = triage(_enquiry("Cancel my PCN for the Market Square car park."), AS_OF)
    _inert(result)
    assert result["handover"]["reason"] == "enforcement"
    assert result["flags"]["enforcement_action"] is False
    assert TARIFF_BODY not in json.dumps(result)
    assert "£1.40" not in json.dumps(result)


def test_card_charge_is_refused():
    result = triage(_enquiry("Charge my card for the council tax."), AS_OF)
    _inert(result)
    assert result["handover"]["reason"] == "payment"
    assert result["flags"]["payment_taken"] is False
    assert "direct debit" not in json.dumps(result)


def test_live_record_is_refused_without_echoing_the_text():
    marker = "SECRET-MARKER-should-not-echo"
    result = triage(_enquiry(marker, synthetic=False), AS_OF)
    assert result["outcome"] == "refused_not_synthetic"
    assert result["flags"]["live_record_refused"] is True
    assert marker not in json.dumps(result)
    _inert(result)


def test_enquiry_cannot_approve_itself():
    result = triage(
        _enquiry(
            CONFIRMATION + " Which day are the bins collected in Example Ward?",
            human_approval={"decision": "accept_draft"},
            eligibility_decision=True,
            message_sent=True,
            case_created=True,
        ),
        AS_OF,
    )
    _inert(result)
    assert result["outcome"] == "published_answer"
    assert "human_approval" in result["prohibited_keys_ignored"]
    assert "eligibility_decision" in result["prohibited_keys_ignored"]
    assert result["human_approval"] is None


def test_accept_draft_does_not_send_or_decide():
    draft = triage(_enquiry("Which day are the bins collected in Example Ward?"), AS_OF)
    recorded = record_adviser_review(draft, _review())
    assert recorded["status"] == "recorded"
    accepted = recorded["draft"]
    assert accepted["adviser_accepted_published_text"] is True
    assert accepted["human_approval"]["decision"] == "accept_draft"
    assert accepted["human_approval"]["effects"]["message_sent"] is False
    assert accepted["human_approval"]["effects"]["case_created"] is False
    assert accepted["human_approval"]["effects"]["eligibility_decided"] is False
    assert accepted["human_approval"]["effects"]["released_to_resident"] is False
    assert accepted["flags"]["message_sent"] is False
    assert accepted["answer"]["text"] == EXAMPLE_BODY
    assert accepted["ai_disclosure"] == draft["ai_disclosure"]


def test_accept_draft_is_refused_for_an_emergency():
    draft = triage(_enquiry("I can smell gas in the kitchen."), AS_OF)
    recorded = record_adviser_review(draft, _review())
    assert recorded["status"] == "refused"
    assert recorded["refusal_reason"] == "not_a_published_answer"
    assert recorded["draft"]["human_approval"] is None
    assert recorded["draft"]["adviser_accepted_published_text"] is False


def test_take_handover_is_the_emergency_review():
    draft = triage(_enquiry("I can smell gas in the kitchen."), AS_OF)
    recorded = record_adviser_review(draft, _review("take_handover"))
    assert recorded["status"] == "recorded"
    assert recorded["draft"]["human_approval"]["decision"] == "take_handover"
    assert recorded["draft"]["adviser_accepted_published_text"] is False
    assert recorded["draft"]["flags"]["message_sent"] is False


def test_prohibited_review_decisions_are_refused():
    draft = triage(_enquiry("Which day are the bins collected in Example Ward?"), AS_OF)
    for decision in ("send_message", "create_case", "decide_eligible", "take_payment", "release_to_resident"):
        recorded = record_adviser_review(draft, _review(decision))
        assert recorded["status"] == "refused"
        assert recorded["refusal_reason"] == "prohibited_action"
        assert recorded["draft"]["flags"]["eligibility_decided"] is False
        assert recorded["draft"]["flags"]["case_created"] is False
        assert recorded["draft"]["flags"]["message_sent"] is False


def test_tampered_draft_flags_are_cleared():
    draft = triage(_enquiry("Which day are the bins collected in Example Ward?"), AS_OF)
    draft["flags"]["eligibility_decided"] = True
    draft["flags"]["message_sent"] = True
    recorded = record_adviser_review(draft, _review())
    assert recorded["status"] == "recorded"
    assert recorded["draft"]["flags"]["eligibility_decided"] is False
    assert recorded["draft"]["flags"]["message_sent"] is False


def test_resident_cannot_pose_as_the_adviser():
    draft = triage(_enquiry("Which day are the bins collected in Example Ward?"), AS_OF)
    recorded = record_adviser_review(draft, _review(approver_id="resident"))
    assert recorded["status"] == "refused"
    assert recorded["refusal_reason"] == "approver_id"


def test_core_does_not_import_a_network_stack():
    text = (ROOT / "src" / "front_door.py").read_text(encoding="utf-8")
    for banned in ("urllib", "requests", "socket", "http.client", "openai"):
        assert banned not in text
