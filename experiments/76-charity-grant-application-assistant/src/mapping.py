"""Does a sentence support the registered-charity requirement?

A sentence supports it only when "registered" and "charity" are both
affirmed, close together, and England or Wales is affirmed in that same
sentence. A negation is not support. A qualifier is not support. Sharing
a few of the words is not support.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from cues import qualifier_in
    from negate import affirmed_positions, sentences
else:
    from .cues import qualifier_in
    from .negate import affirmed_positions, sentences

_WINDOW = 4


def _close(sentence: str, left: str, right: str) -> bool:
    for start in affirmed_positions(sentence, left):
        for other in affirmed_positions(sentence, right):
            if start <= other:
                gap = sentence[start + len(left):other]
            else:
                gap = sentence[other + len(right):start]
            if len(gap.split()) <= _WINDOW:
                return True
    return False


def supports_registered_charity(text: str) -> bool:
    """True only when the sentence actually states that requirement."""

    for sentence in sentences(text or ""):
        if qualifier_in(sentence):
            continue
        if not _close(sentence, "registered", "charity"):
            continue
        if affirmed_positions(sentence, "england") or affirmed_positions(sentence, "wales"):
            return True
    return False
