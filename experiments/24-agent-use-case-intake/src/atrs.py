"""Whether the opened ATRS guidance points at a record.

Mandatory scope is not decided. The scope and exemptions policy was not opened.
"""

from __future__ import annotations

from sources import ATRS_GUIDANCE_URL, ATRS_MANDATORY_ORGS, ATRS_MANDATORY_TOOLS, ATRS_RECOMMENDED, ATRS_SCOPE_URL

MANDATORY_ORG_KINDS = frozenset({"government_department", "alb_public_or_frontline"})
WIDER_PUBLIC_KINDS = frozenset(
    {"alb_other", "local_authority", "police", "wider_public_sector"}
)
OUTSIDE_KINDS = frozenset({"fca_firm", "private"})
KNOWN_KINDS = MANDATORY_ORG_KINDS | WIDER_PUBLIC_KINDS | OUTSIDE_KINDS


def _yn(value: object) -> str:
    if value in {"yes", "no", "unknown"}:
        return value
    return "missing"


def atrs_position(kind: object, influence: object, interaction: object) -> dict:
    """Return a draft position. ``scope_decided_by_this_tool`` stays false."""

    influence_value = _yn(influence)
    interaction_value = _yn(interaction)
    tool_yes = influence_value == "yes" or interaction_value == "yes"
    tool_no = influence_value == "no" and interaction_value == "no"
    base = {
        "atrs_scope_decided_by_this_tool": False,
        "may_be_emailed": False,
        "guidance_url": ATRS_GUIDANCE_URL,
        "scope_policy_url": ATRS_SCOPE_URL,
        "scope_policy_opened": False,
        "quotes": {
            "mandatory_organisations": ATRS_MANDATORY_ORGS,
            "mandatory_tools": ATRS_MANDATORY_TOOLS,
            "recommended_wider_public_sector": ATRS_RECOMMENDED,
        },
    }
    if kind not in KNOWN_KINDS:
        return {
            **base,
            "atrs_likely_needed": None,
            "atrs_basis": "insufficient_facts",
            "kind_not_recognised": kind not in {None, "", "unknown"},
            "note": (
                "The organisation kind is not one of the recorded values. "
                "No ATRS position is given. Absence of an answer is not a no."
            ),
        }
    if kind in OUTSIDE_KINDS:
        return {
            **base,
            "atrs_likely_needed": False,
            "atrs_basis": "not_indicated_outside_public_sector",
            "kind_not_recognised": False,
            "note": (
                "The guidance opened on 30 October 2026 is written for public "
                "sector organisations. This draft does not recommend an ATRS "
                "record for a private organisation or an FCA-regulated firm. "
                "That is not advice about any other record the firm keeps."
            ),
        }
    if kind in WIDER_PUBLIC_KINDS:
        return {
            **base,
            "atrs_likely_needed": True,
            "atrs_basis": "recommended_for_the_wider_public_sector",
            "kind_not_recognised": False,
            "note": (
                "The guidance says the standard is recommended across the public "
                "sector, and that records from local government, police forces, "
                "and other broader public sector organisations have been welcomed. "
                "It does not say this organisation is a government department or "
                "an ALB in the mandatory organisation sentence. This draft does "
                "not decide mandatory scope."
            ),
        }
    if tool_yes:
        return {
            **base,
            "atrs_likely_needed": True,
            "atrs_basis": "recorded_facts_match_the_guidance_tests",
            "kind_not_recognised": False,
            "note": (
                "The recorded organisation kind is in the mandatory organisation "
                "sentence, and a recorded answer matches the tool sentence "
                "(significant influence on a decision-making process with public "
                "effect, or direct interaction with the general public). A single "
                "point of contact, where the organisation has one, still decides. "
                "This draft does not."
            ),
        }
    if tool_no:
        return {
            **base,
            "atrs_likely_needed": None,
            "atrs_basis": "tool_tests_recorded_as_not_met",
            "kind_not_recognised": False,
            "note": (
                "The organisation kind matches the mandatory organisation sentence, "
                "and both tool answers were recorded as no. This draft does not "
                "turn that into a finding that no record is needed. The scope "
                "and exemptions policy was not opened."
            ),
        }
    return {
        **base,
        "atrs_likely_needed": None,
        "atrs_basis": "insufficient_facts",
        "kind_not_recognised": False,
        "note": (
            "The organisation kind matches the mandatory organisation sentence, "
            "and at least one tool answer is missing or unknown. No likely-needed "
            "flag is set. Absence of an answer is not a no."
        ),
    }
