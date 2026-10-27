"""Approving, rating, onboarding, filing, and sending are not implemented."""

from __future__ import annotations

import pytest

from src.review import (
    ReviewForbidden,
    approve_customer,
    assign_risk_rating,
    file_sar,
    onboard_customer,
    record_reviewer_confirmation,
    reject_customer,
    review,
    send_to_customer,
)
from tests.support import AS_OF, PASSPORT, customer_file, file_row


def _confirmed():
    draft = review(
        customer_file([file_row("ID-014", PASSPORT, filename="passport.txt")]),
        as_of=AS_OF,
    )
    return record_reviewer_confirmation(
        draft,
        role="KYC reviewer",
        file_ids=["ID-014"],
        purpose="kyc_evidence",
    )


@pytest.mark.parametrize(
    "function",
    [approve_customer, reject_customer, onboard_customer, file_sar, send_to_customer],
)
def test_forbid_functions_raise_before_and_after_confirmation(function):
    draft = review(
        customer_file([file_row("ID-014", PASSPORT, filename="passport.txt")]),
        as_of=AS_OF,
    )
    with pytest.raises(ReviewForbidden):
        function(draft)
    confirmed = _confirmed()
    with pytest.raises(ReviewForbidden):
        function(confirmed)
    assert confirmed["flags"]["customer_approved"] is False
    assert confirmed["flags"]["customer_rejected"] is False
    assert confirmed["flags"]["customer_onboarded"] is False
    assert confirmed["flags"]["sar_filed"] is False
    assert confirmed["flags"]["external_sent"] is False
    assert confirmed["flags"]["final_risk_rating_assigned"] is False


def test_assign_risk_rating_raises_for_every_label():
    draft = _confirmed()
    for rating in ("low", "medium", "high", None):
        with pytest.raises(ReviewForbidden):
            assign_risk_rating(draft, rating)
    assert draft["final_risk_rating"] is None


def test_experiment_12_still_refuses_the_underlying_matter():
    intake_src_imported = review(
        customer_file([file_row("ID-014", PASSPORT, filename="passport.txt")]),
        as_of=AS_OF,
    )
    from src.review import _load_intake

    intake_module = _load_intake()
    draft = intake_src_imported["document_intake"]
    with pytest.raises(intake_module.IntakeForbidden):
        intake_module.approve_underlying_matter(draft)
    with pytest.raises(intake_module.IntakeForbidden):
        intake_module.reject_underlying_matter(draft)
    with pytest.raises(intake_module.IntakeForbidden):
        intake_module.commit_to_queue(draft)
    with pytest.raises(intake_module.IntakeForbidden):
        intake_module.send_external(draft)
