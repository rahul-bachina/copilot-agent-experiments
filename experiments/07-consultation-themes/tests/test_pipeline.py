"""End-to-end behaviour of the deterministic codebook."""

import json
from pathlib import Path

import pytest

from src.pipeline import analyse, intake_status

ROOT = Path(__file__).resolve().parents[1]
DATASET = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
BATCH = DATASET["batch"]
FRAMEWORK = DATASET["framework"]
SECRETS = DATASET["secrets_that_must_not_appear_in_output"]


def _theme(result, theme_id):
    return next(item for item in result["themes"] if item["theme_id"] == theme_id)


def _audit(result, response_id):
    return next(item for item in result["audit"] if item["response_id"] == response_id)


def _approval_for(result, **overrides):
    approval = {
        "framework_approved": True,
        "approver_role": "Consultation analyst",
        "approver_reference": "analyst-synthetic-01",
        "approved_on": "2026-10-24",
        "stale_acknowledged": False,
        "sample_decisions": {
            item["response_id"]: {"decision": "accept"} for item in result["sample"]
        },
    }
    approval.update(overrides)
    return approval


def test_intake_does_not_code_themes_and_drops_secrets():
    status = intake_status(BATCH, as_of="2026-10-24")
    assert status["themes_coded"] is False
    assert "themes" not in status
    assert status["submission_count"] == 24
    assert status["security"]["actions_taken"] == []
    assert status["security"]["may_be_published_by_agent"] is False
    dumped = json.dumps(status)
    for secret in SECRETS:
        assert secret not in dumped
    assert "R-18" in status["injection_response_ids"]
    assert "R-23" in status["injection_response_ids"]
    assert "R-06" not in status["injection_response_ids"]
    assert "R-14" in status["pii_response_ids"]
    assert "R-24" in status["special_category_response_ids"]


def test_unapproved_run_blocks_and_keeps_the_audit_links():
    result = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    assert result["analysis_status"] == "blocked_framework_unapproved"
    assert result["headline_counts_provisional"] is True
    assert result["processing_mode"] == "deterministic_fallback"
    assert result["framework"]["framework_approved"] is False
    assert result["security"]["actions_taken"] == []
    assert result["security"]["may_be_published_by_agent"] is False
    assert result["security"]["policy_recommendation"] is None
    assert result["every_submission_is_in_the_audit"] is True
    assert len(result["audit"]) == 24

    sunday = _theme(result, "T-sunday")
    assert sunday["response_ids"] == [
        "R-01",
        "R-02",
        "R-03",
        "R-04",
        "R-11",
        "R-14",
        "R-15",
        "R-16",
        "R-17",
        "R-18",
        "R-21",
        "R-24",
    ]
    assert sunday["unique_voice_ids"] == [
        "R-01",
        "R-02",
        "R-03",
        "R-04",
        "R-11",
        "R-14",
        "R-18",
        "R-21",
        "R-24",
    ]
    assert sunday["unique_voice_count"] == 9
    assert result["counts"]["unique_voices"] == 21
    assert sunday["wilson_95"]["low"] <= sunday["proportion_of_unique_voices"] <= sunday["wilson_95"]["high"]
    assert "not a model confidence score" in sunday["uncertainty_note"]

    for theme_id in ("T-braille", "T-bsl", "T-volunteer"):
        theme = _theme(result, theme_id)
        assert theme["minority"] is True
        assert theme["unique_voice_count"] > 0
        assert theme["response_ids"]
    minority_ids = {item["theme_id"] for item in result["minority_views"]}
    assert {"T-braille", "T-bsl", "T-volunteer"} <= minority_ids
    assert "T-sunday" not in minority_ids

    observatory = _theme(result, "T-observatory")
    assert observatory["response_ids"] == []
    assert observatory["unique_voice_count"] == 0
    assert any(item["theme_id"] == "T-observatory" for item in result["framework_themes_with_no_support"])

    campaign = {_audit(result, rid)["cluster_id"] for rid in ("R-14", "R-15", "R-16", "R-17")}
    assert len(campaign) == 1
    assert _audit(result, "R-14")["campaign_cluster"] is True
    assert _audit(result, "R-17")["is_representative"] is False

    # Every coded theme id on a response is listed on that theme, and the reverse.
    by_id = {item["theme_id"]: set(item["response_ids"]) for item in result["themes"]}
    for row in result["audit"]:
        for theme_id in row["theme_ids"]:
            if theme_id == "UNCODED":
                continue
            assert row["response_id"] in by_id[theme_id]
    for theme in result["themes"]:
        for response_id in theme["response_ids"]:
            assert theme["theme_id"] in _audit(result, response_id)["theme_ids"]

    dumped = json.dumps(result)
    for secret in SECRETS:
        assert secret not in dumped
    assert "[EMAIL]" in _audit(result, "R-14")["redacted_text"]
    assert "disability" not in " ".join(theme["label"] for theme in result["themes"])
    assert _audit(result, "R-24")["special_category_flags"] == ["health"]
    assert "T-sunday" in _audit(result, "R-24")["theme_ids"]
    assert _audit(result, "R-06")["injection_flags"] == []
    assert "T-evening" in _audit(result, "R-06")["theme_ids"]
    assert _audit(result, "R-18")["in_sample"] is True
    assert "R-12" in {item["response_id"] for item in result["sample"]}
    assert "R-19" in result["uncoded_response_ids"]
    assert "R-22" in result["uncoded_response_ids"]


