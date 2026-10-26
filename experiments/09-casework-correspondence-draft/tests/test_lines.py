"""A line is cited only while it is current and still inside its review date."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lines import line_applicability, load_library, match_lines  # noqa: E402

AS_OF = date(2026, 10, 26)


def test_library_is_synthetic_and_labelled():
    library = load_library()
    assert "fictional" in library["organisation"].lower()
    assert library["lines"]


def test_current_park_line_is_cited_and_the_withdrawn_line_is_refused():
    library = load_library()
    match = match_lines(
        "Please confirm the opening hours. A neighbour says the parks close at 16:00.",
        library,
        AS_OF,
    )
    cited = [line["id"] for line in match["cited"]]
    refused = {line["id"]: line["reason"] for line in match["refused"]}
    assert cited == ["LTT-PARKS-01"]
    assert refused["LTT-PARKS-00"] == "withdrawn"
    assert "park_hours" not in [gap["topic"] for gap in match["gaps"]]


def test_overdue_litter_line_is_not_cited():
    library = load_library()
    match = match_lines("The litter bin by the gate has not been emptied.", library, AS_OF)
    assert match["cited"] == []
    assert match["refused"][0]["id"] == "LTT-LITTER-01"
    assert match["refused"][0]["reason"] == "review_overdue"
    assert match["gaps"][0]["topic"] == "litter"


def test_future_dog_line_is_not_cited():
    library = load_library()
    line = next(item for item in library["lines"] if item["id"] == "LTT-DOGS-02")
    allowed, reason = line_applicability(line, AS_OF)
    assert allowed is False
    assert reason == "not_yet_in_force"
    match = match_lines("Can dogs be off a lead in the playground?", library, AS_OF)
    assert match["cited"] == []
    assert match["gaps"][0]["topic"] == "dogs"


def test_review_date_itself_is_not_citable():
    line = {
        "status": "current",
        "effective_on": "2026-01-01",
        "review_due_on": "2026-10-26",
    }
    allowed, reason = line_applicability(line, AS_OF)
    assert allowed is False
    assert reason == "review_overdue"


def test_uncovered_topic_is_a_gap_with_no_line():
    library = load_library()
    match = match_lines("Will you license a coffee franchise in the park?", library, AS_OF)
    assert match["cited"] == []
    assert match["refused"] == []
    assert match["gaps"][0]["topic"] == "uncovered_service"
