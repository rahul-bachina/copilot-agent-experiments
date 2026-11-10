"""A stale rule is not stated as current cover. Equal to 180 days is current."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from explainer import STALE_AFTER_DAYS, explain
from samples import request


AS_OF = "2026-11-10"
AS_OF_DATE = date.fromisoformat(AS_OF)


def _shift_dates(body: dict, on: str) -> dict:
    body["contract"]["reviewed_on"] = on
    body["rules_table"]["approved_on"] = on
    for rule in body["rules_table"]["rules"]:
        rule["approved_on"] = on
        rule["review_due_on"] = "2027-03-01"
        rule["effective_on"] = "2026-04-01"
    return body


def test_one_hundred_and_eighty_days_is_current():
    on = (AS_OF_DATE - timedelta(days=STALE_AFTER_DAYS)).isoformat()
    document = explain(_shift_dates(request(), on), AS_OF)
    assert document["outcome"] == "explained"
    assert document["coverage_stated"] is True


def test_one_hundred_and_eighty_one_days_is_stale():
    on = (AS_OF_DATE - timedelta(days=STALE_AFTER_DAYS + 1)).isoformat()
    document = explain(_shift_dates(request(), on), AS_OF)
    assert document["outcome"] == "route_to_human"
    assert document["coverage_stated"] is False
    assert document["uncertainty"]["reasons"][0] == "table_stale"
    assert "The approved table says" not in document["explanation"]["text"]


def test_review_due_on_the_as_of_date_is_current():
    body = request()
    for rule in body["rules_table"]["rules"]:
        rule["review_due_on"] = AS_OF
    document = explain(body, AS_OF)
    assert document["outcome"] == "explained"


def test_review_due_the_day_before_routes():
    body = request()
    for rule in body["rules_table"]["rules"]:
        rule["review_due_on"] = (AS_OF_DATE - timedelta(days=1)).isoformat()
    document = explain(body, AS_OF)
    assert document["outcome"] == "route_to_human"
    assert document["uncertainty"]["reasons"][0] == "rule_overdue"
    assert document["coverage_stated"] is False


def test_rule_not_yet_in_force_routes():
    body = request()
    for rule in body["rules_table"]["rules"]:
        rule["effective_on"] = (AS_OF_DATE + timedelta(days=1)).isoformat()
    document = explain(body, AS_OF)
    assert document["uncertainty"]["reasons"][0] == "rule_not_in_force"
    assert document["coverage_stated"] is False


def test_stale_pinned_source_does_not_invent_a_refusal():
    body = request()
    body["contract"]["reviewed_on"] = "2027-10-01"
    body["rules_table"]["approved_on"] = "2027-10-01"
    for rule in body["rules_table"]["rules"]:
        rule["approved_on"] = "2027-10-01"
        rule["review_due_on"] = "2028-01-01"
    document = explain(body, "2027-11-10")
    assert document["outcome"] == "explained"
    assert document["coverage_stated"] is True
    assert document["uncertainty"]["level"] == "medium"
    assert "sources_stale" in document["uncertainty"]["reasons"]
    assert document["flags"]["entitlement_refused"] is False
    assert document["regulatory"]["sources"]["any_relevant_source_stale"] is True
