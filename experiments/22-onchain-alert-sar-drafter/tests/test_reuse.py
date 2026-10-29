"""Experiments 04, 08, 10, and 16 are called. Their decisions are not copied."""

import json
from datetime import date
from pathlib import Path

from tests.support import load_example

from src.investigate import investigate

ROOT = Path(__file__).resolve().parents[2]


def _with_neighbours():
    case = load_example()
    case["travel_rule_transfer"] = json.loads(
        (ROOT / "10-travel-rule-exception-triage" / "examples" / "sample_transfer.json").read_text()
    )
    case["kyc_file"] = json.loads(
        (ROOT / "16-kyc-evidence-intake" / "examples" / "sample_customer_file.json").read_text()
    )
    return case


def test_travel_rule_categories_are_kept_and_names_are_not():
    draft = investigate(_with_neighbours(), as_of=date(2026, 10, 29))
    travel = draft["travel_rule"]
    assert travel["called"] is True
    assert travel["refused"] is False
    assert travel["analyst_decision"] is None
    assert "non_corresponding_information" in travel["exception_categories"]
    assert travel["injection_followed"] is False
    blob = json.dumps(draft)
    assert "Sam Rivera" not in blob
    assert "Sam R" not in blob


def test_kyc_review_does_not_confirm_or_copy_the_customer_note():
    draft = investigate(_with_neighbours(), as_of=date(2026, 10, 29))
    kyc = draft["kyc"]
    assert kyc["called"] is True
    assert kyc["documents_confirmed"] is False
    assert kyc["purpose_confirmed"] is False
    assert kyc["final_risk_rating"] is None
    assert kyc["sar_filed"] is False
    assert kyc["customer_facing_copied"] is False
    assert kyc["injection_followed"] is False


def test_identifier_gateway_does_not_claim_anonymisation():
    draft = investigate(load_example(), as_of=date(2026, 10, 29))
    gateway = draft["identifier_gateway"]
    assert gateway["called"] is True
    assert gateway["output_is_anonymised"] is False
    assert gateway["agent_may_release"] is False
    assert "nino" in gateway["entity_types"]
    assert "QQ 12 34 56 A" not in json.dumps(draft)
    assert "ZZ99 9ZZ" not in json.dumps(draft)


def test_experiment_04_pin_is_cited_and_the_gap_register_does_not_run():
    draft = investigate(load_example(), as_of=date(2026, 10, 29))
    pin = draft["experiment_04"]
    assert pin["called"] is True
    assert pin["gap_register_run"] is False
    assert pin["registration_page_last_verified_by_experiment_04"] == "2026-10-24"
    assert draft["fca_monitoring_expectation"]["tool_configured_by_this_agent"] is False
