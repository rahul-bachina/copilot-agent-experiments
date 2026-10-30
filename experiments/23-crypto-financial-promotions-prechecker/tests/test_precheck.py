"""The sample draft is a checklist. It is not an approval."""

import json

from tests.support import by_id, draft_sample

from src.sources import RISK_WARNING_CRYPTO


def test_sample_is_a_draft_and_not_an_approval():
    draft = draft_sample()
    assert draft["label"] == "DRAFT CHECKLIST FOR THE S21 APPROVER"
    assert draft["catalogue_id"] == "UK08"
    assert draft["autonomy"] == "A0"
    assert draft["promotion_approved"] is False
    assert draft["published"] is False
    assert draft["compliance_opinion"] is False
    assert draft["s21_approver_decision"] is None
    assert draft["rewrite_drafted"] is False
    assert draft["actions_taken"] == []
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["sources_pinned_on"] == "2026-10-30"
    assert draft["sources_stale"] is False
    assert draft["rules_current"] is True
    rows = by_id(draft)
    assert rows["FP-ROUTE"]["status"] == "phrase_not_found"
    assert rows["FP-RISK"]["status"] == "phrase_not_found"
    assert rows["FP-INCENTIVE"]["status"] == "flagged_for_review"
    assert rows["FP-FAIR"]["status"] == "flagged_for_review"
    assert rows["FP-DOFP"]["status"] == "question_for_approver"
    assert rows["FP-OFFENCE"]["status"] == "recorded_not_applied"
    assert rows["FP-GATEWAY"]["status"] == "recorded_not_applied"
    for row in draft["checklist"]:
        assert row["compliance_finding"] is False
    blob = json.dumps(draft)
    assert "QQ 12 34 56 A" not in blob
    assert draft["identifier_gateway"]["called"] is True
    assert draft["identifier_gateway"]["output_is_anonymised"] is False
    assert draft["identifier_gateway"]["agent_may_release"] is False
    assert draft["identifier_gateway"]["finding_count"] >= 1
    assert "nino" in draft["identifier_gateway"]["finding_types"]


def test_prescribed_warning_does_not_flag_the_word_protected():
    promotion = {
        "synthetic": True,
        "promotion_id": "SYNTH-PROMO-CLEAN",
        "firm": "Harbourline Markets Ltd",
        "channel": "web",
        "character_limited": False,
        "caller_marks_direct_offer": True,
        "caller_claims_qualifying_cryptoasset": True,
        "communicator": {"name": "Harbourline Markets Ltd", "route_claimed": "mlr_registered"},
        "s21_approver": {"name": None},
        "text": (
            "The route is article 73ZA. Harbourline is an MLR-registered firm.\n"
            + RISK_WARNING_CRYPTO
            + "\nTake 2 mins to learn more.\n"
            "There is a 24-hour cooling-off period.\n"
            "Alex Example, this is a high-risk investment. How would you feel if you lost the money you're about to invest? Take 2 mins to learn more.\n"
            "The journey asks whether the person is a restricted investor.\n"
            "An appropriateness assessment is described.\n"
        ),
    }
    from datetime import date

    from src.precheck import precheck

    draft = precheck(promotion, as_of=date(2026, 10, 30))
    rows = by_id(draft)
    assert rows["FP-RISK"]["status"] == "phrase_present"
    assert rows["FP-RISK-LINK"]["status"] == "phrase_present"
    assert rows["FP-FAIR"]["status"] == "phrase_not_found"
    assert rows["FP-INCENTIVE"]["status"] == "phrase_not_found"
    assert rows["FP-DOFP"]["status"] == "phrase_present"
    assert rows["FP-ROUTE"]["status"] == "phrase_present"
    assert rows["FP-S21-NAME"]["status"] == "not_applied"
    assert draft["promotion_approved"] is False
    assert draft["compliance_opinion"] is False


def test_s21_route_without_a_name_is_not_sign_off():
    from datetime import date

    from src.precheck import precheck

    promotion = {
        "synthetic": True,
        "channel": "social",
        "caller_claims_qualifying_cryptoasset": True,
        "communicator": {"route_claimed": "s21_approval"},
        "s21_approver": {"name": "  "},
        "text": "This promotion is approved by an authorised person under section 21.\n" + RISK_WARNING_CRYPTO,
    }
    draft = precheck(promotion, as_of=date(2026, 10, 30))
    rows = by_id(draft)
    assert rows["FP-S21-NAME"]["status"] == "phrase_not_found"
    assert draft["s21_approver_decision"] is None


def test_short_warning_without_a_stated_limit_is_flagged():
    from datetime import date

    from src.precheck import precheck
    from src.sources import RISK_WARNING_CRYPTO_SHORT

    promotion = {
        "synthetic": True,
        "channel": "social",
        "character_limited": False,
        "caller_claims_qualifying_cryptoasset": True,
        "text": RISK_WARNING_CRYPTO_SHORT,
    }
    draft = precheck(promotion, as_of=date(2026, 10, 30))
    assert by_id(draft)["FP-RISK"]["status"] == "flagged_for_review"


def test_short_warning_with_a_stated_limit_is_a_question():
    from datetime import date

    from src.precheck import precheck
    from src.sources import RISK_WARNING_CRYPTO_SHORT

    promotion = {
        "synthetic": True,
        "channel": "social",
        "character_limited": True,
        "caller_claims_qualifying_cryptoasset": True,
        "text": RISK_WARNING_CRYPTO_SHORT + " Take 2 mins to learn more.",
    }
    draft = precheck(promotion, as_of=date(2026, 10, 30))
    assert by_id(draft)["FP-RISK"]["status"] == "question_for_approver"


def test_nrr_wording_is_not_treated_as_the_crypto_warning():
    from datetime import date

    from src.precheck import precheck
    from src.sources import RISK_WARNING_NRR

    promotion = {
        "synthetic": True,
        "channel": "app",
        "caller_claims_qualifying_cryptoasset": True,
        "text": RISK_WARNING_NRR,
    }
    draft = precheck(promotion, as_of=date(2026, 10, 30))
    assert by_id(draft)["FP-RISK"]["status"] == "flagged_for_review"
    assert "4.12A.11R(1)(a)" in by_id(draft)["FP-RISK"]["detail"]


def test_unclaimed_cryptoasset_does_not_score_the_warning():
    from datetime import date

    from src.precheck import precheck

    promotion = {
        "synthetic": True,
        "channel": "web",
        "caller_claims_qualifying_cryptoasset": False,
        "text": "A token for a closed test.",
    }
    draft = precheck(promotion, as_of=date(2026, 10, 30))
    assert by_id(draft)["FP-RISK"]["status"] == "not_applied"
    assert by_id(draft)["FP-26F"]["status"] == "recorded_not_applied"
