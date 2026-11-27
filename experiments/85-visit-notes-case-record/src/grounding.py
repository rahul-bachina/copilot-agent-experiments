"""Whether a statement is supported by the cited line.

A supported statement is a contiguous span of that line. A denial in the
same sentence is not support for the positive claim. A diagnosis, an
eligibility finding, or a risk rating that the line does not contain is
not support. Nothing here invents a quote.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import bounded, denied_at
else:
    from .negate import bounded, denied_at

DIAGNOSIS_TOKENS = (
    "dementia",
    "eligible",
    "eligibility",
    "high risk",
    "low risk",
    "lacks capacity",
    "has capacity",
    "diagnosis",
    "depressed",
)

_SPACE = re.compile(r"\s+")


def normalise(text: str) -> str:
    return _SPACE.sub(" ", (text or "").casefold()).strip(" .!?")


def supports_claim(claim: str, line: str) -> bool:
    """True only when the claim is a span of the line and the line does not deny it."""

    if not isinstance(claim, str) or not isinstance(line, str):
        return False
    if not claim.strip() or not line.strip():
        return False
    folded_claim = claim.casefold()
    folded_line = line.casefold()
    for token in DIAGNOSIS_TOKENS:
        if token in folded_claim and token not in folded_line:
            return False
    needle = normalise(claim)
    hay = normalise(line)
    if not needle or needle not in hay:
        return False
    index = hay.find(needle)
    if not bounded(hay, index, len(needle)):
        return False
    raw_needle = claim.casefold().strip().rstrip(".!? ")
    raw_index = folded_line.find(raw_needle)
    if raw_index < 0:
        raw_index = folded_line.find(needle)
    if raw_index >= 0 and denied_at(line, raw_needle if raw_needle in folded_line else needle, raw_index):
        return False
    return True


def is_supported(statement: dict, lines: dict[int, str]) -> bool:
    """A verbatim statement cites one line. An inferred one is only joined spans."""

    if not isinstance(statement, dict):
        return False
    cited = statement.get("source_lines")
    if not isinstance(cited, list) or not cited:
        return False
    if statement.get("inferred") is True:
        parts = statement.get("parts")
        if not isinstance(parts, list) or len(parts) != len(cited):
            return False
        for part, number in zip(parts, cited):
            if not isinstance(number, int) or number not in lines:
                return False
            if not isinstance(part, str) or not supports_claim(part, lines[number]):
                return False
        return True
    if len(cited) != 1 or not isinstance(cited[0], int) or cited[0] not in lines:
        return False
    text = statement.get("text")
    if not isinstance(text, str):
        return False
    return supports_claim(text, lines[cited[0]])


def score_claims(rows: list[dict]) -> dict:
    """Precision and recall for a labelled set. Rows are not added to a case total."""

    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0
    for row in rows:
        predicted = supports_claim(row["claim"], row["line"])
        expected = bool(row["supported"])
        if predicted and expected:
            true_positive += 1
        elif predicted and not expected:
            false_positive += 1
        elif not predicted and expected:
            false_negative += 1
        else:
            true_negative += 1
    predicted_positive = true_positive + false_positive
    actual_positive = true_positive + false_negative
    precision = 1.0 if predicted_positive == 0 else true_positive / predicted_positive
    recall = 1.0 if actual_positive == 0 else true_positive / actual_positive
    return {
        "precision": precision,
        "recall": recall,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "positives": actual_positive,
        "negatives": true_negative + false_positive,
        "not_added_to_case_total": True,
    }