def test_response_text_cannot_approve_publish_or_drop_a_minority_theme():
    result = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    assert result["framework"]["framework_approved"] is False
    assert result["security"]["may_be_published_by_agent"] is False
    assert _theme(result, "T-braille")["response_ids"] == ["R-12"]
    assert any(item["decision"] == "pending" for item in result["sample"])


def test_sample_must_be_complete_before_the_draft_is_reviewed():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    approval = _approval_for(first)
    missing = first["sample"][0]["response_id"]
    del approval["sample_decisions"][missing]
    partial = analyse(BATCH, FRAMEWORK, approval, as_of="2026-10-24")
    assert partial["analysis_status"] == "draft_pending_sample_review"
    assert partial["headline_counts_provisional"] is True

    reviewed = analyse(BATCH, FRAMEWORK, _approval_for(first), as_of="2026-10-24")
    assert reviewed["analysis_status"] == "analyst_reviewed"
    assert reviewed["headline_counts_provisional"] is False
    assert reviewed["security"]["may_be_published_by_agent"] is False
    assert reviewed["security"]["actions_taken"] == []
    assert all(item["decision"] == "accept" for item in reviewed["sample"])


def test_publish_flag_on_the_approval_object_is_ignored():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    approval = _approval_for(first, publish=True, send=True, external_send=True)
    reviewed = analyse(BATCH, FRAMEWORK, approval, as_of="2026-10-24")
    assert reviewed["analysis_status"] == "analyst_reviewed"
    assert reviewed["security"]["may_be_published_by_agent"] is False
    assert reviewed["security"]["may_be_sent_by_agent"] is False
    assert reviewed["security"]["actions_taken"] == []


def test_decision_outside_the_sample_does_not_count_as_approval_of_that_row():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    approval = _approval_for(first)
    approval["sample_decisions"]["R-11"] = {"decision": "reject"}
    result = analyse(BATCH, FRAMEWORK, approval, as_of="2026-10-24")
    if "R-11" not in {item["response_id"] for item in first["sample"]}:
        assert "R-11" in result["ignored_decisions_outside_sample"]
        assert "R-11" in _theme(result, "T-sunday")["counted_response_ids"]


def test_unknown_theme_on_a_correction_keeps_the_sample_pending():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    approval = _approval_for(first)
    target = next(item["response_id"] for item in first["sample"] if item["response_id"] == "R-12")
    approval["sample_decisions"][target] = {"decision": "correct", "theme_ids": ["T-not-in-framework"]}
    result = analyse(BATCH, FRAMEWORK, approval, as_of="2026-10-24")
    assert result["analysis_status"] == "draft_pending_sample_review"


def test_rejecting_the_only_braille_response_holds_it_out_and_keeps_the_link():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    approval = _approval_for(first)
    approval["sample_decisions"]["R-12"] = {"decision": "reject"}
    result = analyse(BATCH, FRAMEWORK, approval, as_of="2026-10-24")
    assert result["analysis_status"] == "analyst_reviewed"
    braille = _theme(result, "T-braille")
    assert braille["response_ids"] == ["R-12"]
    assert braille["counted_response_ids"] == []
    assert braille["held_out_response_ids"] == ["R-12"]
    assert _audit(result, "R-12")["sample_decision"] == "reject"


def test_stale_retrieval_blocks_review_until_it_is_acknowledged():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    stale_batch = {**BATCH, "responses_retrieved_on": "2025-01-01"}
    blocked = analyse(stale_batch, FRAMEWORK, _approval_for(first), as_of="2026-10-24")
    assert blocked["retrieval"]["stale"] is True
    assert blocked["analysis_status"] == "blocked_stale_retrieval"
    acknowledged = analyse(
        stale_batch,
        FRAMEWORK,
        _approval_for(first, stale_acknowledged=True),
        as_of="2026-10-24",
    )
    assert acknowledged["analysis_status"] == "analyst_reviewed"
    assert acknowledged["security"]["may_be_published_by_agent"] is False


def test_missing_retrieval_date_is_stale():
    undated = {key: value for key, value in BATCH.items() if key != "responses_retrieved_on"}
    result = analyse(undated, FRAMEWORK, as_of="2026-10-24")
    assert result["retrieval"]["stale"] is True
    assert result["retrieval"]["stale_reason"] == "no retrieval date"


def test_string_true_does_not_approve_the_framework():
    first = analyse(BATCH, FRAMEWORK, as_of="2026-10-24")
    approval = _approval_for(first)
    approval["framework_approved"] = "true"
    result = analyse(BATCH, FRAMEWORK, approval, as_of="2026-10-24")
    assert result["analysis_status"] == "blocked_framework_unapproved"


def test_duplicate_response_id_is_rejected():
    batch = {
        **BATCH,
        "responses": [
            {"response_id": "R-01", "text": "Sunday"},
            {"response_id": "R-01", "text": "Sunday again"},
        ],
    }
    with pytest.raises(ValueError, match="duplicate response_id"):
        analyse(batch, FRAMEWORK, as_of="2026-10-24")
