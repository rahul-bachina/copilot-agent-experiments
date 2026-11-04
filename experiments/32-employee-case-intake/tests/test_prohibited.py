"""The agent cannot confirm, contact, or write, including after a human record."""

from datetime import date

import pytest

from src.draft import (
    CONFIRM,
    CaseForbidden,
    contact_employee,
    contact_manager,
    draft_case,
    record_hr_confirmation,
    write_hr_system,
)

AS_OF = date(2026, 11, 4)


def _draft():
    return draft_case(
        {
            "synthetic": True,
            "case_id": "SYN-HR-PRO",
            "narrative": "I want to raise a grievance about the rota. Synthetic.",
            "jurisdiction": "england",
        },
        as_of=AS_OF,
    )


def test_confirmation_does_not_enable_a_write_or_a_contact():
    confirmed = record_hr_confirmation(
        _draft(),
        role="HR officer",
        decision=CONFIRM,
        confirmed_category="grievance",
        confirmed_route="hr_grievance_officer",
    )
    with pytest.raises(CaseForbidden):
        write_hr_system(confirmed)
    with pytest.raises(CaseForbidden):
        contact_employee(confirmed)
    with pytest.raises(CaseForbidden):
        contact_manager(confirmed)
    assert confirmed["external_sent"] is False
    assert confirmed["outcome"] is None


def test_unknown_route_is_rejected():
    with pytest.raises(ValueError):
        record_hr_confirmation(
            _draft(),
            role="HR officer",
            decision=CONFIRM,
            confirmed_route="line_manager",
        )


def test_return_does_not_confirm():
    updated = record_hr_confirmation(
        _draft(),
        role="HR officer",
        decision="return_for_edit",
    )
    assert updated["hr_confirmation"]["classification_confirmed"] is False
    assert updated["hr_confirmation"]["routing_confirmed"] is False
    assert updated["hr_confirmation"]["decision"] == "return_for_edit"
