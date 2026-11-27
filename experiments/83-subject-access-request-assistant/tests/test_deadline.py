"""The one-month illustration. Neither reading is selected."""

from src.sar import reset_held, scope
from tests.support import document, request


def setup_function():
    reset_held()


def test_the_ico_date_and_the_beginning_with_reading_are_both_shown():
    result = scope(request(received_on="2026-10-03"), as_of="2026-10-20")
    deadline = result["deadline"]
    assert deadline["relevant_time"] == "2026-10-03"
    assert deadline["ico_same_date"] == "2026-11-03"
    assert deadline["ico_end_after_weekend_only"] == "2026-11-03"
    assert deadline["beginning_with_day_before_corresponding_date"] == "2026-11-02"
    assert deadline["readings_differ"] is True
    assert deadline["deadline_selected"] is None
    assert deadline["deadline_decided"] is False
    assert deadline["public_holidays_applied"] is False
    assert deadline["extension_applied"] is False
    assert result["response_sent"] is False


def test_a_short_month_and_a_leap_day_are_not_invented():
    ordinary = scope(request(case_id="SAR-8311", received_on="2026-01-31"), as_of="2026-02-01")
    assert ordinary["deadline"]["ico_same_date"] == "2026-02-28"
    assert ordinary["deadline"]["ico_end_after_weekend_only"] == "2026-03-02"
    assert ordinary["deadline"]["weekend_shift_applied"] is True
    leap = scope(request(case_id="SAR-8312", received_on="2024-01-31"), as_of="2024-02-01")
    assert leap["deadline"]["ico_same_date"] == "2024-02-29"
    assert leap["deadline"]["weekend_shift_applied"] is False


def test_an_ambiguous_received_date_is_not_coerced():
    result = scope(request(received_on="01/02/2024"), as_of="2026-10-20")
    assert result["deadline"]["relevant_time"] is None
    assert result["deadline"]["deadline_selected"] is None
    assert result["deadline"]["coerced"] is False
    assert "received_not_usable" in result["deadline"]["problems"]
    assert "conflicts_seen" in result["required_acknowledgements"]


def test_stop_the_clock_is_illustrative_and_an_open_pause_has_no_end_date():
    paused = scope(
        request(
            case_id="SAR-8313",
            clarification_requested_on="2026-10-10",
            clarification_received_on="2026-10-15",
        ),
        as_of="2026-11-01",
    )
    assert paused["deadline"]["pause_days_if_both_dates_usable"] == 6
    assert paused["deadline"]["illustrated_end_if_pause_confirmed"] == "2026-11-09"
    assert paused["deadline"]["pause_applied_as_a_decision"] is False
    assert paused["deadline"]["extension_notice_sent"] is False
    open_pause = scope(
        request(case_id="SAR-8314", clarification_requested_on="2026-10-10"),
        as_of="2026-11-01",
    )
    assert open_pause["deadline"]["clock_paused_open"] is True
    assert open_pause["deadline"]["illustrated_end_if_pause_confirmed"] is None
    assert open_pause["deadline"]["ico_end_after_weekend_only"] == "2026-11-03"


def test_an_extension_is_proposed_and_not_applied():
    result = scope(
        request(text="This request is complex. Please send all personal data you hold about me. Reference CUS-4401."),
        as_of="2026-10-20",
    )
    assert result["deadline"]["extension_candidate"] is True
    assert result["deadline"]["extension_applied"] is False
    assert result["deadline"]["candidate_three_month_end"] == "2027-01-04"
    assert result["deadline"]["extension_notice_sent"] is False


def test_a_negated_complexity_claim_is_not_an_extension():
    result = scope(
        request(text="It is not true that this request is complex. Please send my personal data. Reference CUS-4401."),
        as_of="2026-10-20",
    )
    assert result["deadline"]["extension_candidate"] is False


def test_law_enforcement_does_not_apply_an_unopened_identity_limb():
    result = scope(
        request(
            case_id="SAR-8315",
            processing_regime="law_enforcement",
            identity_information_received_on="2026-10-10",
            text="This is law enforcement processing. Please send my personal data. Reference CUS-4401.",
        ),
        as_of="2026-10-20",
    )
    assert result["deadline"]["regime"] == "law_enforcement"
    assert result["deadline"]["relevant_time"] == "2026-10-03"
    assert result["deadline"]["identity_date_applied"] is False
    assert "section_52_not_opened_identity_not_applied" in result["deadline"]["problems"]
    assert result["uk_context"]["section_52_opened"] is False


def test_identity_information_moves_the_uk_gdpr_relevant_time():
    result = scope(
        request(identity_information_received_on="2026-10-10", identity_evidence_supplied=True),
        as_of="2026-10-20",
    )
    assert result["deadline"]["relevant_time"] == "2026-10-10"
    assert result["deadline"]["identity_date_applied"] is True
    assert result["deadline"]["ico_same_date"] == "2026-11-10"
    assert result["deadline"]["fee_decided_by_agent"] is False


def test_a_stale_export_and_an_unusable_document_date_are_not_coerced():
    stale = scope(
        request(case_id="SAR-8316", records_exported_on="2026-08-01"),
        as_of="2026-10-20",
    )
    assert stale["records_export"]["stale"] is True
    assert stale["records_export"]["coerced"] is False
    assert stale["records_export"]["starter_rule_not_a_statute"] is True
    assert stale["outcome"] == "route_to_human"
    assert stale["may_be_relied_on"] is False
    recent = scope(request(case_id="SAR-8317", records_exported_on="2026-10-01"), as_of="2026-10-20")
    assert recent["records_export"]["stale"] is False
    assert recent["outcome"] == "draft_for_officer"
    future = scope(
        request(
            case_id="SAR-8318",
            records=[document(document_date="2026-12-01")],
        ),
        as_of="2026-10-20",
    )
    assert future["records_export"]["document_dates"][0]["future"] is True
    assert future["records_export"]["document_dates"][0]["iso"] == "2026-12-01"
    assert future["records_export"]["coerced"] is False
    assert any(item["kind"] == "document_date_future" and item["picked"] is False for item in future["conflicts"])
    blank = scope(
        request(case_id="SAR-8319", records=[document(document_date="31/02/2026")]),
        as_of="2026-10-20",
    )
    assert blank["records_export"]["document_dates"][0]["unparseable"] is True
    assert blank["records_export"]["document_dates"][0]["iso"] is None
    assert blank["records_export"]["document_dates"][0]["coerced"] is False
    same = scope(
        request(case_id="SAR-8327", records=[document(document_date="12/12/2024")]),
        as_of="2026-10-20",
    )
    assert same["records_export"]["document_dates"][0]["ambiguous"] is False
    assert same["records_export"]["document_dates"][0]["iso"] == "2024-12-12"


def test_a_stated_sent_date_is_not_picked_over_the_structured_date():
    result = scope(
        request(text="I sent this on 1 September 2026. Please send my personal data. Reference CUS-4401."),
        as_of="2026-10-20",
    )
    assert result["deadline"]["relevant_time"] == "2026-10-03"
    assert any(item["kind"] == "stated_sent_date" and item["picked"] is False for item in result["conflicts"])
