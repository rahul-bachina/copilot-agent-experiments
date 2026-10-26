"""Field comparison, sunrise handling, and the empty analyst decision."""

import copy
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.triage import LABEL, triage  # noqa: E402
from tests.support import clean_inbound, party  # noqa: E402


def _option(result, option_id):
    return next(item for item in result["options"] if item["id"] == option_id)


def _assert_inert(result):
    assert result["analyst_decision"] is None
    assert result["actions_taken"] == []
    assert result["model_called"] is False
    assert result["network_called"] is False
    flags = result["flags"]
    assert flags["transfer_held_by_agent"] is False
    assert flags["transfer_returned_by_agent"] is False
    assert flags["transfer_rejected_by_agent"] is False
    assert flags["transfer_released_by_agent"] is False
    assert flags["sar_filed"] is False
    assert flags["counterparty_contacted"] is False
    assert flags["fca_report_made"] is False
    assert flags["cryptoasset_made_available_by_agent"] is False
    assert flags["fca_statement_treated_as_waiver"] is False
    assert flags["exclusion_confirmed_by_agent"] is False
    assert flags["jmlsg_euro_threshold_used"] is False
    assert result["human_review"]["agent_recorded_decision"] is None
    for option in result.get("options", []):
        assert option["agent_will_not_take"] is True


