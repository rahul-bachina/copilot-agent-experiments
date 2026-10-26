"""Published UK identifier rules used by the gateway.

The comments cite the page that was read. Checksums are implemented only
where that page gives the steps. A format rule is not a lookup against a
live register.

Pinned on 26 October 2026. Callers who pass an earlier rules date are warned.
Detection still uses these rules.
"""

from __future__ import annotations

import re
from datetime import date

RULES_PINNED_ON = date(2026, 10, 26)

# NHS Data Dictionary, NHS NUMBER, modulus 11.
# https://www.datadictionary.nhs.uk/attributes/nhs_number.html
NHS_WEIGHTS = (10, 9, 8, 7, 6, 5, 4, 3, 2)

# NIM39110, read 26 October 2026.
# https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual/nim39110
NINO_FORBIDDEN_FIRST = frozenset("DFIQUV")
NINO_FORBIDDEN_SECOND = frozenset("DFIOQUV")
NINO_NOT_ALLOCATED = frozenset({"BG", "GB", "KN", "NK", "NT", "TN", "ZZ"})
NINO_SUFFIXES = frozenset("ABCD")

# Companies House URI customer guide, version 1.1 (05/12), prefix list.
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/809682/uniformResourceIdentifiersCustomerGuide.pdf
# WebFiling help, read the same day, writes the pre-partition Northern Ireland
# prefix as RO. The 2011 guide writes R0. Both are accepted. The guide is
# from 2011. Later prefixes were not opened.
CRN_PREFIXES = frozenset(
    {
        "AC", "ZC", "FC", "GE", "LP", "OC", "SE",
        "SA", "SZ", "SF", "GS", "SL", "SO", "SC", "ES",
        "NA", "NZ", "NF", "GN", "NL", "NC", "R0", "RO", "NI", "EN",
        "IP", "SP", "IC", "SI", "NP", "NV", "RC", "SR", "NR", "NO",
    }
)

# ILR specification 2015-16, Annex C. Inward letters never used: C I K M O V.
# https://assets.publishing.service.gov.uk/media/5a7f4a19ed915d74e62298dd/ILRSpecification_2015_16_Appendix_C_Feb2015_v1.pdf
INWARD_LETTERS = "ABDEFGHJLNPQRSTUWXYZ"
POSTCODE_RE = re.compile(
    r"\b("
    r"[A-Z]{2}\d[A-Z]"  # AANA
    r"|[A-Z]{2}\d{2}"  # AANN
    r"|[A-Z]\d[A-Z]"  # ANA
    r"|[A-Z]\d{2}"  # ANN
    r"|[A-Z]{2}\d"  # AAN
    r"|[A-Z]\d"  # AN
    rf")\s(\d[{INWARD_LETTERS}]{{2}})\b",
    re.IGNORECASE,
)

NINO_RE = re.compile(
    r"\b([A-Za-z]{2})[ \t]{0,2}(\d{2})[ \t]{0,2}(\d{2})[ \t]{0,2}(\d{2})[ \t]{0,2}([A-Da-d])\b"
)
NHS_GROUPED_RE = re.compile(r"\b(\d{3})[ \t-]+(\d{3})[ \t-]+(\d{4})\b")
NHS_CUE_RE = re.compile(r"\b(?:NHS\s+numbers?|NHS\s+no\.?)\b", re.IGNORECASE)
NHS_LABEL_RE = re.compile(
    r"\b(?:NHS\s+numbers?|NHS\s+no\.?)\b[:\s]{0,12}(\d{3}[ \t-]?\d{3}[ \t-]?\d{4}|\d{10})\b",
    re.IGNORECASE,
)
SORT_RE = re.compile(r"\b(\d{2}-\d{2}-\d{2})\b")
SORT_LABEL_RE = re.compile(r"\bsort[\s-]?codes?\b", re.IGNORECASE)
ACCOUNT_LABEL_RE = re.compile(
    r"\b(?:account\s+numbers?|account\s+no\.?|a/c|acct)\b[:\s]{0,8}(\d{6,10})\b",
    re.IGNORECASE,
)
CRN_RE = re.compile(r"\b(R0|[A-Za-z]{2})(\d{6})\b")
CRN_LABEL_RE = re.compile(
    r"\b(?:company(?:\s+registration)?\s+numbers?|company\s+no\.?|CRNs?|"
    r"Companies\s+House(?:\s+numbers?)?|registered\s+numbers?)\b[:\s]{0,8}(\d{8})\b",
    re.IGNORECASE,
)
IBAN_RE = re.compile(r"\b(GB\d{2}[A-Za-z]{4}\d{14})\b", re.IGNORECASE)
UTR_RE = re.compile(
    r"\b(?:UTRs?|unique\s+taxpayer\s+references?)\b[:\s]{0,8}(\d{10})\b",
    re.IGNORECASE,
)
EIGHT_DIGIT_RE = re.compile(r"\b(\d{8})\b")


