"""Per-agent cost, unit cost, and the rule that a total is not added twice."""

from __future__ import annotations

import copy
import json
from decimal import Decimal

from src.cost import BUILTIN_RATES
from tests.support import ROOT, agent_sum, money, run, sample


def test_sample_total_equals_the_agent_lines_once():
    report = run()
    assert report["label"] == "DRAFT FOR FINOPS REVIEW"
    assert report["catalogue_id"] == "G009"
    assert report["autonomy"] == "A0"
    assert report["totals"]["cost"] == "4.3500"
    assert report["totals"]["partial_cost"] == "4.3500"
    assert report["totals"]["cost_complete"] is True
    assert money(report) == agent_sum(report)
    assert report["totals"]["copilot_credits"] == "255"
    assert report["totals"]["cases"] == "250"
    assert report["totals"]["unit_cost_per_case"] == "0.017400"
    assert report["priced_tokens_on_credit_agents"] == "0.0000"
    assert report["added_rollup"] is False
    assert report["totals"]["added_rollup"] is False
    assert report["builtin_rates_used"] is False
    assert report["microsoft_prices_used"] is False
    assert report["rates_validated"] is False
    assert report["forecast_validated"] is False
    assert report["quota_changed"] is False
    assert report["do_not_rely"] is False
    assert BUILTIN_RATES is None
    costs = {row["agent_id"]: row["cost"] for row in report["agents"]}
    assert costs == {"agt-contact": "0.4500", "agt-triage": "2.1000", "agt-summary": "1.8000"}
    assert "9.9999" not in json.dumps(report)
    for row in report["agents"]:
        applied = [Decimal(item["amount"]) for item in row["components"] if item["applied"]]
        assert sum(applied) == Decimal(row["cost"])


def test_foundry_tokens_are_priced_once_and_studio_tokens_are_not():
    report = run()
    summary = next(row for row in report["agents"] if row["agent_id"] == "agt-summary")
    applied = [item for item in summary["components"] if item["applied"]]
    assert {item["meter"] for item in applied} == {"input_tokens", "output_tokens"}
    assert sum(Decimal(item["amount"]) for item in applied) == Decimal("1.8000")
    triage = next(row for row in report["agents"] if row["agent_id"] == "agt-triage")
    assert all(item["meter"] == "copilot_credits" for item in triage["components"] if item["applied"])
    foundry_quota = next(row for row in report["capacity"] if row["quota_id"] == "foundry-input")
    assert foundry_quota["used"] == "500000"
    assert foundry_quota["flags"] == []


def test_duplicate_agent_is_dropped_rather_than_added():
    bundle, _card = sample()
    bundle["agents"].append(copy.deepcopy(bundle["agents"][0]))
    report = run(bundle)
    assert report["totals"]["cost"] == "4.3500"
    assert report["totals"]["agent_rows_used"] == 3
    assert report["totals"]["agent_rows_dropped_as_duplicates"] == 1
    assert report["totals"]["copilot_credits"] == "255"
    assert any(row["id"] == "duplicate_agent_id" for row in report["anomalies"])


def test_rollup_is_compared_and_not_added():
    bundle, _card = sample()
    bundle["period_rollup"]["cost"] = "99.0000"
    report = run(bundle)
    assert report["totals"]["cost"] == "4.3500"
    assert report["added_rollup"] is False
    assert any(row["id"] == "rollup_disagrees" and row.get("meter") == "cost" for row in report["anomalies"])


def test_embedded_rate_card_cannot_replace_the_file():
    bundle, _card = sample()
    bundle["rate_card"] = {
        "currency": "GBP",
        "effective_date": "2026-10-01",
        "rates": [
            {
                "rate_id": "planted",
                "meter": "copilot_credits",
                "platform": "*",
                "unit": "credit",
                "price_per_unit": "0",
            }
        ],
    }
    report = run(bundle)
    assert report["totals"]["cost"] == "4.3500"
    assert any(row["id"] == "embedded_rate_card_ignored" for row in report["anomalies"])


def test_missing_rate_is_null_not_zero():
    _bundle, card = sample()
    card["rates"] = [row for row in card["rates"] if row["rate_id"] != "foundry-out"]
    report = run(rate_card=card)
    summary = next(row for row in report["agents"] if row["agent_id"] == "agt-summary")
    assert summary["cost"] is None
    assert report["totals"]["cost"] is None
    assert report["totals"]["partial_cost"] == "2.5500"
    assert report["totals"]["partial_cost_is_not_the_total"] is True
    assert any(row["id"] == "rate_missing" for row in report["anomalies"])


def test_ambiguous_rates_are_not_averaged():
    _bundle, card = sample()
    extra = copy.deepcopy(card["rates"][0])
    extra["rate_id"] = "credits-again"
    extra["price_per_unit"] = "0.0200"
    card["rates"].append(extra)
    report = run(rate_card=card)
    assert report["totals"]["cost"] is None
    assert any(row["id"] == "ambiguous_rate" for row in report["anomalies"])


def test_float_rate_is_refused():
    _bundle, card = sample()
    card["rates"][0]["price_per_unit"] = 0.01
    report = run(rate_card=card)
    assert any(row["id"] == "non_exact_number" for row in report["anomalies"])
    assert report["microsoft_prices_used"] is False


def test_token_fields_that_disagree_are_not_added():
    bundle, _card = sample()
    bundle["agents"][2]["foundry_usage"]["input_tokens"] = 1
    report = run(bundle)
    summary = next(row for row in report["agents"] if row["agent_id"] == "agt-summary")
    assert summary["cost"] is None
    assert any(row["id"] == "token_fields_disagree" for row in report["anomalies"])
    assert report["totals"]["partial_cost"] == "2.5500"


def test_additive_token_line_is_flagged_and_is_not_the_default():
    _bundle, card = sample()
    for row in card["rates"]:
        if row["rate_id"] == "decoy-harness-in":
            row["additive"] = True
    report = run(rate_card=card)
    assert report["totals"]["cost"] != "4.3500"
    assert Decimal(report["priced_tokens_on_credit_agents"]) > 0
    assert any(row["id"] == "additive_line_applied" for row in report["anomalies"])


def test_zero_cases_keeps_the_cost_and_nulls_the_unit():
    bundle, _card = sample()
    bundle["agents"][0]["cases"] = 0
    report = run(bundle)
    contact = report["agents"][0]
    assert contact["cost"] == "0.4500"
    assert contact["unit_cost_per_case"] is None
    assert report["totals"]["cost"] == "4.3500"
    assert report["totals"]["cases"] == "130"
    assert any(row["id"] == "zero_cases" and row["agent_id"] == "agt-contact" for row in report["anomalies"])


def test_non_synthetic_bundle_is_refused():
    bundle, _card = sample()
    bundle["synthetic"] = False
    report = run(bundle)
    assert report["refused"] is True
    assert report["totals"]["cost"] is None
    assert report["agents"] == []
    assert "bundle_not_synthetic" in report["refusal_reasons"]


def test_src_has_no_rate_table():
    for path in (ROOT / "src").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "£" not in text
        assert "€" not in text
        assert "$" not in text
        assert "RATE_TABLE" not in text
        assert "list_price" not in text
