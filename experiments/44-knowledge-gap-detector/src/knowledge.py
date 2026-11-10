"""Approved knowledge base for an invented service.

Northmere Knowledge Service is not a council, a bank, an insurer, or a
supplier. Article bodies are not copied into the detector's output.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KB = ROOT / "fixtures" / "knowledge_base.json"

ORGANISATION = "Northmere Knowledge Service (fictional)"

JARGON = (
    "hereinafter",
    "aforementioned",
    "notwithstanding",
    "utilise",
    "utilize",
    "commence",
    "the customer shall",
)
ACCESS_PHRASES = ("another format", "large print", "easy read", "audio")
MAX_SENTENCE_WORDS = 25

REQUIRED_ARTICLE_KEYS = (
    "id",
    "title",
    "sector",
    "status",
    "effective_from",
    "review_due",
    "last_reviewed",
    "topic",
    "claim",
    "polarity",
    "keywords",
    "body",
)

# Closed hints. A group matches when any term is present. All groups must match.
# exclude drops the hint. These phrases are the starter's, not customer text.
HINTS: tuple[dict, ...] = (
    {"topic": "blue-badge", "groups": (("blue badge",),), "exclude": ()},
    {
        "topic": "missed-bin",
        "groups": (("missed bin", "bin was not collected", "missed collection"),),
        "exclude": (),
    },
    {"topic": "opening-hours", "groups": (("opening hours", "counter hours"),), "exclude": ()},
    {"topic": "concessionary-bus", "groups": (("concessionary bus",),), "exclude": ()},
    {"topic": "legacy-bus-leaflet", "groups": (("legacy bus pass leaflet",),), "exclude": ()},
    {
        "topic": "statement",
        "groups": (("where is my statement", "statement date"),),
        "exclude": (),
    },
    {"topic": "account-fee", "groups": (("account fee", "monthly fee"),), "exclude": ()},
    {"topic": "garden-waste", "groups": (("garden waste",),), "exclude": ()},
    {"topic": "vpn-809", "groups": (("vpn",), ("809",)), "exclude": ("legacy", "2019")},
    {
        "topic": "legacy-vpn",
        "groups": (("legacy vpn", "vpn client 2019"),),
        "exclude": (),
    },
    {"topic": "yellow-lines", "groups": (("yellow lines", "yellow line"),), "exclude": ()},
    {"topic": "meter-reading", "groups": (("meter reading", "meter read"),), "exclude": ()},
)

TITLES = {
    "blue-badge": "Draft: renewing a blue badge",
    "missed-bin": "Draft: a missed bin collection",
    "opening-hours": "Draft: counter opening hours",
    "concessionary-bus": "Draft: concessionary bus pass",
    "legacy-bus-leaflet": "Draft: refresh the bus-pass leaflet",
    "statement": "Draft: where a statement is shown",
    "account-fee": "Draft: the monthly account fee",
    "garden-waste": "Draft: garden waste",
    "vpn-809": "Draft: VPN error 809",
    "legacy-vpn": "Draft: legacy VPN client",
    "yellow-lines": "Draft: yellow line restrictions",
    "meter-reading": "Draft: giving a meter reading",
}

OUTLINE_SECTIONS = (
    "Who this is for",
    "The question, written by the knowledge manager. This outline does not copy the query.",
    "The steps a reader can take",
    "What this article does not decide",
    "How to ask for another format",
    "The date the article should next be reviewed",
)


def load_articles(library: list[dict] | None = None) -> list[dict]:
    if library is not None:
        articles = library
    else:
        payload = json.loads(DEFAULT_KB.read_text(encoding="utf-8"))
        articles = payload["articles"]
    checked = []
    for article in articles:
        if not isinstance(article, dict):
            raise ValueError("an article must be an object")
        missing = [key for key in REQUIRED_ARTICLE_KEYS if key not in article]
        if missing:
            raise ValueError("an article is missing a required field")
        if article["polarity"] not in {"affirm", "deny"}:
            raise ValueError("polarity must be affirm or deny")
        checked.append(article)
    return checked


def _groups_match(hay: str, groups) -> bool:
    return all(any(term in hay for term in group) for group in groups)


def hint_topics(text: str) -> list[str]:
    hay = (text or "").lower()
    found = []
    for hint in HINTS:
        if any(term in hay for term in hint["exclude"]):
            continue
        if _groups_match(hay, hint["groups"]):
            found.append(hint["topic"])
    return found


def article_matches(article: dict, hay: str, sector: str) -> bool:
    if article["sector"] not in {sector, "any"}:
        return False
    if any(term in hay for term in article.get("exclude") or []):
        return False
    return _groups_match(hay, article["keywords"])


def citation_block(article: dict, as_of: date, is_stale) -> tuple[bool, str]:
    """Whether this starter may treat the article as current coverage.

    review_due on the as-of date is not citable. That is this starter's rule.
    last_reviewed uses Experiment 21's is_stale, including its 180-day window.
    """

    if article["status"] != "current":
        return False, article["status"]
    effective = date.fromisoformat(article["effective_from"])
    if effective > as_of:
        return False, "not_yet_in_force"
    review_due = date.fromisoformat(article["review_due"])
    if review_due <= as_of:
        return False, "review_due"
    if is_stale(article["last_reviewed"], as_of):
        return False, "last_reviewed_window"
    return True, "citable"


def screen_wording(body: str) -> dict:
    sentences = [part.strip() for part in re.split(r"[.!?]+", body or "") if part.strip()]
    long = []
    for sentence in sentences:
        count = len(sentence.split())
        if count > MAX_SENTENCE_WORDS:
            long.append(count)
    hay = (body or "").lower()
    jargon = [term for term in JARGON if term in hay]
    accessible = any(phrase in hay for phrase in ACCESS_PHRASES)
    return {
        "passed": not long and not jargon,
        "long_sentence_word_counts": long,
        "jargon": jargon,
        "accessible_format_mentioned": accessible,
        "max_words": MAX_SENTENCE_WORDS,
        "is_the_prin_test": False,
    }


def conflicts_among(citable: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for article in citable:
        groups.setdefault((article["topic"], article["claim"]), []).append(article)
    found = []
    for (topic, claim), articles in groups.items():
        polarities = {article["polarity"] for article in articles}
        if "affirm" in polarities and "deny" in polarities:
            found.append(
                {
                    "topic": topic,
                    "claim": claim,
                    "article_ids": sorted(article["id"] for article in articles),
                    "winner_chosen": False,
                }
            )
    found.sort(key=lambda item: (item["topic"], item["claim"]))
    return found


def title_for(topic: str) -> str:
    if topic.startswith("unmatched-"):
        return "Draft article"
    return TITLES.get(topic, "Draft article")
