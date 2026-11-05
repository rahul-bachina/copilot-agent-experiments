"""Deterministic normalisation. The class is decided here, not by a model.

A value the rules do not accept is unparsed. Identical unparsed text is a
match of the text, not a finding that the value is valid. A difference the
rules do not collapse is material. The reviewer resolves material rows.
This module does not choose a source.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from siblings import load
else:
    from .siblings import load

FIELD_TYPES = (
    "name",
    "address",
    "date",
    "currency",
    "postcode",
    "company_number",
    "figure",
    "reference",
)

CLASSES = ("match", "immaterial_difference", "material_discrepancy")

_MONTHS: dict[str, int] = {}
for _index, _name in enumerate(
    (
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ),
    start=1,
):
    _MONTHS[_name] = _index
    _MONTHS[_name[:3]] = _index

_TITLES = frozenset({"mr", "mrs", "ms", "miss", "mx", "dr", "prof", "sir", "dame"})
_SUFFIX = {"limited": "ltd", "ltd": "ltd", "plc": "plc", "llp": "llp", "cic": "cic"}
_STREET = {
    "st": "street",
    "street": "street",
    "rd": "road",
    "road": "road",
    "ave": "avenue",
    "avenue": "avenue",
    "ln": "lane",
    "lane": "lane",
    "dr": "drive",
    "drive": "drive",
    "ct": "court",
    "court": "court",
    "pl": "place",
    "place": "place",
    "gdns": "gardens",
    "gardens": "gardens",
}
_FIGURE_UNIT = {
    "day": "days",
    "days": "days",
    "month": "months",
    "months": "months",
    "%": "percent",
    "percent": "percent",
}
_CRN_LABEL = re.compile(
    r"(?i)\b(?:company(?:\s+registration)?\s+numbers?|company\s+no\.?|crns?|registered\s+numbers?)\b[:\s]*"
)
_CURRENCY_GROUPED = re.compile(r"\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?")


def display_fold(value: str) -> str:
    """Case and whitespace only. Punctuation stays, so a real difference is not hidden."""
    return re.sub(r"\s+", " ", value).strip().casefold()


def _name(raw: str) -> str | None:
    text = raw.casefold().replace("&", " and ")
    text = text.replace(".", " ").replace(",", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    text = re.sub(r"\bpublic limited company\b", "plc", text)
    text = re.sub(r"\blimited liability partnership\b", "llp", text)
    text = re.sub(r"\bcommunity interest company\b", "cic", text)
    tokens = text.split(" ")
    if len(tokens) >= 2 and tokens[0] in _TITLES and len(tokens[1]) == 1:
        tokens = tokens[1:]
    return " ".join(_SUFFIX.get(token, token) for token in tokens)


def _address(raw: str) -> str | None:
    """Expand a street abbreviation only when it is the last word.

    Expanding St anywhere would turn a saint's name into Street and could
    hide a real difference. A town after the street word is left as it is,
    so that pair stays material if the street words differ.
    """
    text = raw.casefold().replace(".", " ").replace(",", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    tokens = text.split(" ")
    last = tokens[-1]
    if last in _STREET:
        tokens[-1] = _STREET[last]
    return " ".join(tokens)


def _as_date(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _date(raw: str) -> str | None:
    """UK day-first numbers. A two-digit year is not accepted. ISO is year-month-day."""
    text = raw.strip()
    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if iso:
        return _as_date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
    numeric = re.fullmatch(r"(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})", text)
    if numeric:
        return _as_date(int(numeric.group(3)), int(numeric.group(2)), int(numeric.group(1)))
    named = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if named:
        month = _MONTHS.get(named.group(2).casefold())
        if month is None:
            return None
        return _as_date(int(named.group(3)), month, int(named.group(1)))
    return None


def _currency(raw: str) -> str | None:
    """Pence as a decimal string. The pound sign is removed. Other currencies stay unparsed."""
    text = raw.strip().replace("\u00a3", "")
    text = re.sub(r"(?i)\bgbp\b", "", text).strip()
    negative = False
    if text.startswith("-"):
        negative = True
        text = text[1:].strip()
    text = text.replace(" ", "")
    if not _CURRENCY_GROUPED.fullmatch(text):
        return None
    amount = Decimal(text.replace(",", ""))
    pence = amount * 100
    if pence != pence.to_integral_value():
        return None
    sign = "-" if negative else ""
    return f"{sign}{int(pence)}"


def _postcode(raw: str) -> str | None:
    """One space before the inward code, using Experiment 08's six shapes."""
    pattern = load()["identifiers"].POSTCODE_RE
    compact = re.sub(r"\s+", "", raw).upper()
    if not 5 <= len(compact) <= 7:
        return None
    spaced = f"{compact[:-3]} {compact[-3:]}"
    if pattern.fullmatch(spaced):
        return spaced.upper()
    return None


def _company_number(raw: str) -> str | None:
    """Eight digits, or a prefix from Experiment 08 plus six digits.

    Numeric forms are padded to eight digits. That is formatting. It is not
    a Companies House lookup. An unknown prefix is left unparsed.
    """
    prefixes = load()["identifiers"].CRN_PREFIXES
    text = _CRN_LABEL.sub("", raw).strip()
    compact = re.sub(r"[\s-]+", "", text).upper()
    if re.fullmatch(r"\d{1,8}", compact):
        return compact.zfill(8)
    match = re.fullmatch(r"(R0|[A-Z]{2})(\d{6})", compact)
    if match and match.group(1) in prefixes:
        return match.group(1) + match.group(2)
    return None


def _figure(raw: str) -> str | None:
    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)(?:\s+(days?|months?|%|percent))?\s*",
        raw,
        re.IGNORECASE,
    )
    if not match:
        return None
    number = Decimal(match.group(1))
    if number == number.to_integral_value():
        shown = str(int(number))
    else:
        shown = format(number.normalize(), "f")
    unit = _FIGURE_UNIT.get((match.group(2) or "").casefold(), "")
    return f"{shown}|{unit}"


def _reference(raw: str) -> str | None:
    folded = display_fold(raw)
    return folded or None


_RULES = {
    "name": _name,
    "address": _address,
    "date": _date,
    "currency": _currency,
    "postcode": _postcode,
    "company_number": _company_number,
    "figure": _figure,
    "reference": _reference,
}


def normalise_value(field_type: str, raw: str) -> tuple[str | None, bool]:
    """Return (canonical, accepted). Unparsed values are (None, False)."""
    if field_type not in _RULES:
        raise ValueError("field_type is not in the closed list")
    if not isinstance(raw, str):
        raise TypeError("field value must be a string")
    canonical = _RULES[field_type](raw)
    if canonical is None:
        return None, False
    return canonical, True


def classify_values(items: list[tuple[str | None, str, bool]]) -> tuple[str, str]:
    """Classify two or more usable values. The caller handles missing citations.

    `items` are (canonical, display_fold, accepted).
    """
    if len(items) < 2:
        raise ValueError("classify_values needs two usable values")
    if any(not accepted for _, _, accepted in items):
        if all(not accepted for _, _, accepted in items) and len({fold for _, fold, _ in items}) == 1:
            return "match", "same_unparsed_text"
        return "material_discrepancy", "unparseable"
    canonicals = {canonical for canonical, _, _ in items}
    folds = {fold for _, fold, _ in items}
    if len(canonicals) == 1 and len(folds) == 1:
        return "match", "same_display"
    if len(canonicals) == 1:
        return "immaterial_difference", "formatting_or_abbreviation"
    return "material_discrepancy", "normalised_values_differ"
