"""Shared synthetic cases. Northmere Borough Council is fictional."""

from __future__ import annotations

AS_OF = "2026-11-09"


def case(text: str, **overrides) -> dict:
    base = {
        "synthetic": True,
        "case_id": "SYN-CASE-4201",
        "channel": "web_form",
        "sector": "council",
        "text": text,
    }
    base.update(overrides)
    return base
