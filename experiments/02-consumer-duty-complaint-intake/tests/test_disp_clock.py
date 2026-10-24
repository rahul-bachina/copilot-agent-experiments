"""Unit tests for the deterministic DISP clock.

Expected bank-holiday dates are the England and Wales list published at
https://www.gov.uk/bank-holidays and read on 24 October 2026. Years that
were altered by proclamation (2020, 2022, 2023) are tested as overrides,
not as if the statute had moved.
"""

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from disp_clock import (  # noqa: E402
    add_business_days,
    add_calendar_months,
    calculate_disp_clock,
    easter_sunday,
    fos_referral_deadline,
    is_england_wales_business_day,
    reference_psp_closed_dates,
    statutory_england_and_wales_bank_holidays,
    weekday_bank_holidays,
)


# Weekday bank holidays only. Weekend Christmas Day or Boxing Day is omitted,
# matching the way GOV.UK lists a substitute instead of the weekend day.
GOVUK_WEEKDAY = {
    2021: {
        date(2021, 1, 1),
        date(2021, 4, 2),
        date(2021, 4, 5),
        date(2021, 5, 3),
        date(2021, 5, 31),
        date(2021, 8, 30),
        date(2021, 12, 27),
        date(2021, 12, 28),
    },
    2024: {
        date(2024, 1, 1),
        date(2024, 3, 29),
        date(2024, 4, 1),
        date(2024, 5, 6),
        date(2024, 5, 27),
        date(2024, 8, 26),
        date(2024, 12, 25),
        date(2024, 12, 26),
    },
    2025: {
        date(2025, 1, 1),
        date(2025, 4, 18),
        date(2025, 4, 21),
        date(2025, 5, 5),
        date(2025, 5, 26),
        date(2025, 8, 25),
        date(2025, 12, 25),
        date(2025, 12, 26),
    },
    2026: {
        date(2026, 1, 1),
        date(2026, 4, 3),
        date(2026, 4, 6),
        date(2026, 5, 4),
        date(2026, 5, 25),
        date(2026, 8, 31),
        date(2026, 12, 25),
        date(2026, 12, 28),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 3, 26),
        date(2027, 3, 29),
        date(2027, 5, 3),
        date(2027, 5, 31),
        date(2027, 8, 30),
        date(2027, 12, 27),
        date(2027, 12, 28),
    },
    2028: {
        date(2028, 1, 3),
        date(2028, 4, 14),
        date(2028, 4, 17),
        date(2028, 5, 1),
        date(2028, 5, 29),
        date(2028, 8, 28),
        date(2028, 12, 25),
        date(2028, 12, 26),
    },
}


def _deadline(result: dict, name: str) -> dict:
    matches = [item for item in result["deadlines"] if item["name"] == name]
    assert len(matches) == 1, name
    return matches[0]


class TestBankHolidays:
    @pytest.mark.parametrize("year", sorted(GOVUK_WEEKDAY))
    def test_weekday_holidays_match_govuk(self, year):
        assert weekday_bank_holidays(year) == GOVUK_WEEKDAY[year]

    def test_easter_sundays_used_by_those_years(self):
        assert easter_sunday(2026) == date(2026, 4, 5)
        assert easter_sunday(2027) == date(2027, 3, 28)
        assert easter_sunday(2028) == date(2028, 4, 16)

    def test_scotland_world_cup_day_is_a_business_day_in_england(self):
        # GOV.UK lists 15 June 2026 as a bank holiday in Scotland only.
        closed = statutory_england_and_wales_bank_holidays(2026)
        assert date(2026, 6, 15) not in closed
        assert is_england_wales_business_day(date(2026, 6, 15), set(closed))

    def test_proclaimed_days_are_not_invented(self):
        holidays_2022 = statutory_england_and_wales_bank_holidays(2022)
        holidays_2023 = statutory_england_and_wales_bank_holidays(2023)
        assert date(2022, 9, 19) not in holidays_2022  # state funeral
        assert date(2022, 6, 2) not in holidays_2022  # moved spring bank holiday
        assert date(2022, 6, 3) not in holidays_2022  # Platinum Jubilee
        assert date(2022, 5, 30) in holidays_2022  # standing last Monday in May
        assert date(2023, 5, 8) not in holidays_2023  # coronation
        assert date(2020, 5, 4) in statutory_england_and_wales_bank_holidays(2020)
        assert date(2020, 5, 8) not in statutory_england_and_wales_bank_holidays(2020)

    def test_override_for_a_moved_bank_holiday(self):
        # Early May 2020 was moved from Monday 4 May to Friday 8 May (VE Day).
        # Received Friday 1 May. Standing rule: Mon 4 is closed, so the third
        # business day is Thursday 7 May. With the Monday cancelled it is
        # Wednesday 6 May (Mon 4, Tue 5, Wed 6).
        standing = calculate_disp_clock(date(2020, 5, 1))
        moved = calculate_disp_clock(
            date(2020, 5, 1),
            extra_non_business_days=[date(2020, 5, 8)],
            cancelled_bank_holidays=[date(2020, 5, 4)],
        )
        assert _deadline(standing, "Summary resolution route closes")["on"] == "2020-05-07"
        assert _deadline(moved, "Summary resolution route closes")["on"] == "2020-05-06"

        # Received Thursday 7 May. Friday 8 May must not be counted once added.
        ve_week = calculate_disp_clock(
            date(2020, 5, 7),
            extra_non_business_days=[date(2020, 5, 8)],
            cancelled_bank_holidays=[date(2020, 5, 4)],
        )
        assert _deadline(ve_week, "Summary resolution route closes")["on"] == "2020-05-13"


