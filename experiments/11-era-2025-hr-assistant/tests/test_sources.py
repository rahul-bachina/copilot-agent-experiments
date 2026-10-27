"""The pinned dates are the pages opened on 27 October 2026."""

from datetime import date

from src.sources import (
    ACAS_UPDATED,
    ALL_REASONABLE_STEPS_IN_FORCE,
    LAST_VERIFIED,
    NDA_INSTRUMENT_OPENED,
    REASONABLE_STEPS_IN_FORCE,
    SCOTLAND_CONTRACT_INSTRUMENT_OPENED,
    SCOTLAND_CONTRACT_TIMELINE_DATE,
    SOURCES,
    SPECIFIED_STEPS_REGULATIONS_MADE,
    SPECIFY_STEPS_POWER_IN_FORCE,
    THIRD_PARTY_IN_FORCE,
    TRIBUNAL_LIMITS_IN_FORCE,
    UNFAIR_DISMISSAL_IN_FORCE,
    WHISTLEBLOWING_IN_FORCE,
)


def test_catalogue_was_opened_on_27_october_2026():
    assert LAST_VERIFIED == "2026-10-27"
    assert all(row["last_verified"] == LAST_VERIFIED for row in SOURCES)
    assert all(row["url"].startswith("https://") for row in SOURCES)
    assert all("legislation.gov.uk" in row["url"] or "www.gov.uk" in row["url"] or "acas.org.uk" in row["url"] for row in SOURCES)


def test_commencement_dates_match_the_instruments_that_were_opened():
    assert REASONABLE_STEPS_IN_FORCE == date(2024, 10, 26)
    assert ALL_REASONABLE_STEPS_IN_FORCE == date(2026, 10, 30)
    assert THIRD_PARTY_IN_FORCE == date(2026, 10, 30)
    assert SPECIFY_STEPS_POWER_IN_FORCE == date(2026, 10, 30)
    assert WHISTLEBLOWING_IN_FORCE == date(2026, 4, 6)
    assert TRIBUNAL_LIMITS_IN_FORCE == date(2026, 10, 1)
    assert UNFAIR_DISMISSAL_IN_FORCE == date(2027, 1, 1)
    assert SPECIFIED_STEPS_REGULATIONS_MADE is False


def test_unopened_dates_are_not_treated_as_instruments():
    assert SCOTLAND_CONTRACT_TIMELINE_DATE == "2026-11-09"
    assert SCOTLAND_CONTRACT_INSTRUMENT_OPENED is False
    assert NDA_INSTRUMENT_OPENED is False
    assert ACAS_UPDATED == "2026-08-26"


def test_section_40b_is_described_as_a_power_not_a_list():
    section_22 = next(row for row in SOURCES if row["id"] == "era-2025-s22")
    assert "No regulations" in section_22["notes"]
    assert "section/22" in section_22["url"]
