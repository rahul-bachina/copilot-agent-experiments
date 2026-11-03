"""Content tokens for the claim-to-source check.

A word of four letters or more is content, unless it is in the stop list.
The stop list is closed. A paraphrase that avoids the source's own words is
flagged. That is a limit of this checker, not a reading of meaning.
"""

from __future__ import annotations

import re

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]{3,}")

STOP = frozenset(
    {
        "this",
        "that",
        "with",
        "from",
        "have",
        "been",
        "were",
        "they",
        "their",
        "them",
        "which",
        "when",
        "where",
        "what",
        "into",
        "over",
        "under",
        "than",
        "then",
        "also",
        "only",
        "such",
        "some",
        "more",
        "most",
        "many",
        "much",
        "very",
        "just",
        "about",
        "after",
        "before",
        "within",
        "during",
        "these",
        "those",
        "there",
        "here",
        "would",
        "could",
        "should",
        "shall",
        "will",
        "does",
        "did",
        "done",
        "being",
        "other",
        "another",
        "because",
        "while",
        "until",
        "among",
        "between",
        "through",
        "across",
        "above",
        "below",
        "again",
        "still",
        "even",
        "both",
        "each",
        "every",
        "same",
        "onto",
        "upon",
        "without",
        "against",
        "towards",
        "whether",
        "however",
        "therefore",
        "although",
        "though",
        "since",
        "using",
        "used",
        "your",
        "yours",
        "ours",
        "ourselves",
        "themselves",
        "itself",
        "himself",
        "herself",
        "does",
        "says",
        "said",
        "note",
        "notes",
    }
)


def content_tokens(text: str) -> list[str]:
    found: list[str] = []
    for match in TOKEN.finditer(text or ""):
        word = match.group(0).casefold().strip("'-")
        if len(word) < 4 or word in STOP:
            continue
        found.append(word)
    return found