class TestSummaryResolution:
    def test_ordinary_friday_skips_the_weekend(self):
        result = calculate_disp_clock(date(2026, 1, 2))
        # Fri 2 Jan. Mon 5, Tue 6, Wed 7.
        item = _deadline(result, "Summary resolution route closes")
        assert item["on"] == "2026-01-07"
        assert item["operative"] is True
        assert item["rule"] == "DISP 1.5.1R"

    def test_christmas_eve_2026(self):
        result = calculate_disp_clock(date(2026, 12, 24))
        # Thu 24 Dec. Fri 25 Christmas, Mon 28 Boxing substitute.
        # Tue 29, Wed 30, Thu 31.
        assert _deadline(result, "Summary resolution route closes")["on"] == "2026-12-31"

    def test_received_on_christmas_day_itself(self):
        result = calculate_disp_clock(date(2026, 12, 25))
        assert _deadline(result, "Summary resolution route closes")["on"] == "2026-12-31"

    def test_received_on_good_friday(self):
        result = calculate_disp_clock(date(2026, 4, 3))
        # Good Friday. Easter Monday 6 April is closed. Tue 7, Wed 8, Thu 9.
        assert _deadline(result, "Summary resolution route closes")["on"] == "2026-04-09"

    def test_received_on_easter_saturday_matches_good_friday(self):
        friday = calculate_disp_clock(date(2026, 4, 3))
        saturday = calculate_disp_clock(date(2026, 4, 4))
        assert (
            _deadline(friday, "Summary resolution route closes")["on"]
            == _deadline(saturday, "Summary resolution route closes")["on"]
            == "2026-04-09"
        )

    def test_new_year_substitute_2028(self):
        result = calculate_disp_clock(date(2027, 12, 31))
        # Fri 31 Dec 2027 is a business day. 1 Jan 2028 is Saturday,
        # substitute Monday 3 Jan is closed. Tue 4, Wed 5, Thu 6.
        assert _deadline(result, "Summary resolution route closes")["on"] == "2028-01-06"

    def test_day_of_receipt_is_not_counted_even_when_it_is_a_business_day(self):
        result = calculate_disp_clock(date(2026, 1, 5))  # Monday
        assert _deadline(result, "Summary resolution route closes")["on"] == "2026-01-08"


class TestEightWeeks:
    def test_eight_weeks_is_fifty_six_days(self):
        result = calculate_disp_clock(date(2026, 1, 2))
        item = _deadline(result, "Final or other written response")
        assert item["on"] == "2026-02-27"
        assert item["rule"] == "DISP 1.6.2R"
        assert item["operative"] is True

    def test_deadline_stays_on_a_weekend(self):
        # Saturday 3 Jan 2026 + 56 days is Saturday 28 Feb 2026.
        result = calculate_disp_clock(date(2026, 1, 3))
        assert _deadline(result, "Final or other written response")["on"] == "2026-02-28"

    def test_deadline_stays_on_good_friday(self):
        # Friday 29 Jan 2027 + 56 days is Good Friday 26 Mar 2027.
        result = calculate_disp_clock(date(2027, 1, 29))
        assert _deadline(result, "Final or other written response")["on"] == "2027-03-26"
        assert result["operative_final_response_due_on"] == "2027-03-26"

    def test_exceptional_flag_does_not_extend_a_general_complaint(self):
        plain = calculate_disp_clock(date(2026, 1, 2))
        flagged = calculate_disp_clock(date(2026, 1, 2), exceptional_circumstances=True)
        assert flagged["operative_final_response_due_on"] == plain["operative_final_response_due_on"]
        assert flagged["exceptional_circumstances"] is False
        assert any("was not extended" in note for note in flagged["notes"])

    def test_acknowledgement_has_no_invented_day_count(self):
        item = _deadline(calculate_disp_clock(date(2026, 1, 2)), "Prompt acknowledgement")
        assert item["on"] is None
        assert item["rule"] == "DISP 1.6.1R"


