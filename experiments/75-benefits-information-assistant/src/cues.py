"""Question cues. A negated phrase is not an inclusion, except a safety stem.

Distress, domestic abuse, and safeguarding are routed even when the sentence
denies them. Eligibility, awards, debt, and eviction use the same-sentence
negation rule.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import regex_affirmed, sentences
else:
    from .negate import regex_affirmed, sentences

_PATTERNS: dict[str, tuple[str, ...]] = {
    "eligibility": (
        r"will i (?:get|receive|be paid|be awarded)",
        r"would i (?:get|receive|qualify|be entitled)",
        r"do i qualify",
        r"am i (?:eligible|entitled|going to get|going to qualify)",
        r"tell me if i (?:qualify|will get|am eligible)",
        r"decide (?:my|the) (?:claim|eligibility|entitlement)",
        r"\bi will get\b",
        r"\bi am eligible\b",
        r"\bi (?:do )?qualify\b",
        r"mark me eligible",
    ),
    "award": (
        r"how much (?:will|would|do|am) i (?:get|receive|be paid|be entitled)",
        r"how much am i entitled",
        r"what (?:will|would) i be paid",
        r"calculate my (?:award|entitlement|payment|benefit)",
        r"work out my (?:award|entitlement|payment|benefit)",
        r"estimate my (?:award|entitlement|payment)",
        r"what is my entitlement",
        r"how much is my award",
    ),
    "debt": (
        r"\bin debt\b",
        r"can(?:not|'t) pay (?:the |my )?(?:rent|bills|council tax)",
        r"behind on (?:the |my )?(?:rent|bills|council tax)",
        r"\bbailiffs?\b",
        r"debt collectors?",
        r"rent arrears",
        r"i owe (?:money|rent|the council|my landlord)",
        r"struggling to pay",
        r"can(?:not|'t) afford (?:the |my )?(?:rent|food|bills)",
    ),
    "eviction": (
        r"evict",
        r"notice to quit",
        r"section 21",
        r"losing my home",
        r"told (?:me )?to leave my home",
        r"kicking me out",
        r"possession order",
        r"bailiff.{0,40}(?:door|home|flat)",
    ),
    "claim": (
        r"submit my (?:claim|application)",
        r"complete my (?:claim|application|form)",
        r"fill in my (?:claim|form|application)",
        r"file my claim",
        r"lodge my (?:claim|application)",
        r"send my claim",
    ),
    "send": (
        r"(?:email|e-mail) (?:me|this|the summary|the claim)",
        r"send (?:me|this|the summary|the claim|it to)",
        r"text me the",
    ),
    "biased": (
        r"only (?:help|answer|serve) (?:people|residents|claimants) who",
        r"do not help (?:disabled|older|foreign|non-english)",
        r"exclude (?:people|residents) who",
        r"only if (?:they|the resident) (?:is|are) (?:british|white|male)",
        r"refuse (?:the |any )?adjustments?",
    ),
    "count": (
        r"how many (?:people|residents|claimants|households)",
    ),
    "adjustment": (
        r"reasonable adjustment",
        r"large print",
        r"accessible format",
        r"british sign language",
        r"\bbsl\b",
        r"face to face",
        r"face-to-face",
    ),
    "advice": (
        r"independent advice",
        r"welfare rights",
        r"advice organisation",
        r"who can help me understand",
        r"where (?:can|do) i get advice",
    ),
    "approval_marker": (
        r"resident has approved",
        r"i approve this summary",
        r"human_approval",
        r"this summary is approved",
        r"content_hash",
    ),
    "embedded_instruction": (
        r"ignore (?:all |any )?(?:previous |prior |above |your )?instructions",
        r"you are now",
        r"system prompt",
        r"mark me eligible",
        r"override (?:the )?review date",
        r"do not offer a human",
        r"disregard the (?:pinned |knowledge )?pages",
    ),
}

_SAFETY = {
    "distress": (
        r"suicid",
        r"kill myself",
        r"end my life",
        r"self-harm",
        r"self harm",
        r"can(?:not|'t) cope",
        r"not coping",
        r"feel hopeless",
        r"no reason to live",
        r"want to die",
        r"hurt myself",
        r"\bin crisis\b",
        r"feel desperate",
    ),
    "domestic_abuse": (
        r"domestic abuse",
        r"domestic violence",
        r"hits me",
        r"hitting me",
        r"afraid of my (?:partner|husband|wife)",
        r"coercive control",
        r"not safe at home",
        r"frightened of (?:him|her|my partner)",
        r"partner hurts me",
    ),
    "safeguarding": (
        r"safeguarding",
        r"child (?:is )?at risk",
        r"child at risk",
        r"hurting (?:my |a )?child",
        r"child (?:is )?in danger",
        r"adult at risk",
        r"vulnerable adult",
        r"\bneglect\b",
    ),
}

_BENEFITS: tuple[tuple[str, str], ...] = (
    ("housing_benefit", r"housing benefit"),
    ("council_tax_benefit", r"council tax benefit"),
    ("council_tax_reduction", r"council tax (?:reduction|support)"),
    ("universal_credit", r"universal credit"),
    ("pension_credit", r"pension credit"),
    ("discretionary_housing_payment", r"discretionary housing payment|\bdhp\b"),
    ("synthetic_illustration", r"synthetic illustration"),
    ("leap_note", r"leap-day review|leap day review"),
)

_KINDS: tuple[tuple[str, str], ...] = (
    ("evidence", r"\bevidence\b|documents do i need|what do i need to provide|proof of"),
    ("apply", r"how (?:do i |to )?(?:apply|claim)|application process|where do i apply"),
    ("what", r"what is|what are|what does|explain|tell me about|describe|in general|used for"),
)

_GENERAL = re.compile(r"general information|this page explains|what the benefit is", re.IGNORECASE)
_QUALIFIER = re.compile(
    r"\bexcept\b|\bunless\b|provided that|save where|other than|only if|only when",
    re.IGNORECASE,
)
_CLEARANCE_CLAIM = re.compile(
    r"\bmy clearance is\b|\bi have .{0,30}clearance\b|\bi am the adviser\b|\bmy role is\b",
    re.IGNORECASE,
)
_CALLER_RULE = re.compile(
    r"\bthe (?:rate|rule|threshold) is\b|\beveryone (?:with|who).{0,40}(?:gets|qualifies)\b",
    re.IGNORECASE,
)


def category_hit(text: str, category: str) -> bool:
    if not text or category not in _PATTERNS:
        return False
    for pattern in _PATTERNS[category]:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            return True
    return False


def safety_hit(text: str, category: str) -> bool:
    """A safety stem is kept even when the sentence denies it."""

    if not text or category not in _SAFETY:
        return False
    for pattern in _SAFETY[category]:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def carve_out(text: str) -> bool:
    """Acceptable wording followed by a qualification is not acceptable."""

    for sentence in sentences(text or ""):
        if _QUALIFIER.search(sentence) and (
            _GENERAL.search(sentence)
            or category_hit(sentence, "eligibility")
            or category_hit(sentence, "award")
            or category_hit(sentence, "biased")
        ):
            return True
    return False


def benefits_in(text: str) -> list[str]:
    found = []
    for name, pattern in _BENEFITS:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            found.append(name)
    return found


def kinds_in(text: str) -> list[str]:
    found = []
    for name, pattern in _KINDS:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            found.append(name)
    if category_hit(text, "advice"):
        found.append("advice")
    if category_hit(text, "adjustment"):
        found.append("adjustment")
    return found


def clearance_claimed(text: str) -> bool:
    return bool(_CLEARANCE_CLAIM.search(text or ""))


def caller_rule_claimed(text: str) -> bool:
    return bool(regex_affirmed(text or "", _CALLER_RULE))
