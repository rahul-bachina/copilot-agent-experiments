"""Shared token rules for descriptions and utterances.

A content token is a word of four letters or more, or a three-letter token
written in capitals in the source (FOI, EIR, SAR). Function words and words
that appear in almost every skill in this repository are stopped, so a
shared word such as "draft" does not select a skill.
"""

from __future__ import annotations

import re

STOP = frozenset(
    """
    a an the and or of to for in on with by from this that these those
    one use used using when skill skills agent agents you your our their
    are was were been being have has had does did not into only call calls
    calling json python showing existing member staff paste pastes pasted
    its then than also each every before after which what where while
    within without under over such some other another will can may must
    should would could about above below between through during against
    because there here just more most same very any all both few own how
    who why out off per via once else but yet so if as at be is it do
    never always please want need like make made get got let see look
    tell ask asked asking help helps something anything everything nothing
    someone catalogue experiment experiments synthetic locally local
    return returns returned show shows draft drafts approve reject send
    write writes written read reads file files dont cannot
    including include includes onto upon across among
    """.split()
)

_WORD = re.compile(r"[A-Za-z0-9]+")


def normalise_phrase(text: str) -> str:
    """Lower case, drop apostrophes, and collapse everything else to spaces."""
    cleaned = text.lower().replace("'", "")
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def content_tokens(text: str) -> list[str]:
    """Return content tokens in order. Duplicates are kept; callers unique them."""
    found: list[str] = []
    for match in _WORD.finditer(text or ""):
        raw = match.group(0)
        word = raw.lower()
        if word in STOP:
            continue
        if len(word) >= 4 or (len(word) == 3 and raw.isupper() and raw.isalpha()):
            found.append(word)
    return found


def token_set(text: str) -> set[str]:
    return set(content_tokens(text))
