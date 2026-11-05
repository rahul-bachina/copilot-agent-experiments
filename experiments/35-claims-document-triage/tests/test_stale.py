"""A document date outside the window is a flag, not an outcome."""

from datetime import date

from src.triage import record_handler_classification, triage
from tests.support import amount_pack, period_pack, stale_pack

AS_OF = date(2026, 11, 5)


def test_stale_document_is_still_quoted_and_not_declined():
    draft = triage(stale_pack(), as_of=AS_OF)
    assert draft["do_not_rely"] is True
    invoice = next(file for file in draft["files"] if file["file_id"] == "invoice")
    assert invoice["date_status"] == "stale"
    assert any(item["id"] == "date_not_current:invoice" for item in draft["inconsistency_prompts"])
    assert draft["claim_declined"] is False
    assert draft["scorecard"]["below_threshold"] is False
    assert any(line["source_file_id"] == "invoice" for line in draft["summary"]["lines"])


def test_stale_record_needs_the_handler_to_say_they_reviewed_it():
    draft = triage(stale_pack(), as_of=AS_OF)
    try:
        record_handler_classification(
            draft,
            role="Claims handler",
            classification="escape_of_water",
            file_ids=[file["file_id"] for file in draft["files"]],
            confirms_prompts_checked=True,
            confirms_scorecard_read=True,
            signed_on="2026-11-05",
        )
    except ValueError as exc:
        assert "stale" in str(exc)
    else:
        raise AssertionError("stale pack was recorded without a review confirmation")


def test_amount_and_period_prompts_do_not_fail_the_score():
    amount = triage(amount_pack(), as_of=AS_OF)
    assert any(item["id"].startswith("amount_check:") for item in amount["inconsistency_prompts"])
    assert amount["scorecard"]["below_threshold"] is False
    assert amount["claim_declined"] is False
    period = triage(period_pack(), as_of=AS_OF)
    assert any(item["id"].startswith("period_check:") for item in period["inconsistency_prompts"])
    assert period["coverage_decided"] is False
    assert period["claim_declined"] is False
    assert period["do_not_rely"] is False


def test_source_pin_ages_past_the_window():
    draft = triage(amount_pack(), as_of=date(2027, 5, 5), stale_after_days=90)
    assert draft["sources_stale"] is True
    assert draft["do_not_rely"] is True
    assert draft["claim_accepted"] is False
