"""Compare dates written in a policy with the pinned FCA dates.

Only lines that talk about the application window or regime commencement
are checked. Other dates in a policy are left alone. This is a text
comparison, not a conclusion about when the law commences.
"""

from __future__ import annotations

import calendar
import re
from datetime import date

from .sources import APPLICATION_WINDOW_CLOSES, APPLICATION_WINDOW_OPENS, REGIME_COMMENCEMENT

_MONTHS = {name.lower(): number for number, name in enumerate(calendar.month_name) if name}

_LONG_DATE = re.compile(
    r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(20\d{2})\b",
    re.IGNORECASE,
)
_ISO_DATE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
_WINDOW = re.compile(r"application\s+(?:window|period)", re.IGNORECASE)
_COMMENCEMENT = re.compile(
    r"(regime\s+(?:starts|start\b|will\s+start|is\s+expected|goes\s+live)|"
    r"comes\s+into\s+force|go-live|commencement)",
    re.IGNORECASE,
)

WINDOW_DATES = {
    date.fromisoformat(APPLICATION_WINDOW_OPENS),
    date.fromisoformat(APPLICATION_WINDOW_CLOSES),
}
COMMENCEMENT_DATES = {date.fromisoformat(REGIME_COMMENCEMENT)}


def dates_in_line(line: str) -> list[date]:
    """Return calendar dates written on one line. Invalid dates are skipped."""
    found: list[date] = []
    for day, month, year in _LONG_DATE.findall(line):
        try:
            found.append(date(int(year), _MONTHS[month.lower()], int(day)))
        except ValueError:
            continue
    for year, month, day in _ISO_DATE.findall(line):
        try:
            found.append(date(int(year), int(month), int(day)))
        except ValueError:
            continue
    return found


def date_observations(documents: list[dict]) -> list[dict]:
    """List dates on window or commencement lines that are not the pinned ones.

    documents items need id and usable_text. Injection lines are already gone
    from usable_text, and a quarantined document has empty usable text.
    """
    rows: list[dict] = []
    for document in documents:
        for number, line in enumerate(document["usable_text"].splitlines(), start=1):
            window = _WINDOW.search(line) is not None
            commencement = _COMMENCEMENT.search(line) is not None
            if not window and not commencement:
                continue
            allowed: set[date] = set()
            if window:
                allowed |= WINDOW_DATES
            if commencement:
                allowed |= COMMENCEMENT_DATES
            for found in dates_in_line(line):
                if found in allowed:
                    continue
                rows.append(
                    {
                        "document_id": document["id"],
                        "line": number,
                        "date_in_text": found.isoformat(),
                        "line_excerpt": line.strip()[:240],
                        "text_observation": "date_in_text_differs_from_pinned_fca_page",
                        "accepted_as_gap": False,
                        "pinned_application_window": [
                            APPLICATION_WINDOW_OPENS,
                            APPLICATION_WINDOW_CLOSES,
                        ],
                        "pinned_regime_commencement": REGIME_COMMENCEMENT,
                        "note": (
                            "The date on this line is not the date pinned from the "
                            "FCA pages verified on 24 October 2026. That is a text "
                            "comparison for the Compliance Officer or MLRO. It is "
                            "not a conclusion about legal commencement."
                        ),
                    }
                )
    return rows
