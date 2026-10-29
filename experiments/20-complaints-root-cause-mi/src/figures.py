"""Count and sum figures. A count equals the length of its record-id list."""

from __future__ import annotations

import re
from datetime import date, datetime

_NUMBER = re.compile(r"\d+")


def count_figure(figure_id: str, record_ids: list[str]) -> dict:
    ids = sorted(record_ids)
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"{figure_id} repeats a record id")
    return {"id": figure_id, "kind": "count", "value": len(ids), "record_ids": ids}


def sum_pence_figure(figure_id: str, pairs: list[tuple[str, int]]) -> dict:
    ids = [record_id for record_id, _pence in pairs]
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"{figure_id} repeats a record id")
    ordered = sorted(pairs, key=lambda item: item[0])
    total = sum(pence for _record_id, pence in ordered)
    return {
        "id": figure_id,
        "kind": "sum_pence",
        "value": total,
        "record_ids": [record_id for record_id, _pence in ordered],
    }


def supplied_integer(figure_id: str, value: int, source: str) -> dict:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{figure_id} is not an integer")
    return {
        "id": figure_id,
        "kind": "supplied_integer",
        "value": value,
        "record_ids": [],
        "source": source,
    }


def to_pence(value: object) -> int | None:
    """Whole pence, or None when the field was not recorded.

    A present value that is not a non-negative number of pence is an error.
    Absence is not zero.
    """

    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("redress must be a number of pounds or omitted")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("redress must not be negative")
        return value * 100
    if isinstance(value, float):
        pence = value * 100
        if abs(pence - round(pence)) > 1e-6:
            raise ValueError("redress is not a whole number of pence")
        rounded = int(round(pence))
        if rounded < 0:
            raise ValueError("redress must not be negative")
        return rounded
    raise ValueError("redress must be a number of pounds or omitted")


def sentence(sentence_id: str, text: str, figure_ids: list[str], **extra) -> dict:
    row = {"sentence_id": sentence_id, "text": text, "figure_ids": list(figure_ids)}
    row.update(extra)
    return row


def _date_tokens(value: date) -> set[str]:
    return {f"{value.year:04d}", f"{value.month:02d}", f"{value.day:02d}"}


def assert_sentences(sentences: list[dict], figures: dict[str, dict], dates: list[date]) -> None:
    allowed_dates: set[str] = set()
    for value in dates:
        allowed_dates |= _date_tokens(value)
    for row in sentences:
        allowed = set(allowed_dates)
        for figure_id in row["figure_ids"]:
            if figure_id not in figures:
                raise RuntimeError(f"{row['sentence_id']} cites a missing figure")
            allowed.add(str(figures[figure_id]["value"]))
        for token in _NUMBER.findall(row["text"]):
            if token not in allowed:
                raise RuntimeError(
                    f"{row['sentence_id']} contains {token}, which is not a cited figure or a period date"
                )
        if "£" in row["text"] or "%" in row["text"]:
            raise RuntimeError(f"{row['sentence_id']} contains a rate or a currency sign")


def parse_date(value: object, *, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be YYYY-MM-DD")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field} must be YYYY-MM-DD") from exc
