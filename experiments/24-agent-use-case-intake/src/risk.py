"""Queueing tier for one proposal. Not a DPIA and not an Orange Book score.

Unknown answers do not lower a tier, and they do not raise one. A high
fact that was actually recorded still makes the tier high.
"""

from __future__ import annotations

NOTE = (
    "This tier orders a governance queue. It is not a finding that processing "
    "is high risk under UK GDPR Article 35, and it is not an Orange Book assessment. "
    "The Orange Book was not opened for this experiment."
)


def _tri(block: dict | None, key: str) -> str:
    if not isinstance(block, dict) or key not in block:
        return "missing"
    value = block.get(key)
    if value in {"yes", "no", "unknown"}:
        return value
    return "missing"


def _flag(block: dict | None, key: str) -> bool:
    return isinstance(block, dict) and block.get(key) is True


def risk_tier(proposal: dict) -> dict:
    data = proposal.get("data") if isinstance(proposal.get("data"), dict) else {}
    decisions = proposal.get("decisions_affected") if isinstance(proposal.get("decisions_affected"), dict) else {}
    personal = _tri(data, "personal_data")
    special = _tri(data, "special_category")
    criminal = _tri(data, "criminal_offence_data")
    effect = decisions.get("significant_effect")
    if effect not in {"legal", "similarly_significant", "none", "unknown"}:
        effect = "missing"
    interaction = _tri(proposal, "public_interaction")
    wanted = proposal.get("autonomy_wanted")
    classification = data.get("classification")

    gaps = []
    for name, value in (
        ("personal_data", personal),
        ("special_category", special),
        ("significant_effect", effect),
        ("public_interaction", interaction),
    ):
        if value in {"missing", "unknown"}:
            gaps.append(name)
    if wanted not in {"A0", "A1", "A2", "A3"}:
        gaps.append("autonomy_wanted")

    highs: list[str] = []
    if special == "yes":
        highs.append("special_category_recorded")
    if criminal == "yes":
        highs.append("criminal_offence_data_recorded")
    if effect in {"legal", "similarly_significant"}:
        highs.append("legal_or_similarly_significant_effect_recorded")
    if _flag(decisions, "significant_automated_decision"):
        highs.append("significant_automated_decision_recorded")
    if _flag(decisions, "regulated_decision"):
        highs.append("regulated_decision_recorded")
    if wanted == "A3":
        highs.append("autonomy_a3_requested")
    if classification == "secret_or_above":
        highs.append("classification_secret_or_above")

    mediums: list[str] = []
    if personal == "yes":
        mediums.append("personal_data_recorded")
    if interaction == "yes":
        mediums.append("public_interaction_recorded")

    if highs:
        tier = "high"
        rules = highs + mediums
    elif gaps:
        tier = "not_assessed"
        rules = mediums
    elif mediums:
        tier = "medium"
        rules = mediums
    else:
        tier = "low"
        rules = ["no_recorded_high_or_medium_fact"]

    return {
        "risk_tier": tier,
        "rules": rules,
        "gaps": gaps,
        "risk_tier_is_a_legal_finding": False,
        "note": NOTE,
    }
