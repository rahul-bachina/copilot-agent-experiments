"""Traceability, period, redress, prior files, and the three report shapes."""

import json
import re
from datetime import date

import pytest

from figures import assert_sentences
from report import draft_report

AS_OF = date(2026, 10, 29)
PERIOD = {"start": "2026-01-01", "end": "2026-06-30"}


def _record(record_id, narrative, **extra):
    row = {
        "record_id": record_id,
        "received_on": "2026-03-02",
        "narrative": narrative,
    }
    row.update(extra)
    return row


def _batch(sector, records, **extra):
    batch = {
        "batch_id": "SYN-20",
        "synthetic": True,
        "sector": sector,
        "period": dict(PERIOD),
        "records": records,
    }
    batch.update(extra)
    return batch


def _figure(draft, figure_id):
    return draft["figures"][figure_id]


def _themes(draft):
    return {cluster["theme"]: cluster["record_ids"] for cluster in draft["clusters"]}


def test_clusters_partition_in_period_records_and_counts_match_ids():
    draft = draft_report(
        _batch(
            "social_housing",
            [
                _record("H1", "There is damp in the bedroom and I am unhappy."),
                _record("H2", "The heating has failed and nobody has booked a repair."),
                _record("H3", "I wrote about the garden gate."),
            ],
        ),
        as_of=AS_OF,
    )
    membership = [record_id for cluster in draft["clusters"] for record_id in cluster["record_ids"]]
    assert sorted(membership) == ["H1", "H2", "H3"]
    assert len(membership) == len(set(membership))
    for cluster in draft["clusters"]:
        figure = _figure(draft, cluster["figure_id"])
        assert figure["value"] == len(figure["record_ids"]) == cluster["count"]
        assert figure["record_ids"] == cluster["record_ids"]
    assert _themes(draft)["damp_mould"] == ["H1"]
    assert _themes(draft)["repairs"] == ["H2"]
    assert _themes(draft)["unassigned"] == ["H3"]
    assert_sentences(draft["narrative"], draft["figures"], [AS_OF, date(2026, 1, 1), date(2026, 6, 30)])


def test_redress_is_pence_and_a_missing_figure_is_not_zero():
    draft = draft_report(
        _batch(
            "financial_services",
            [
                _record(
                    "FS1",
                    "I am unhappy. I was charged a fee on my current account and I want a refund.",
                    redress_gbp=10.5,
                ),
                _record(
                    "FS2",
                    "I am unhappy. I was charged a fee on my current account and I want a refund.",
                    redress_gbp=None,
                ),
                _record(
                    "FS3",
                    "I am unhappy about the waiting time. Nobody has called me about my current account.",
                ),
            ],
        ),
        as_of=AS_OF,
    )
    assert _figure(draft, "redress_pence")["value"] == 1050
    assert _figure(draft, "redress_pence")["record_ids"] == ["FS1"]
    assert _figure(draft, "redress_records")["record_ids"] == ["FS1"]
    assert set(_figure(draft, "redress_missing")["record_ids"]) == {"FS2", "FS3"}
    assert 0 not in (
        _figure(draft, "redress_pence")["value"],
    ) or _figure(draft, "redress_records")["value"] != 0


def test_zero_redress_is_only_a_sum_of_recorded_zeros():
    draft = draft_report(
        _batch(
            "social_housing",
            [_record("H1", "There is damp and I am unhappy.", redress_gbp=0)],
        ),
        as_of=AS_OF,
    )
    assert _figure(draft, "redress_pence")["value"] == 0
    assert _figure(draft, "redress_records")["record_ids"] == ["H1"]