def test_clean_inbound_proposes_nothing_and_does_not_release():
    result = triage(clean_inbound(), as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert result["label"] == LABEL
    assert "no_exception_on_these_fields" in result["exception_categories"]
    assert result["missing"] == []
    assert result["mismatches"] == []
    assert _option(result, "hold")["proposed"] is False
    assert _option(result, "return")["proposed"] is False
    assert _option(result, "escalate")["proposed"] is False
    assert result["threshold"]["paragraph_6_must_accompany"] is False


def test_same_record_is_deterministic():
    record = clean_inbound()
    assert triage(record, as_of=date(2026, 10, 26)) == triage(copy.deepcopy(record), as_of=date(2026, 10, 26))


def test_missing_beneficiary_name_proposes_hold_and_return():
    record = clean_inbound()
    record["information_on_transfer"]["beneficiary"]["name"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert "missing_information" in result["exception_categories"]
    assert any(item["field"] == "beneficiary.name" for item in result["missing"])
    assert _option(result, "hold")["proposed"] is True
    assert "64D(2)(c)(i)" in _option(result, "hold")["reason"]
    assert _option(result, "return")["proposed"] is True
    assert "reasonable time" in _option(result, "return")["reason"]
    assert _option(result, "escalate")["proposed"] is False
    assert any(step["id"] == "request_missing_information_from_counterparty" for step in result["firm_steps_for_a_person"])


def test_name_mismatch_is_not_cleared_by_truncation_guidance():
    record = clean_inbound()
    record["information_on_transfer"]["beneficiary"]["name"] = "Sam R"
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert "non_corresponding_information" in result["exception_categories"]
    assert result["mismatches"][0]["field"] == "beneficiary.name"
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "return")["proposed"] is True
    assert any("does not clear" in line for line in result["explanation"])


def test_case_and_spacing_alone_are_not_a_mismatch():
    record = clean_inbound()
    record["information_on_transfer"]["beneficiary"]["name"] = "  sam   rivera "
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["mismatches"] == []
    assert "no_exception_on_these_fields" in result["exception_categories"]


def test_800_pounds_requires_paragraph_6_when_not_all_uk():
    originator = party(address=None)
    record = clean_inbound(
        firm_role="originator",
        value_gbp=800,
        all_executing_businesses_in_uk=False,
        information_on_transfer={"originator": originator, "beneficiary": party(name="Sam Rivera", account_number="SYNTH-WALLET-BENE-001")},
    )
    record["counterparty"]["in_united_kingdom"] = False
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert result["threshold"]["at_or_over_800"] is True
    assert result["threshold"]["paragraph_6_must_accompany"] is True
    assert any(item["field"] == "originator.paragraph_6" for item in result["missing"])
    assert _option(result, "hold")["proposed"] is True
    assert "64C(9)" in _option(result, "hold")["reason"]
    assert _option(result, "return")["proposed"] is False


def test_799_pounds_does_not_require_paragraph_6():
    originator = party(address=None)
    record = clean_inbound(
        value_gbp="799.99",
        all_executing_businesses_in_uk=False,
        information_on_transfer={"originator": originator, "beneficiary": party(name="Sam Rivera", account_number="SYNTH-WALLET-BENE-001")},
    )
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["threshold"]["at_or_over_800"] is False
    assert result["threshold"]["paragraph_6_must_accompany"] is False
    assert not any(item["field"] == "originator.paragraph_6" for item in result["missing"])
    assert result["jmlsg_euro_threshold_used"] is False


def test_missing_sterling_figure_does_not_assume_a_side_of_the_threshold():
    record = clean_inbound(value_gbp=None, all_executing_businesses_in_uk=False)
    record["information_on_transfer"]["originator"]["address"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["threshold"]["operative"] is False
    assert result["threshold"]["paragraph_6_must_accompany"] == "cannot_tell"
    assert "threshold_not_operative" in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "return")["proposed"] is False


def test_all_uk_over_800_does_not_require_paragraph_6_to_accompany():
    record = clean_inbound(value_gbp=5000, all_executing_businesses_in_uk=True)
    record["information_on_transfer"]["originator"]["address"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["threshold"]["paragraph_6_must_accompany"] is False
    assert "no_exception_on_these_fields" in result["exception_categories"]


def test_all_uk_request_for_paragraph_6_does_not_invent_a_due_date():
    record = clean_inbound(firm_role="originator", value_gbp=5000, paragraph_6_requested_by_beneficiary=True)
    record["information_on_transfer"]["originator"]["address"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    assert "paragraph_6_request_outstanding" in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert "64C(2)" in _option(result, "hold")["reason"]
    blob = json.dumps(result)
    assert "due_on" not in blob
    assert "three working days" in blob


def test_sunrise_inbound_missing_field_is_not_a_waiver():
    record = clean_inbound(value_gbp=1200, all_executing_businesses_in_uk=False)
    record["counterparty"] = {
        "vasp_name": "Synthetic Quay Exchange",
        "jurisdiction_label": "Synthetic Sunrise Republic",
        "jurisdiction_code": "SYN-SUN",
        "travel_rule_status": "not_in_force",
        "status_recorded_on": "2026-10-01",
        "can_receive_required_information": False,
        "in_united_kingdom": False,
    }
    record["information_on_transfer"]["beneficiary"]["account_number"] = None
    record["unique_transaction_identifier"] = None
    record["information_on_transfer"]["beneficiary"]["unique_transaction_identifier"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert result["sunrise"]["is_sunrise_on_relied_status"] is True
    assert result["sunrise"]["word_used_by_fca_page"] == "a jurisdiction without the Travel Rule"
    assert "sunrise_jurisdiction" in result["exception_categories"]
    assert "missing_information" in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "return")["proposed"] is True
    assert result["flags"]["fca_statement_treated_as_waiver"] is False
    assert any("not treated as a waiver" in line for line in result["explanation"])
    assert any(step["id"] == "request_missing_information_from_counterparty" for step in result["firm_steps_for_a_person"])


def test_sunrise_outbound_must_still_collect_when_counterparty_cannot_receive():
    originator = party()
    beneficiary = party(name="Sam Rivera", account_number="SYNTH-WALLET-BENE-001")
    empty = party(name=None, account_number=None, address=None)
    record = clean_inbound(
        firm_role="originator",
        value_gbp=900,
        all_executing_businesses_in_uk=False,
        information_stored_by_firm=False,
        information_on_transfer={"originator": originator, "beneficiary": beneficiary},
        firm_holds={"originator": empty, "beneficiary": empty},
    )
    record["counterparty"]["travel_rule_status"] = "not_in_force"
    record["counterparty"]["can_receive_required_information"] = False
    record["counterparty"]["in_united_kingdom"] = False
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "return")["proposed"] is False
    assert any(step["id"] == "store_information_before_sending" for step in result["firm_steps_for_a_person"])
    assert result["flags"]["transfer_released_by_agent"] is False


def test_stale_jurisdiction_status_is_not_relied_on():
    record = clean_inbound()
    record["counterparty"]["travel_rule_status"] = "not_in_force"
    record["counterparty"]["status_recorded_on"] = "2026-01-01"
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["sunrise"]["relied_on"] is False
    assert result["sunrise"]["is_sunrise_on_relied_status"] is False
    assert "counterparty_travel_rule_status_not_relied_on" in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "escalate")["proposed"] is True


def test_status_ninety_days_old_is_not_stale_and_ninety_one_is():
    fresh = triage(clean_inbound(), as_of=date(2026, 10, 26), stale_after_days=90)
    assert fresh["sunrise"]["relied_on"] is True
    record = clean_inbound()
    record["counterparty"]["status_recorded_on"] = "2026-07-27"
    on_the_day = triage(record, as_of=date(2026, 10, 25), stale_after_days=90)
    assert on_the_day["sunrise"]["relied_on"] is True
    older = triage(record, as_of=date(2026, 10, 26), stale_after_days=90)
    assert older["sunrise"]["relied_on"] is False


def test_stale_catalogue_is_not_refreshed():
    result = triage(clean_inbound(), as_of=date(2027, 4, 1))
    assert result["rules_current"] is False
    assert result["any_source_stale"] is True
    assert "rules_stale" in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "escalate")["proposed"] is True
    assert result["network_called"] is False