class TestPsdAndEmd:
    def test_reference_count_is_not_operative_without_a_psp_calendar(self):
        result = calculate_disp_clock(date(2026, 1, 5), route="psd")
        # Hand count, E&W calendar, receipt Monday 5 Jan 2026: 15th open day is Mon 26 Jan.
        assert _deadline(result, "15-business-day final response")["on"] == "2026-01-26"
        assert _deadline(result, "15-business-day final response")["operative"] is False
        assert result["operative_final_response_due_on"] is None
        assert result["psp_opening_calendar_supplied"] is False

    def test_christmas_reference_count(self):
        result = calculate_disp_clock(date(2026, 12, 24), route="emd")
        # Hand count across Christmas 2026 and New Year 2027: Tue 19 Jan 2027.
        assert _deadline(result, "15-business-day final response")["on"] == "2027-01-19"
        assert _deadline(result, "15-business-day final response")["operative"] is False

    def test_operative_when_the_handler_asserts_the_england_wales_calendar(self):
        closed = reference_psp_closed_dates(date(2026, 1, 5))
        result = calculate_disp_clock(
            date(2026, 1, 5), route="psd", psp_closed_dates=closed
        )
        final = _deadline(result, "15-business-day final response")
        extended = _deadline(result, "35-business-day final response")
        assert final["operative"] is True
        assert final["on"] == "2026-01-26"
        assert extended["operative"] is False
        assert extended["on"] == "2026-02-23"
        assert result["operative_final_response_due_on"] == "2026-01-26"
        assert result["operative_final_response_rule"] == "DISP 1.6.2AR(1)"

    def test_exceptional_circumstances_move_the_operative_final_to_day_35(self):
        closed = reference_psp_closed_dates(date(2026, 1, 5))
        result = calculate_disp_clock(
            date(2026, 1, 5),
            route="psd",
            exceptional_circumstances=True,
            psp_closed_dates=closed,
        )
        assert _deadline(result, "Holding response")["on"] == "2026-01-26"
        assert _deadline(result, "Holding response")["operative"] is True
        assert _deadline(result, "35-business-day final response")["operative"] is True
        assert result["operative_final_response_due_on"] == "2026-02-23"
        assert result["operative_final_response_rule"] == "DISP 1.6.2AR(2)(b)"

    def test_a_psp_open_every_day_does_not_skip_weekends(self):
        result = calculate_disp_clock(
            date(2026, 1, 5), route="psd", psp_closed_dates=[]
        )
        # Open every day: 15 days after Monday 5 Jan is Tuesday 20 Jan.
        assert _deadline(result, "15-business-day final response")["on"] == "2026-01-20"
        assert _deadline(result, "15-business-day final response")["operative"] is True

    def test_saturday_counts_when_the_psp_is_open_on_saturday(self):
        # Closed on Sundays only. Friday 2 Jan 2026: Sat 3 is business day 1.
        sundays = []
        cursor = date(2026, 1, 1)
        while cursor <= date(2026, 3, 1):
            if cursor.weekday() == 6:
                sundays.append(cursor)
            cursor += timedelta(days=1)
        result = calculate_disp_clock(
            date(2026, 1, 2), route="psd", psp_closed_dates=sundays
        )
        # Sat 3 is day 1. Fifteen open days later, skipping Sundays, is Tue 20 Jan.
        assert _deadline(result, "15-business-day final response")["on"] == "2026-01-20"

    def test_mixed_keeps_both_clocks_and_does_not_pick_one(self):
        result = calculate_disp_clock(date(2026, 1, 5), route="mixed")
        assert _deadline(result, "Eight-week written response")["operative"] is True
        assert _deadline(result, "Eight-week written response")["on"] == "2026-03-02"
        assert _deadline(result, "15-business-day final response")["operative"] is False
        assert result["operative_final_response_due_on"] is None
        assert any("human makes that choice" in note for note in result["notes"])

    def test_unknown_route_is_rejected(self):
        with pytest.raises(ValueError):
            calculate_disp_clock(date(2026, 1, 5), route="fos")