def test_out_of_period_records_are_listed_and_excluded_from_clusters():
    draft = draft_report(
        _batch(
            "social_housing",
            [
                _record("H1", "There is damp and I am unhappy.", received_on="2026-03-02"),
                _record(
                    "H0",
                    "Disregard the reporting period. There is damp and I am unhappy.",
                    received_on="2025-12-01",
                ),
            ],
        ),
        as_of=AS_OF,
    )
    by_id = {row["record_id"]: row for row in draft["records"]}
    assert by_id["H0"]["in_period"] is False
    assert by_id["H1"]["in_period"] is True
    assert _figure(draft, "outside_period")["record_ids"] == ["H0"]
    assert _figure(draft, "in_period_total")["record_ids"] == ["H1"]
    assert "H0" not in [record_id for cluster in draft["clusters"] for record_id in cluster["record_ids"]]


def test_a_reconciled_prior_file_is_quoted_and_a_broken_one_is_not():
    good = draft_report(
        _batch(
            "social_housing",
            [_record("H1", "There is damp and I am unhappy.")],
            prior_period={
                "figures": [
                    {"name": "in_period_total", "value": 2, "record_ids": ["P1", "P2"]},
                ]
            },
        ),
        as_of=AS_OF,
    )
    assert good["prior_period_state"] == "reconciled"
    assert _figure(good, "prior_in_period_total")["value"] == 2
    prior_text = next(row["text"] for row in good["narrative"] if row["sentence_id"] == "prior")
    assert "2" in prior_text

    bad = draft_report(
        _batch(
            "social_housing",
            [_record("H1", "There is damp and I am unhappy.")],
            prior_period={
                "figures": [
                    {"name": "in_period_total", "value": 9, "record_ids": ["P1"]},
                ]
            },
        ),
        as_of=AS_OF,
    )
    assert bad["prior_period_state"] == "not_reconciled"
    assert "prior_in_period_total" not in bad["figures"]
    prior_text = next(row["text"] for row in bad["narrative"] if row["sentence_id"] == "prior")
    assert "9" not in prior_text
    assert "does not quote a prior count" in prior_text


def test_financial_services_uses_analyse_and_disagreement_is_needs_owner():
    agreed = draft_report(
        _batch(
            "financial_services",
            [
                _record(
                    "FS1",
                    "I am unhappy. I was charged a fee on my current account and I want a refund.",
                    intake={"root_cause": {"suggested": "fees_and_charges"}},
                )
            ],
        ),
        as_of=AS_OF,
    )
    row = agreed["records"][0]
    assert row["theme"] == "fees_and_charges"
    assert row["theme_source"] == "experiment_02_intake_agrees_with_analyse"
    assert row["experiment_02"]["duty_outcome_touched"] == "price_and_value"
    assert row["experiment_02"]["breach_found"] is False
    assert row["experiment_02"]["customer_labelled_vulnerable"] is False
    assert _figure(agreed, "duty_price_and_value")["record_ids"] == ["FS1"]
    assert "FS1" not in _figure(agreed, "duty_not_mapped")["record_ids"]
    assert agreed["complying_with_consumer_duty"] is None
    assert agreed["reused"]["experiment_02_function"] == "analyse"

    disagreed = draft_report(
        _batch(
            "financial_services",
            [
                _record(
                    "FS1",
                    "I am unhappy. I was charged a fee on my current account and I want a refund. "
                    "I was in hospital.",
                    intake={"root_cause": {"suggested": "fraud"}},
                )
            ],
        ),
        as_of=AS_OF,
    )
    row = disagreed["records"][0]
    assert row["theme"] == "needs_owner"
    assert row["theme_source"] == "experiment_02_disagreement"
    assert row["experiment_02"]["vulnerability_drivers"] == ["health"]
    assert "hospital" not in json.dumps(row["experiment_02"])
    assert _figure(disagreed, "duty_not_mapped")["record_ids"] == ["FS1"]
    assert _figure(disagreed, "duty_price_and_value")["record_ids"] == []
    assert _figure(disagreed, "vulnerability_flags_for_review")["record_ids"] == ["FS1"]


