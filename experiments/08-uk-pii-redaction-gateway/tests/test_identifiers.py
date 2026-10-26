"""Checksums and prefix rules, against the pages cited in identifiers.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from identifiers import (  # noqa: E402
    RULES_PINNED_ON,
    classify_nino_prefix,
    iban_checksum_status,
    looks_like_day_and_month,
    nhs_check_digit,
    nhs_checksum_status,
)


def test_rules_are_pinned():
    assert RULES_PINNED_ON.isoformat() == "2026-10-26"


def test_nhs_modulus_11_matches_the_dictionary_steps():
    assert nhs_check_digit("999000001") == 8
    assert nhs_checksum_status("9990000018") == "passed"
    assert nhs_checksum_status("9990000026") == "passed"
    # NHS England's published examples do not survive step 4.
    assert nhs_check_digit("999123456") is None
    assert nhs_checksum_status("9991234566") == "failed"
    assert nhs_checksum_status("9991234567") == "failed"


def test_check_digit_zero_when_step_4_is_11():
    assert nhs_check_digit("000000000") == 0
    assert nhs_checksum_status("0000000000") == "passed"


def test_nino_prefix_classes_follow_nim39110():
    assert classify_nino_prefix("QQ") == "disallowed_letter"
    assert classify_nino_prefix("BG") == "not_allocated"
    assert classify_nino_prefix("TN") == "not_allocated"
    assert classify_nino_prefix("ZZ") == "not_allocated"
    # Passes the three exclusion rules. Not an issued number, and not a fixture.
    assert classify_nino_prefix("AB") == "format_accepted"


def test_iban_rearrangement_accepts_the_synthetic_value():
    assert iban_checksum_status("GB76XXXX00000000000000") == "passed"
    assert iban_checksum_status("GB00XXXX00000000000000") == "failed"


def test_day_and_month_sort_code_shape():
    assert looks_like_day_and_month("20-12-26") is True
    assert looks_like_day_and_month("00-00-00") is False
    assert looks_like_day_and_month("32-01-26") is False
