"""The draft is internal, deterministic, and does not decide."""

import json
from datetime import date

from tests.support import draft_sample, load_example

from src.investigate import NotSynthetic, investigate


def test_sample_is_a_draft_for_the_nominated_officer():
    draft = draft_sample()
    assert draft["label"] == "DRAFT FOR THE NOMINATED OFFICER"
    assert draft["catalogue_id"] == "UK07"
    assert draft["autonomy"] == "A1"
    assert draft["mlro_decision"] is None
    assert draft["sar_filed"] is False
    assert draft["nca_contacted"] is False
    assert draft["daml_requested"] is False
    assert draft["actions_taken"] == []
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["chain_queried"] is False
    assert draft["glossary_codes_assigned"] is False
    assert draft["suspicion_recorded_by_agent"] is False
    assert draft["sar_narrative"]["not_a_disclosure"] is True
    assert draft["sar_narrative"]["not_submitted"] is True
    assert draft["sar_narrative"]["statutory_test_applied"] is False
    assert draft["sar_narrative"]["marc_sentence_applied"] is False
    assert draft["customer_facing"]["drafted"] is False
    assert draft["customer_facing"]["text"] is None


def test_same_case_and_date_produce_the_same_json():
    first = draft_sample()
    second = draft_sample()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_timeline_is_in_time_order_and_quotes_only_synthetic_tokens():
    draft = draft_sample()
    placed = [event for event in draft["evidence_timeline"] if event["placed"] and event["kind"] == "on_chain_hop"]
    assert [event["at"] for event in placed] == sorted(event["at"] for event in placed)
    assert len(placed) == 2
    blob = json.dumps(draft)
    assert "SYNTH-ADDR-CUSTOMER-014" in blob
    assert "SYNTH-TX-0A11B2" in blob
    assert "mixer" in blob
    assert all(item["is_a_suspicion"] is False for item in draft["indicators_for_a_person"])


def test_narrative_does_not_speak_as_if_the_agent_suspects():
    text = draft_sample()["sar_narrative"]["reason_for_suspicion_draft"].lower()
    assert "we suspect" not in text
    assert "i suspect" not in text
    assert "reasonable grounds are made out" not in text
    assert "not a disclosure" in text or "not itself a disclosure" in text
    assert draft_sample()["sar_narrative"]["over_ukfiu_reason_field_limit"] is False


def test_a_case_that_is_not_synthetic_is_refused_without_the_body():
    case = load_example()
    case["synthetic"] = False
    case["analyst_note"] = "LIVE-BODY-SHOULD-NOT-ECHO"
    try:
        investigate(case, as_of=date(2026, 10, 29))
    except NotSynthetic as exc:
        assert "LIVE-BODY-SHOULD-NOT-ECHO" not in str(exc)
    else:
        raise AssertionError("expected NotSynthetic")


def test_missing_customer_still_drafts_and_does_not_file():
    case = load_example()
    del case["customer"]
    draft = investigate(case, as_of=date(2026, 10, 29))
    assert draft["sar_filed"] is False
    assert any("does not describe the relationship" in paragraph for paragraph in draft["investigation_note"]["paragraphs"])
