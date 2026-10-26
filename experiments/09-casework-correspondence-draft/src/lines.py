"""Lines-to-take library.

A line may be cited only when its status is current, its effective date is on
or before the as-of date, and its review date is still in the future. On the
review date the line is not cited. The author needs a line that has not yet
fallen due for review.

Keyword hits on a withdrawn, overdue, or not-yet-in-force line are reported
as refused. They are not paraphrased into a new position.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

DEFAULT_LIBRARY = Path(__file__).resolve().parent.parent / "fixtures" / "lines_to_take.json"

TOPICS = (
    ("park_hours", ("opening hours", "until dusk", "park hours", "16:00", "4pm", "close the park", "close at 16:00")),
    ("allotments", ("allotment", "allotments")),
    ("litter", ("litter", "litter bin")),
    ("dogs", ("dog", "dogs", "on a lead")),
    ("bandstand", ("bandstand",)),
    ("uncovered_service", ("cafe", "café", "coffee", "lido")),
)


def _has(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text, flags=re.IGNORECASE) is not None


def load_library(path: Path | None = None) -> dict:
    library_path = path or DEFAULT_LIBRARY
    with open(library_path, encoding="utf-8") as handle:
        return json.load(handle)


def line_applicability(line: dict, as_of: date) -> tuple[bool, str]:
    """Return whether the line may be cited, and the reason if it may not."""
    if line.get("status") != "current":
        return False, str(line.get("status") or "not_current")
    effective = date.fromisoformat(line["effective_on"])
    if effective > as_of:
        return False, "not_yet_in_force"
    review = line.get("review_due_on")
    if review and date.fromisoformat(review) <= as_of:
        return False, "review_overdue"
    return True, "current"


def topics_in_text(text: str) -> list[str]:
    found = []
    for topic, phrases in TOPICS:
        if any(_has(text, phrase) for phrase in phrases):
            found.append(topic)
    return found


def match_lines(text: str, library: dict, as_of: date) -> dict:
    """Cite current in-date lines and list the rest that the keywords hit."""
    topics = topics_in_text(text)
    cited = []
    refused = []
    gaps = []

    for topic in topics:
        topic_lines = [line for line in library["lines"] if line["topic"] == topic]
        cited_for_topic = []
        for line in topic_lines:
            if not any(_has(text, keyword) for keyword in line["keywords"]):
                continue
            allowed, reason = line_applicability(line, as_of)
            record = {
                "id": line["id"],
                "topic": topic,
                "reason": reason,
                "status": line.get("status"),
                "effective_on": line.get("effective_on"),
                "review_due_on": line.get("review_due_on"),
                "text": line["text"],
            }
            if allowed:
                cited_for_topic.append(record)
            else:
                refused.append(record)
        if cited_for_topic:
            cited.extend(cited_for_topic)
        else:
            gaps.append(
                {
                    "topic": topic,
                    "summary": f"no current line to take covers {topic.replace('_', ' ')}",
                }
            )

    if not topics:
        gaps.append({"topic": "unspecified", "summary": "no current line to take covers this letter"})

    return {"topics": topics, "cited": cited, "refused": refused, "gaps": gaps}
