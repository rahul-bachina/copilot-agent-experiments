"""Distress, vulnerability, grievance, and safeguarding cues.

A paraphrase counts. A denial still counts: the cue words are in the pack,
and the route is a person. The matched sentence is not returned.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import sentences
else:
    from .negate import sentences

_CUES = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"\bend of (?:my|their|his|her|our) tether\b",
        r"\bcannot go on\b",
        r"\bcan't go on\b",
        r"\bcannot cope\b",
        r"\bcan't cope\b",
        r"\bdo not want to be here\b",
        r"\bdon't want to be here\b",
        r"\bno way out\b",
        r"\bending it\b",
        r"\bend my life\b",
        r"\bbetter off without me\b",
        r"\bsuicidal\b",
        r"\bself-harm(?:ing)?\b",
        r"\bself harm(?:ing)?\b",
        r"\bharm myself\b",
        r"\bdo not want to wake\b",
        r"\bdon't want to wake\b",
        r"\bdo not feel safe\b",
        r"\bdon't feel safe\b",
        r"\bnot safe\b",
        r"\bfeel unsafe\b",
        r"\bbeing threatened\b",
        r"\bsafeguarding\b",
        r"\bwant to raise a grievance\b",
        r"\bthis is a grievance\b",
        r"\bformal complaint about\b",
        r"\bbeing bullied\b",
        r"\bnowhere left to turn\b",
        r"\bfrightened to come\b",
        r"\bafraid to come\b",
        r"\bin danger\b",
        r"\bdisclosure of abuse\b",
        r"\btreat this as a disclosure\b",
    )
)


def distress_present(text: str) -> bool:
    for sentence in sentences(text or ""):
        for pattern in _CUES:
            if pattern.search(sentence):
                return True
    return False
