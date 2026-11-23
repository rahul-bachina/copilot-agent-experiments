"""Whether two texts are the same duty, and whether a control addresses it.

A reworded sentence with the same affirmed themes is a near-duplicate.
A negated sentence is not. A carve-out is not an acceptable match.
A control supports an obligation only when every theme is affirmed with
"must" or "shall" and the sentence has no carve-out. "should" does not
support a "must". Experiment 69 can mark a qualified sentence as support
at low confidence. This module does not.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from cues import biased
    from negate import carve_out, clauses, denial_split, qualified, sentences, strength_of
else:
    from .cues import biased
    from .negate import carve_out, clauses, denial_split, qualified, sentences, strength_of

THEMES: dict[str, list[list[str]]] = {
    "keep_register": [
        ["keep", "keeps", "keeping", "kept", "maintain", "maintains", "maintaining", "maintained", "hold", "holds", "holding", "held", "retain", "retains", "retaining", "retained"],
        ["register", "registers", "inventory", "inventories"],
        ["obligation", "obligations"],
    ],
    "review_register": [
        ["review", "reviews", "reviewed", "reviewing", "reassess", "reassesses", "reassessed"],
        ["register", "registers", "inventory", "inventories"],
    ],
    "certificate": [
        ["certificate", "certificates", "certified", "certification"],
        ["specified function", "specified functions"],
        ["employee", "employees", "staff"],
    ],
    "approval": [
        ["reasonable care"],
        ["controlled function", "controlled functions", "senior management function", "senior management functions"],
        ["approval", "approvals", "approved"],
    ],
    "complaints": [
        ["record", "records", "log"],
        ["complaint", "complaints"],
    ],
}
_AT_LEAST = re.compile(r"\bat least every\s+(\d+)\s+months?\b", re.IGNORECASE)
_EVERY = re.compile(r"\bevery\s+(\d+)\s+months?\b", re.IGNORECASE)
_STOP = frozenset(
    "a an the of to and or for its that this with by from on in is are be as at least every".split()
)


def _hit(text: str, alternative: str) -> bool:
    return re.search(rf"\b{re.escape(alternative)}\b", text or "", re.IGNORECASE) is not None


def _groups_hit(text: str, groups: list[list[str]]) -> bool:
    return all(any(_hit(text, alternative) for alternative in group) for group in groups)


def theme_reading(text: str) -> dict:
    affirmed: set[str] = set()
    denied: set[str] = set()
    is_qualified = False
    strengths: list[str] = []
    is_biased = biased(text)
    for sentence in sentences(text or ""):
        if qualified(sentence):
            is_qualified = True
        _main, _carve = carve_out(sentence)
        for clause in clauses(sentence):
            scope, denied_span = denial_split(clause)
            strengths.append(strength_of(clause))
            for theme, groups in THEMES.items():
                in_scope = _groups_hit(scope, groups)
                in_denied = _groups_hit(denied_span, groups) if denied_span else False
                if in_denied and not in_scope:
                    denied.add(theme)
                elif in_scope and not in_denied:
                    affirmed.add(theme)
                elif in_scope and in_denied:
                    denied.add(theme)
    both = affirmed & denied
    affirmed -= both
    if both:
        is_biased = is_biased
    strength = _combine(strengths, denied=bool(denied) and not affirmed)
    return {
        "affirmed": sorted(affirmed),
        "denied": sorted(denied),
        "contradiction": bool(both),
        "qualified": is_qualified,
        "strength": strength,
        "biased": is_biased,
        "acceptable": False,
        "included": bool(affirmed) and not is_qualified and strength == "must" and not is_biased,
    }


def _combine(strengths: list[str], denied: bool) -> str:
    usable = [item for item in strengths if item != "unstated"]
    if not usable:
        return "denied" if denied else "unstated"
    if "ambiguous" in usable:
        return "ambiguous"
    unique = set(usable)
    if unique == {"must"}:
        return "must"
    if len(unique) == 1:
        return unique.pop()
    if "must" in unique and unique <= {"must", "denied", "must_not"}:
        return "must" if "must" in unique and "must_not" not in unique else "ambiguous"
    return "ambiguous"


def interval_months(text: str) -> dict:
    """Months between reviews. Two different numbers are not reduced to one."""

    at_least = [int(match.group(1)) for match in _AT_LEAST.finditer(text or "")]
    stripped = _AT_LEAST.sub(" ", text or "")
    every = [int(match.group(1)) for match in _EVERY.finditer(stripped)]
    found = at_least + every
    unique = list(dict.fromkeys(found))
    if not unique:
        return {"months": None, "not_stated": True, "multiple": False, "coerced": False, "chosen": False}
    if len(unique) != 1:
        return {"months": None, "not_stated": False, "multiple": True, "coerced": False, "chosen": False}
    return {"months": unique[0], "not_stated": False, "multiple": False, "coerced": False, "chosen": False}


def addresses(control_text: str, theme_ids: list[str]) -> dict:
    """Support is true only for an unqualified must that hits every theme."""

    reading = theme_reading(control_text)
    base = {
        "addresses": False,
        "supports": False,
        "acceptable": False,
        "qualified": reading["qualified"],
        "strength": reading["strength"],
        "biased": reading["biased"],
        "route_to_human": bool(reading["biased"] or reading["contradiction"]),
        "affirmed": reading["affirmed"],
        "denied": reading["denied"],
        "guessed": False,
    }
    if reading["biased"] or reading["contradiction"]:
        return base
    if reading["qualified"] or reading["strength"] != "must":
        return base
    if any(theme in reading["denied"] for theme in theme_ids):
        return base
    if theme_ids and all(theme in reading["affirmed"] for theme in theme_ids):
        base["addresses"] = True
        base["supports"] = True
        return base
    return base


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", (text or "").casefold())
    return {word for word in words if word not in _STOP and len(word) > 2}


def jaccard(left: str, right: str) -> float:
    a = _tokens(left)
    b = _tokens(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def relation(left: str, right: str) -> str:
    """exact, near, qualified_near, contradiction, or none.

    near includes a reworded must with the same themes. A negation is not near.
    """

    a = theme_reading(left)
    b = theme_reading(right)
    if a["qualified"] or b["qualified"]:
        if a["affirmed"] and a["affirmed"] == b["affirmed"]:
            return "qualified_near"
        return "none"
    if a["affirmed"] and b["denied"] and set(a["affirmed"]) & set(b["denied"]):
        return "contradiction"
    if b["affirmed"] and a["denied"] and set(b["affirmed"]) & set(a["denied"]):
        return "contradiction"
    if not a["affirmed"] or a["affirmed"] != b["affirmed"]:
        return "none"
    if a["strength"] != "must" or b["strength"] != "must":
        return "none"
    if _normal(left) == _normal(right):
        return "exact"
    if jaccard(left, right) >= 0.72 or a["affirmed"] == b["affirmed"]:
        return "near"
    return "none"


def _normal(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (text or "").casefold()))


def same_duty(left: str, right: str) -> bool:
    return relation(left, right) in {"exact", "near"}
