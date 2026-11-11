"""Keyword codes for one redacted text.

A hit is a code on the text. It is not a conclusion about a person.
Themes can overlap. Sentiment is one of four codes.
"""

from __future__ import annotations

import re

SENTIMENTS = ("negative", "positive", "mixed", "unclear")

# Longer phrases first. Single words use a boundary so "wait" does not hit "awaited".
_NEGATIVE = (
    "could not get through",
    "couldn't get through",
    "could not complain",
    "couldn't make a complaint",
    "complaint was ignored",
    "do not understand",
    "don't understand",
    "did not understand",
    "didn't understand",
    "did not reply",
    "didn't reply",
    "no reply",
    "no one answered",
    "nobody answered",
    "on hold",
    "long wait",
    "hung up",
    "not explained",
    "nobody explained",
    "unclear",
    "confusing",
    "jargon",
    "misleading",
    "unhappy",
    "disappointed",
    "frustrated",
    "rude",
    "unhelpful",
    "waited",
    "complaint",
)
_POSITIVE = (
    "explained clearly",
    "good service",
    "thank you",
    "thanks",
    "helpful",
    "resolved",
    "polite",
    "clear",
    "understood",
)

# (theme_id, family, phrases). Family is the outcome-testing bucket for a
# financial-services pack. A public-service pack records the family and does
# not apply PRIN.
THEMES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "unclear_information",
        "consumer_understanding",
        (
            "do not understand",
            "don't understand",
            "did not understand",
            "didn't understand",
            "unclear",
            "confusing",
            "jargon",
            "misleading",
            "not explained",
            "nobody explained",
        ),
    ),
    (
        "could_not_get_support",
        "consumer_support",
        (
            "could not get through",
            "couldn't get through",
            "on hold",
            "no reply",
            "did not reply",
            "didn't reply",
            "no one answered",
            "nobody answered",
            "hung up",
            "long wait",
            "waited",
        ),
    ),
    (
        "barrier_to_complaint",
        "consumer_support",
        (
            "could not complain",
            "couldn't make a complaint",
            "complaint was ignored",
            "no acknowledgement",
        ),
    ),
    (
        "staff_manner",
        "consumer_support",
        ("rude", "shouted", "unhelpful"),
    ),
    (
        "support_helped",
        "consumer_support",
        ("helpful", "resolved", "explained clearly", "polite", "thank you", "thanks"),
    ),
)


def _has(text: str, phrase: str) -> bool:
    if " " in phrase or "'" in phrase:
        return phrase in text
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def _hits(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_has(text, phrase) for phrase in phrases)


def sentiment_of(text: str) -> str:
    """One code for the text. Supplied labels are not read here."""

    lowered = (text or "").lower()
    negative = _hits(lowered, _NEGATIVE)
    positive = _hits(lowered, _POSITIVE)
    if negative and positive:
        return "mixed"
    if negative:
        return "negative"
    if positive:
        return "positive"
    return "unclear"


def themes_of(text: str) -> list[str]:
    """Theme ids in lexicon order. Overlap is expected."""

    lowered = (text or "").lower()
    return [theme_id for theme_id, _family, phrases in THEMES if _hits(lowered, phrases)]


def theme_family(theme_id: str) -> str:
    for candidate, family, _phrases in THEMES:
        if candidate == theme_id:
            return family
    return "none"
