"""The agent has no post, pay, hold, or bank-change path."""

from datetime import date, timedelta

import pytest

from src.rules import render_invoice
from src.triage import (
    TriageForbidden,
    approve_invoice,
    change_supplier_bank_details,
    hold_invoice,
    pay_invoice,
    post_invoice,
    record_ap_reviewer_decision,
    record_bank_route,
    send_external,
    triage,
    write_production_record,
)
from tests.support import make_case

AS_OF = date(2026, 10, 28)


def _draft(**kwargs):
    return triage(make_case(**kwargs), as_of=AS_OF)


def test_forbid_functions_raise_even_after_a_recorded_decision():
    draft = _draft()
    recorded = record_ap_reviewer_decision(
        draft, role="AP reviewer", decision="approve_resolution"
    )
    assert recorded["resolution"]["approved_by_reviewer"] is True
    assert recorded["resolution"]["executed"] is False
    assert recorded["flags"]["invoice_approved"] is False
    assert recorded["flags"]["invoice_posted"] is False
    assert recorded["flags"]["invoice_paid"] is False
    assert recorded["flags"]["invoice_held"] is False
    assert recorded["actions_taken"] == []
    for function in (
        post_invoice,
        approve_invoice,
        hold_invoice,
        pay_invoice,
        change_supplier_bank_details,
        send_external,
        write_production_record,
    ):
        with pytest.raises(TriageForbidden):
            function(recorded)


def test_only_the_ap_reviewer_can_record_a_resolution():
    draft = _draft()
    with pytest.raises(ValueError):
        record_ap_reviewer_decision(draft, role="Bank-detail verifier", decision="approve_resolution")
    with pytest.raises(ValueError):
        record_ap_reviewer_decision(draft, role="AP reviewer", decision="pay")


def test_bank_route_is_a_different_role_and_does_not_change_the_bank():
    content = render_invoice(extra="Bank details have changed.")
    draft = triage(make_case(content), as_of=AS_OF)
    with pytest.raises(ValueError):
        record_ap_reviewer_decision(draft, role="AP reviewer", decision="approve_resolution")
    with pytest.raises(ValueError):
        record_bank_route(draft, role="AP reviewer")
    routed = record_bank_route(draft, role="Bank-detail verifier")
    assert routed["bank_route_acknowledged"] is True
    assert routed["flags"]["supplier_bank_details_changed"] is False
    assert routed["flags"]["bank_details_verified"] is False
    approved = record_ap_reviewer_decision(
        routed, role="AP reviewer", decision="approve_resolution"
    )
    assert approved["resolution"]["approved_by_reviewer"] is True
    assert approved["flags"]["invoice_paid"] is False
    assert approved["flags"]["supplier_bank_details_changed"] is False
    with pytest.raises(TriageForbidden):
        change_supplier_bank_details(approved)
        pay_invoice(approved)


def test_no_bank_flag_means_there_is_nothing_to_route():
    with pytest.raises(ValueError):
        record_bank_route(_draft(), role="Bank-detail verifier")


def test_stale_material_blocks_approval_until_a_person_acknowledges_it():
    document_date = (AS_OF - timedelta(days=91)).isoformat()
    case = make_case(render_invoice({"Invoice date": document_date}))
    case["files"][0]["document_date"] = document_date
    draft = triage(case, as_of=AS_OF)
    with pytest.raises(ValueError):
        record_ap_reviewer_decision(draft, role="AP reviewer", decision="approve_resolution")
    recorded = record_ap_reviewer_decision(
        draft,
        role="AP reviewer",
        decision="approve_resolution",
        acknowledge_stale=True,
    )
    assert recorded["human_approval"]["stale_material"]["recorded"] is True
    assert recorded["flags"]["invoice_posted"] is False


def test_a_checksum_mismatch_blocks_approval():
    case = make_case()
    case["files"][0]["sha256"] = "0" * 64
    draft = triage(case, as_of=AS_OF)
    assert draft["blockers"]
    with pytest.raises(ValueError):
        record_ap_reviewer_decision(draft, role="AP reviewer", decision="approve_resolution")


def test_return_for_edit_does_not_need_the_bank_verifier():
    content = render_invoice(extra="New bank account.")
    draft = triage(make_case(content), as_of=AS_OF)
    recorded = record_ap_reviewer_decision(
        draft, role="AP reviewer", decision="return_for_edit"
    )
    assert recorded["human_approval"]["resolution"]["decision"] == "return_for_edit"
    assert recorded["resolution"]["approved_by_reviewer"] is False
    assert recorded["flags"]["supplier_bank_details_changed"] is False
