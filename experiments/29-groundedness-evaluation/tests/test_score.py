"""Claim verdicts on the synthetic passages."""

from src.report import report
from tests.support import safety, sample_report


def test_sample_supports_three_claims_and_does_not_release():
    draft = sample_report()
    safety(draft)
    assert draft["summary"]["claim_count"] == 3
    assert draft["summary"]["verdicts"]["supported"] == 3
    assert draft["summary"]["stale_claim_count"] == 0
    assert draft["draft_bar_met"] is True
    assert draft["release_decision"] is None
    assert draft["foundry_option"]["preview_option_is_preview"] is True
    assert draft["foundry_option"]["foundry_score"] is None
    assert draft["foundry_option"]["documented_default_pass_threshold_on_1_to_5_scale"] == 3
    assert draft["draft_thresholds"]["min_supported_rate"] == 1.0
    assert draft["draft_thresholds"]["stale_after_days"] == 180


def test_a_changed_number_is_one_verdict():
    bundle = _one(
        "Emergency repairs are attended within 48 hours.",
        "Emergency repairs are attended within 24 hours.",
    )
    draft = report(bundle, "2026-11-03")
    safety(draft)
    assert draft["summary"]["verdicts"]["number_mismatch"] == 1
    assert draft["claims"][0]["other_failures"] == []
    assert draft["draft_bar_met"] is False


def test_a_changed_date_is_not_also_counted_as_unsupported():
    bundle = _one(
        "The leaflet was issued on 1 April 2026.",
        "The leaflet was issued on 1 September 2026.",
    )
    draft = report(bundle, "2026-11-03")
    assert draft["claims"][0]["verdict"] == "date_mismatch"
    assert draft["claims"][0]["other_failures"] == ["unsupported"]
    assert draft["summary"]["verdict_total"] == 1
    assert draft["summary"]["verdicts"]["unsupported"] == 0


def test_two_sentences_are_two_claims_and_one_answer():
    bundle = _one(
        "Emergency repairs are attended within 24 hours. Routine repairs are attended within 48 working days.",
        "Emergency repairs are attended within 24 hours.",
    )
    draft = report(bundle, "2026-11-03")
    summary = draft["summary"]
    assert summary["answer_count"] == 1
    assert summary["claim_count"] == 2
    assert summary["verdicts"]["supported"] == 1
    assert summary["verdicts"]["number_mismatch"] == 1
    assert summary["verdict_total"] == 2


def _one(text: str, quote: str) -> dict:
    return {
        "bundle_id": "syn-unit",
        "organisation": "Northfen Borough Council",
        "sector": "uk-public-sector",
        "synthetic": True,
        "agent_under_test": "synthetic-housing-repairs-qa",
        "passages": [
            {
                "source_id": "leaflet-repairs",
                "title": "Northfen housing repairs leaflet (synthetic)",
                "reviewed_on": "2026-09-01",
                "text": (
                    "Emergency repairs are attended within 24 hours. "
                    "Routine repairs are attended within 20 working days. "
                    "The leaflet was issued on 1 September 2026."
                ),
            }
        ],
        "answers": [
            {
                "answer_id": "a1",
                "question": "What does the leaflet say?",
                "text": text,
                "citations": [{"source_id": "leaflet-repairs", "quote": quote}],
            }
        ],
    }
