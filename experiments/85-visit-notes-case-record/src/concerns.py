"""Flag concern language. Do not assess risk, need, or eligibility.

A stem is routed even when the sentence denies it. The denial is recorded.
The cue text is not copied into the flag.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from negate import bounded, denied_at, sentences
    from paraphrases import PHRASES
else:
    from .negate import bounded, denied_at, sentences
    from .paraphrases import PHRASES


def _needle(phrase: str) -> str:
    return phrase.casefold().rstrip(".!? ")


def sentence_hits(sentence: str) -> list[dict]:
    folded = sentence.casefold()
    found: list[dict] = []
    for category, phrases in PHRASES.items():
        matches: list[bool] = []
        for phrase in phrases:
            needle = _needle(phrase)
            start = 0
            while True:
                index = folded.find(needle, start)
                if index < 0:
                    break
                if bounded(folded, index, len(needle)):
                    matches.append(not denied_at(sentence, needle, index))
                start = index + max(len(needle), 1)
        if not matches:
            continue
        affirmed = any(matches)
        found.append({
            "category": category,
            "affirmed": affirmed,
            "negated": not affirmed,
            "text_copied": False,
            "assessment_made": False,
        })
    return found


def hits(text: str) -> list[dict]:
    rows: list[dict] = []
    for sentence in sentences(text or ""):
        for hit in sentence_hits(sentence):
            rows.append(hit)
    return rows


def categories_in(text: str) -> list[str]:
    found: list[str] = []
    for hit in hits(text):
        if hit["category"] not in found:
            found.append(hit["category"])
    return found


def affirmed_categories(text: str) -> list[str]:
    found: list[str] = []
    for hit in hits(text):
        if hit["affirmed"] and hit["category"] not in found:
            found.append(hit["category"])
    return found


def routed(text: str) -> bool:
    return bool(hits(text))