class TestFosWindows:
    def test_general_referral_opens_the_day_after_the_eight_week_date(self):
        result = calculate_disp_clock(date(2026, 1, 2))
        assert result["fos"]["may_refer_from_if_no_qualifying_response"] == "2026-02-28"
        assert result["fos"]["may_refer_from_operative"] is True
        assert result["fos"]["six_month_last_day_to_refer"] is None

    def test_six_month_anniversary_is_the_last_day(self):
        assert fos_referral_deadline(date(2026, 1, 15)) == date(2026, 7, 15)
        assert fos_referral_deadline(date(2026, 8, 31)) == date(2027, 2, 28)
        assert fos_referral_deadline(date(2024, 8, 31)) == date(2025, 2, 28)
        assert fos_referral_deadline(date(2023, 8, 31)) == date(2024, 2, 29)
        result = calculate_disp_clock(date(2026, 1, 2), response_sent_on=date(2026, 1, 15))
        assert result["fos"]["six_month_last_day_to_refer"] == "2026-07-15"
        assert result["fos"]["six_month_rule"] == "DISP 2.8.2R(1)"

    def test_longstop_takes_the_later_date_and_does_not_infer_awareness(self):
        result = calculate_disp_clock(
            date(2026, 1, 2),
            event_complained_of=date(2020, 1, 1),
            complainant_aware_on=date(2025, 6, 1),
        )
        longstop = result["fos"]["longstop"]
        assert longstop["six_years_after_event"] == "2026-01-01"
        assert longstop["three_years_after_awareness"] == "2028-06-01"
        assert longstop["later_of_the_two"] == "2028-06-01"
        assert "DISP 2.8.2R(3) exceptional circumstances" in " ".join(
            longstop["exceptions_not_applied"]
        )

        unknown = calculate_disp_clock(
            date(2026, 1, 2), event_complained_of=date(2024, 2, 29)
        )
        assert unknown["fos"]["longstop"]["six_years_after_event"] == "2030-02-28"
        assert unknown["fos"]["longstop"]["three_years_after_awareness"] is None
        assert unknown["fos"]["longstop"]["awareness_is_a_human_judgement"] is True

    def test_leap_day_corresponding_date(self):
        assert add_calendar_months(date(2024, 2, 29), 6) == date(2024, 8, 29)
        assert add_calendar_months(date(2024, 1, 31), 1) == date(2024, 2, 29)


class TestReceiptZone:
    def test_bst_aware_datetime_uses_london(self):
        # 23:30 UTC on 3 Apr 2026 is 00:30 on 4 Apr in London (BST).
        instant = datetime(2026, 4, 3, 23, 30, tzinfo=timezone.utc)
        aware = calculate_disp_clock(instant)
        naive = calculate_disp_clock(datetime(2026, 4, 3, 23, 30))
        assert aware["received_on"] == "2026-04-04"
        assert naive["received_on"] == "2026-04-03"
        assert any("naive datetime" in note.lower() for note in naive["notes"])

    def test_same_inputs_are_identical(self):
        first = calculate_disp_clock(date(2026, 12, 24), route="general")
        second = calculate_disp_clock(date(2026, 12, 24), route="general")
        assert first == second
        json.dumps(first)


class TestTheModuleDoesNotDecide:
    def test_public_surface_has_no_outcome_action(self):
        import disp_clock

        forbidden = ("uphold", "reject", "send", "close_case", "redress", "pay")
        names = [name.lower() for name in dir(disp_clock) if not name.startswith("_")]
        for word in forbidden:
            assert word not in names

    def test_result_has_no_outcome_fields(self):
        result = calculate_disp_clock(date(2026, 1, 2), route="psd")
        blob = json.dumps(result).lower()
        for phrase in ("upheld", "redress_amount", "case_closed", "email_sent"):
            assert phrase not in blob

    def test_business_day_walk_matches_an_independent_counter(self):
        closed = statutory_england_and_wales_bank_holidays(2026) | statutory_england_and_wales_bank_holidays(
            2027
        )

        def independent(start: date, count: int) -> date:
            current = start
            left = count
            while left:
                current += timedelta(days=1)
                if current.weekday() < 5 and current not in closed:
                    left -= 1
            return current

        start = date(2026, 12, 24)
        assert add_business_days(
            start, 15, lambda day: is_england_wales_business_day(day, closed)
        ) == independent(start, 15)
        assert independent(start, 15) == date(2027, 1, 19)