def test_unhosted_unanswered_request_proposes_hold_and_not_return():
    record = clean_inbound(wallet_attribution="unhosted")
    record["unhosted"] = {
        "customer_role": "beneficiary",
        "information_requested_from_customer": True,
        "requested_information_received": False,
    }
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert "unhosted_wallet" in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert "64G(4)" in _option(result, "hold")["reason"]
    assert _option(result, "return")["proposed"] is False
    assert "no return limb" in _option(result, "return")["reason"]


def test_unhosted_without_a_request_does_not_decide_the_may():
    record = clean_inbound(wallet_attribution="unhosted", value_gbp=800)
    record["unhosted"]["customer_role"] = "beneficiary"
    result = triage(record, as_of=date(2026, 10, 26))
    assert _option(result, "hold")["proposed"] is False
    assert any(step["id"] == "analyst_decides_whether_to_request_unhosted_information" for step in result["firm_steps_for_a_person"])
    assert "no_exception_on_these_fields" in result["exception_categories"]


def test_asserted_64a_exclusion_is_not_confirmed_and_not_a_release():
    record = clean_inbound(both_parties_cryptoasset_businesses_own_behalf=True)
    record["information_on_transfer"]["beneficiary"]["name"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert "possible_exclusion_64A" in result["exception_categories"]
    assert "missing_information" not in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "return")["proposed"] is False
    assert _option(result, "escalate")["proposed"] is True
    assert result["flags"]["exclusion_confirmed_by_agent"] is False
    assert result["flags"]["transfer_released_by_agent"] is False


def test_same_business_jmlsg_paragraph_is_not_applied():
    result = triage(clean_inbound(same_cryptoasset_business_both_sides=True), as_of=date(2026, 10, 26))
    assert result["same_business_exclusion_applied"] is False
    assert any("not applied" in line for line in result["explanation"])
    assert "no_exception_on_these_fields" in result["exception_categories"]


def test_intermediary_missing_information_uses_64e_and_not_part_3():
    record = clean_inbound(firm_role="intermediary")
    record["information_on_transfer"]["originator"]["name"] = None
    record["beneficiary_part3_cdd"] = {"name": None, "account_number": None}
    result = triage(record, as_of=date(2026, 10, 26))
    assert "missing_information" in result["exception_categories"]
    assert "correspondence_check_not_possible" not in result["exception_categories"]
    assert "64E(2)(b)(i)" in _option(result, "hold")["reason"]
    assert _option(result, "return")["proposed"] is True
    assert "64E(2)(b)(ii)" in _option(result, "return")["reason"]


def test_suspicion_marker_escalates_and_does_not_file():
    record = clean_inbound()
    record["firm_markers"]["suspicion_already_flagged_by_analyst"] = True
    result = triage(record, as_of=date(2026, 10, 26))
    _assert_inert(result)
    assert "suspicion_marker" in result["exception_categories"]
    assert _option(result, "escalate")["proposed"] is True
    assert _option(result, "hold")["proposed"] is False
    assert result["flags"]["sar_filed"] is False
    assert any(step["id"] == "mlro_considers_sar" for step in result["firm_steps_for_a_person"])
    assert "does not draft" in result["firm_steps_for_a_person"][0]["detail"] or any(
        "does not draft" in step["detail"] for step in result["firm_steps_for_a_person"]
    )


def test_repeated_failure_does_not_report_to_the_fca():
    record = clean_inbound()
    record["firm_markers"]["repeated_information_failure_flagged_by_firm"] = True
    result = triage(record, as_of=date(2026, 10, 26))
    assert _option(result, "escalate")["proposed"] is True
    assert result["flags"]["fca_report_made"] is False
    assert any(step["id"] == "consider_report_of_repeated_failure_to_fca" for step in result["firm_steps_for_a_person"])


def test_live_record_is_refused():
    record = clean_inbound(synthetic=False, notes="Real customer Jane Doe of 10 High Street")
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["label"] == "REFUSED"
    assert result["actions_taken"] == []
    assert result["analyst_decision"] is None
    blob = json.dumps(result)
    assert "Jane Doe" not in blob
    assert "High Street" not in blob


def test_unknown_wallet_is_not_forced_into_either_regime():
    result = triage(clean_inbound(wallet_attribution="unknown"), as_of=date(2026, 10, 26))
    assert "wallet_attribution_unresolved" in result["exception_categories"]
    assert "missing_information" not in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
    assert _option(result, "escalate")["proposed"] is True


def test_batch_assertion_is_not_treated_as_read():
    record = clean_inbound()
    record["batch"] = {
        "is_batch_file": True,
        "beneficiary_wholly_outside_uk": True,
        "batch_accompanied_by_required_information": True,
        "individual_has_originator_account_or_uti": True,
    }
    record["information_on_transfer"]["beneficiary"]["name"] = None
    result = triage(record, as_of=date(2026, 10, 26))
    assert result["batch_file_read"] is False
    assert "batch_file_assertion_not_read" in result["exception_categories"]
    assert "missing_information" not in result["exception_categories"]
    assert _option(result, "hold")["proposed"] is True
