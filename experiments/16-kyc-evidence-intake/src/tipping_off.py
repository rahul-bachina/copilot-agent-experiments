"""Customer-facing wording must not hint at suspicion.

Proceeds of Crime Act 2002, section 333A, was opened on 27 October 2026.
Subsection (1) covers disclosing that a disclosure under that Part has been
made, where that is likely to prejudice an investigation. Subsection (3)
covers disclosing that an investigation is being contemplated or carried out.
This module does not decide whether an offence would be committed. It keeps
a closed list of words out of the note a customer might later be shown.

The list is not complete. A hint that avoids these words can pass. The
reviewer still has to read the note. The agent does not send it.
"""

from __future__ import annotations

import re

# Short tokens are matched as words so "pepper" is not "pep".
SHORT_WORDS = ("sar", "pep", "nca", "edd")

SUBSTRINGS = (
    "suspicious",
    "suspicion",
    "money laundering",
    "terrorist",
    "investigat",
    "nominated officer",
    "national crime agency",
    "tipping",
    "politically exposed",
    "high-risk",
    "high risk",
    "fatf",
    "enhanced due diligence",
    "source of wealth",
    "source of funds",
    "unusual",
    "complex",
    "declined",
    "rejected",
    "approved",
    "risk rating",
    "cannot tell you",
    "we suspect",
    "filed a",
)

SAFE_FALLBACK = "Please contact the firm about the papers already on the file."

IDENTITY_ASK = (
    "Please provide a document that shows your identity, such as a passport "
    "or a driving licence."
)
IDENTITY_REFRESH_ASK = (
    "Please provide a recent document that shows your identity, such as a "
    "passport or a driving licence."
)
ADDRESS_ASK = (
    "Please provide a document that shows your address, such as a council tax "
    "bill or a utility bill."
)
ADDRESS_REFRESH_ASK = (
    "Please provide a recent document that shows your address, such as a "
    "council tax bill or a utility bill."
)
PURPOSE_ASK = "Please describe the purpose of the relationship in your own words."
NONE_ASK = (
    "Please tell us if a document you already provided should be replaced "
    "with a clearer copy."
)
OUTRO = "This note does not give a reason for any item."


def lexicon_hits(text: str) -> list[str]:
    """Return listed words that appear in ``text``, in list order."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    lower = text.lower()
    found: list[str] = []
    for word in SHORT_WORDS:
        if re.search(rf"\b{word}\b", lower):
            found.append(word)
    for phrase in SUBSTRINGS:
        if phrase in lower:
            found.append(phrase)
    return found


def guard_customer_text(text: str) -> dict:
    """Keep the text only when the lexicon is clear. Otherwise use the fallback.

    The fallback is itself checked. If that ever matches, the caller must not
    invent a third sentence.
    """

    hits = lexicon_hits(text)
    fallback_hits = lexicon_hits(SAFE_FALLBACK)
    if fallback_hits:
        raise RuntimeError("the tipping-off fallback matches its own lexicon")
    if hits:
        return {
            "text": SAFE_FALLBACK,
            "hints_at_suspicion": False,
            "hints_found": hits,
            "replaced_by_guard": True,
            "may_be_sent_by_agent": False,
            "audience": "customer",
        }
    published_hits = lexicon_hits(text)
    return {
        "text": text,
        "hints_at_suspicion": bool(published_hits),
        "hints_found": published_hits,
        "replaced_by_guard": False,
        "may_be_sent_by_agent": False,
        "audience": "customer",
    }