def nhs_check_digit(first_nine: str) -> int | None:
    """Return the Data Dictionary check digit, or None when step 4 yields 10.

    Step 4 says a result of 10 means the NHS number is invalid and not used.
    A result of 11 is stored as check digit 0.
    """

    if len(first_nine) != 9 or not first_nine.isdigit():
        raise ValueError("NHS check digit needs nine digits")
    total = sum(int(digit) * weight for digit, weight in zip(first_nine, NHS_WEIGHTS))
    result = 11 - (total % 11)
    if result == 10:
        return None
    if result == 11:
        return 0
    return result


def nhs_checksum_status(ten_digits: str) -> str:
    """Return 'passed', 'failed', or 'invalid_length' for ten digits."""

    if len(ten_digits) != 10 or not ten_digits.isdigit():
        return "invalid_length"
    expected = nhs_check_digit(ten_digits[:9])
    if expected is None:
        return "failed"
    if expected == int(ten_digits[9]):
        return "passed"
    return "failed"


def classify_nino_prefix(prefix: str) -> str:
    """Classify a two-letter prefix against the three NIM39110 rules.

    ``format_accepted`` means the prefix is not in the exclusion lists.
    It does not mean HMRC has issued that number to anyone.
    """

    letters = prefix.upper()
    if len(letters) != 2 or not letters.isalpha():
        return "not_a_prefix"
    if letters[0] in NINO_FORBIDDEN_FIRST or letters[1] in NINO_FORBIDDEN_SECOND:
        return "disallowed_letter"
    if letters in NINO_NOT_ALLOCATED:
        return "not_allocated"
    return "format_accepted"


def looks_like_day_and_month(sort_code: str) -> bool:
    """True when NN-NN-NN could also be a day, a month, and a two-digit year.

    The year is not checked. 01-31 and 01-12 are enough to leave the token
    alone unless the text labels it as a sort code. That trade-off is a
    known false negative for sort codes such as 20-12-26.
    """

    day_text, month_text, _year_text = sort_code.split("-")
    day = int(day_text)
    month = int(month_text)
    return 1 <= day <= 31 and 1 <= month <= 12


def iban_checksum_status(iban: str) -> str:
    """ISO 13616 rearrangement. Remainder 1 means the check digits match.

    The paid ISO text was not opened. The steps are the published ones:
    move the first four characters to the end, A=10 … Z=35, mod 97.
    """

    compact = iban.replace(" ", "").upper()
    if not compact.startswith("GB") or len(compact) != 22:
        return "invalid_length"
    rearranged = compact[4:] + compact[:4]
    digits = []
    for character in rearranged:
        if character.isdigit():
            digits.append(character)
        elif "A" <= character <= "Z":
            digits.append(str(ord(character) - 55))
        else:
            return "failed"
    remainder = int("".join(digits)) % 97
    if remainder == 1:
        return "passed"
    return "failed"


def label_within(text: str, start: int, label: re.Pattern[str], window: int = 40) -> bool:
    """True when a label pattern occurs in the window immediately before start."""

    window_start = max(0, start - window)
    return label.search(text[window_start:start]) is not None
