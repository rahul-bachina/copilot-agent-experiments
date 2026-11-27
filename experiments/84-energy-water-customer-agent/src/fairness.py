"""Fairness counts for synthetic groups.

A count below 5 is not published. A difference or a percentage that would
reveal that count is not published either, including under another field
name. Five is this starter's threshold. It is not anonymisation. The group
code is not used to choose an answer.
"""

from __future__ import annotations

THRESHOLD = 5
_ALIASES = ("count", "n", "headcount", "total_people", "people_affected")


def report(events: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        group = event.get("group")
        if not isinstance(group, str) or not group:
            group = "unknown"
        counts[group] = counts.get(group, 0) + 1
    any_small = (not counts) or any(value < THRESHOLD for value in counts.values())
    total = sum(counts.values())
    if total < THRESHOLD:
        any_small = True
    groups: dict[str, dict] = {}
    for group in sorted(counts):
        value = counts[group]
        small = value < THRESHOLD or any_small and value < THRESHOLD
        published = None if value < THRESHOLD else value
        row = {"suppressed": value < THRESHOLD, "share": None, "percentage": None, "difference": None}
        for name in _ALIASES:
            row[name] = published
        groups[group] = row
    differences: dict[str, int | None] = {}
    names = sorted(counts)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            key = left + "_minus_" + right
            if counts[left] < THRESHOLD or counts[right] < THRESHOLD or any_small:
                differences[key] = None
            else:
                differences[key] = counts[left] - counts[right]
    percentages: dict[str, float | None] = {}
    for group, value in counts.items():
        if any_small or value < THRESHOLD or total < THRESHOLD:
            percentages[group] = None
        else:
            percentages[group] = round(100.0 * value / total, 1)
    return {
        "threshold": THRESHOLD,
        "threshold_is_starter_rule": True,
        "described_as_anonymised": False,
        "any_suppressed": any(row["suppressed"] for row in groups.values()) if groups else False,
        "groups": groups,
        "differences": differences,
        "percentages": percentages,
        "delta": None if any_small else differences,
        "share": None if any_small else percentages,
        "n": None if any_small else total,
        "headcount": None if any_small else total,
        "total_people": None if any_small else total,
        "people_affected": None if any_small else total,
        "published_total": None if any_small else total,
    }