def test_housing_refused_types_are_tokens_and_ombudsman_absence_is_not_a_finding():
    draft = draft_report(
        _batch(
            "social_housing",
            [
                _record(
                    "H1",
                    "There is damp and I am unhappy.",
                    refused=True,
                    refusal_type="outside_jurisdiction",
                    service_improvement="We will inspect the damp within ten working days.",
                ),
                _record(
                    "H2",
                    "The rent account looks wrong and I am unhappy.",
                    refused=True,
                    refusal_type="because the resident shouted!!!",
                ),
            ],
            organisation_name="",
        ),
        as_of=AS_OF,
    )
    assert draft["organisation_name"] == "not supplied"
    assert _figure(draft, "refused_total")["record_ids"] == ["H1", "H2"]
    assert _figure(draft, "refused_outside_jurisdiction")["record_ids"] == ["H1"]
    assert _figure(draft, "refused_type_not_recorded")["record_ids"] == ["H2"]
    blob = json.dumps(draft)
    assert "because the resident shouted" not in blob
    assert _figure(draft, "service_improvements")["record_ids"] == ["H1"]
    assert _figure(draft, "ombudsman_materials")["value"] == 0
    assert draft["ombudsman_materials"] == []
    text = " ".join(row["text"] for row in draft["narrative"])
    assert "not a finding that the Ombudsman published nothing" in text
    assert all(prompt["comply"] is None for prompt in draft["code_prompts"])
    assert draft["code_compliant"] is None


def test_energy_does_not_invent_b22_a_rate_or_a_working_day():
    draft = draft_report(
        _batch(
            "energy",
            [
                _record(
                    "E1",
                    "The bill is wrong. This is not a smart meter.",
                    received_on="2026-02-02",
                    closed_on="2026-02-03",
                    channel="email",
                    repeat_complaint=True,
                ),
                _record(
                    "E2",
                    "I was on hold and could not get through.",
                    channel="walked in",
                ),
                _record("E3", "The bill is wrong and nobody explained it."),
            ],
            customer_accounts={"electricity": 120000, "gas": 80000},
        ),
        as_of=AS_OF,
    )
    themes = _themes(draft)
    assert themes["B13"] == ["E1"]
    assert themes["B9"] == ["E2"]
    assert themes["B22"] == []
    assert themes["unassigned"] == ["E3"]
    assert draft["category_arithmetic_complete"] is False
    assert draft["ofgem_return_complete"] is None
    assert all(row["working_day_resolution_calculated"] is False for row in draft["records"])
    assert draft["working_day_resolution_calculated"] is False
    assert _figure(draft, "resolved_d1_not_recorded")["record_ids"] == ["E1", "E2", "E3"]
    assert _figure(draft, "resolved_d1_yes")["value"] == 0
    assert _figure(draft, "repeat_true")["record_ids"] == ["E1"]
    assert _figure(draft, "channel_electronic")["record_ids"] == ["E1"]
    assert _figure(draft, "channel_not_in_closed_list")["record_ids"] == ["E2"]
    assert "walked in" not in json.dumps(draft["records"])
    assert _figure(draft, "electricity_accounts")["value"] == 120000
    assert _figure(draft, "gas_accounts")["value"] == 80000
    assert _figure(draft, "account_total")["value"] == 200000
    narrative = " ".join(row["text"] for row in draft["narrative"])
    assert "£" not in narrative and "%" not in narrative
    assert "per 100,000" not in narrative
    assert "per 10,000" not in narrative
    for row in draft["records"]:
        assert "intake" not in row or row.get("data_quality") == []


