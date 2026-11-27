"""Small-number suppression, including differences and other field names."""

from src.fairness import report


def _numbers(payload):
    found = []

    def walk(value):
        if isinstance(value, bool):
            return
        if isinstance(value, int):
            found.append(value)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return found


def test_a_small_count_is_not_published_as_a_difference_or_under_another_name():
    events = [{"group": "north-synthetic", "outcome": "answer"} for _ in range(6)]
    events += [{"group": "south-synthetic", "outcome": "answer"} for _ in range(2)]
    published = report(events)
    south = published["groups"]["south-synthetic"]
    assert south["count"] is None
    assert south["n"] is None
    assert south["headcount"] is None
    assert south["total_people"] is None
    assert south["people_affected"] is None
    assert south["suppressed"] is True
    assert published["differences"]["north-synthetic_minus_south-synthetic"] is None
    assert published["percentages"]["south-synthetic"] is None
    assert published["percentages"]["north-synthetic"] is None
    assert published["share"] is None
    assert published["delta"] is None
    assert published["n"] is None
    assert published["headcount"] is None
    assert published["total_people"] is None
    assert published["published_total"] is None
    assert published["described_as_anonymised"] is False
    assert 2 not in _numbers(published)


def test_two_large_groups_can_show_a_difference():
    events = [{"group": "north-synthetic"} for _ in range(6)]
    events += [{"group": "south-synthetic"} for _ in range(6)]
    published = report(events)
    assert published["groups"]["north-synthetic"]["count"] == 6
    assert published["differences"]["north-synthetic_minus_south-synthetic"] == 0
    assert published["percentages"]["north-synthetic"] == 50.0
    assert published["described_as_anonymised"] is False
