"""Exact decimal helpers. Rates are strings. Floats are refused."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY = Decimal("0.0001")
UNIT = Decimal("0.000001")
QUANTITY = Decimal("0.0001")

_NUMBER = r"-?\d+(?:\.\d+)?"


class InexactNumber(ValueError):
    """A JSON float cannot be a rate or a quantity."""


def parse_decimal(value: object) -> Decimal:
    """Parse a str or an int. Reject bools and floats."""
    if isinstance(value, bool) or value is None:
        raise InexactNumber("missing or boolean")
    if isinstance(value, float):
        raise InexactNumber("float")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"nan", "inf", "infinity", "+inf", "-inf"}:
            raise InexactNumber("not a decimal string")
        try:
            parsed = Decimal(text)
        except InvalidOperation as exc:
            raise InexactNumber("not a decimal string") from exc
        if not parsed.is_finite():
            raise InexactNumber("not finite")
        return parsed
    raise InexactNumber(type(value).__name__)


def q(value: Decimal, places: Decimal) -> str:
    return str(value.quantize(places, rounding=ROUND_HALF_UP))


def money(value: Decimal) -> str:
    return q(value, MONEY)


def unit(value: Decimal) -> str:
    return q(value, UNIT)


def quantity(value: Decimal) -> str:
    quantized = value.quantize(QUANTITY, rounding=ROUND_HALF_UP)
    if quantized == quantized.to_integral():
        return str(quantized.to_integral())
    return str(quantized)