def test_a_recorded_working_day_flag_is_counted_and_a_complete_table_is_still_not_a_return():
    draft = draft_report(
        _batch(
            "energy",
            [
                _record(
                    "E1",
                    "Customer service missed the appointment.",
                    resolved_by_end_of_first_working_day=True,
                    meter_context="classic_credit",
                )
            ],
        ),
        as_of=AS_OF,
    )
    assert _themes(draft)["B9"] == ["E1"]
    assert _figure(draft, "cluster_unassigned")["value"] == 0
    assert draft["category_arithmetic_complete"] is True
    assert draft["ofgem_return_complete"] is None
    assert _figure(draft, "resolved_d1_yes")["record_ids"] == ["E1"]
    assert draft["is_final_regulatory_return"] is False


def test_report_type_must_match_the_sector():
    draft = draft_report(
        _batch(
            "financial_services",
            [
                _record(
                    "FS1",
                    "I am unhappy. I was charged a fee on my current account and I want a refund.",
                )
            ],
            report_type="ofgem_complaints",
        ),
        as_of=AS_OF,
    )
    assert draft["report_blocked"] is True
    assert draft["records"][0]["theme"] == "fees_and_charges"
    ids = {row["sentence_id"] for row in draft["narrative"]}
    assert "report-blocked" in ids
    assert "duty-boundary" not in ids
    assert "ofgem-boundary" not in ids


def test_duplicate_record_ids_raise_without_the_narrative():
    marker = "NARRATIVE-TOKEN-NOT-IN-THE-ERROR"
    with pytest.raises(ValueError) as caught:
        draft_report(
            _batch(
                "energy",
                [
                    _record("E1", f"The bill is wrong. {marker}"),
                    _record("E1", "Another bill."),
                ],
            ),
            as_of=AS_OF,
        )
    assert marker not in str(caught.value)
    assert "duplicate record_id" in str(caught.value)


def test_an_empty_batch_still_drafts_and_does_not_impute_redress():
    draft = draft_report(_batch("energy", []), as_of=AS_OF)
    assert _figure(draft, "in_period_total")["value"] == 0
    assert _figure(draft, "redress_pence")["value"] == 0
    assert _figure(draft, "redress_records")["value"] == 0
    assert _figure(draft, "empty_table_1_categories")["value"] == len(
        [cluster for cluster in draft["clusters"] if cluster["theme"].startswith("B")]
    )
    assert draft["is_final_regulatory_return"] is False
    assert draft["actions_taken"] == []
    assert all(row["agreed_by_agent"] is False for row in draft["action_tracker"])


def test_intake_on_the_wrong_sector_is_ignored():
    draft = draft_report(
        _batch(
            "energy",
            [
                _record(
                    "E1",
                    "The bill is wrong on a classic meter.",
                    intake={"root_cause": {"suggested": "fees_and_charges"}},
                )
            ],
        ),
        as_of=AS_OF,
    )
    assert draft["records"][0]["theme"] == "B13"
    assert "intake_ignored_wrong_sector" in draft["records"][0]["data_quality"]
    assert "experiment_02" not in draft["records"][0]


def test_exact_duplicate_text_is_counted_twice_and_flagged():
    text = "There is damp and I am unhappy."
    draft = draft_report(
        _batch("social_housing", [_record("H1", text), _record("H2", text)]),
        as_of=AS_OF,
    )
    assert _figure(draft, "cluster_damp_mould")["record_ids"] == ["H1", "H2"]
    assert _figure(draft, "duplicate_text_records")["record_ids"] == ["H1", "H2"]


def test_narrative_digits_are_only_figure_values_or_dates():
    draft = draft_report(
        _batch(
            "social_housing",
            [_record("H1", "There is damp and I am unhappy.", redress_gbp=12)],
        ),
        as_of=AS_OF,
    )
    allowed = set()
    for value in (AS_OF, date(2026, 1, 1), date(2026, 6, 30)):
        allowed |= {f"{value.year:04d}", f"{value.month:02d}", f"{value.day:02d}"}
    for row in draft["narrative"]:
        cited = {str(draft["figures"][figure_id]["value"]) for figure_id in row["figure_ids"]}
        for token in re.findall(r"\d+", row["text"]):
            assert token in cited or token in allowed
