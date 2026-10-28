"""Screen recorded facts against UK GDPR Articles 22A to 22D.

Not a legal determination. ``lawful`` stays null. Law-enforcement and
intelligence-services processing are named and are not run through Article 22A.
"""

from __future__ import annotations

from datetime import date, datetime

from sources import (
    ARTICLE_22_FULL_COMMENCEMENT,
    ARTICLE_22A_1,
    COMMENCEMENT_NOTE,
    DUAA_SECTION_80_URL,
    SI_2026_82_REG_5_URL,
    UK_GDPR_ARTICLE_22A_URL,
    UK_GDPR_ARTICLE_22B_URL,
    UK_GDPR_ARTICLE_22C_URL,
    UK_GDPR_ARTICLE_22D_URL,
)

TRI = ("yes", "no", "unknown")
EFFECTS = ("legal", "similarly_significant", "none", "unknown")
REGIMES = ("uk_gdpr", "law_enforcement", "intelligence_services", "unknown")


def _tri(facts: dict, key: str) -> str:
    value = facts.get(key, "unknown")
    if value in (None, ""):
        return "unknown"
    if value in TRI or value in EFFECTS or value in REGIMES:
        return value
    return "unknown"


def _basis_is_ea(basis: str) -> bool:
    compact = basis.lower().replace(" ", "")
    return "6(1)(ea)" in compact


def _before_commencement(facts: dict) -> bool:
    if facts.get("decision_taken_before_5_february_2026") == "yes":
        return True
    raw = facts.get("decision_date")
    if not isinstance(raw, str) or not raw:
        return False
    try:
        taken = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return False
    return taken < ARTICLE_22_FULL_COMMENCEMENT


def screen_automated(facts: dict | None, *, as_of: date) -> dict:
    block = facts if isinstance(facts, dict) else {}
    flags = ["article_22D_regulations_not_read"]
    if as_of < ARTICLE_22_FULL_COMMENCEMENT:
        flags.append("as_of_before_full_commencement")
    if _before_commencement(block):
        flags.append("saving_provision_may_apply")
    elif block.get("decision_taken_before_5_february_2026", "unknown") != "no":
        flags.append("decision_date_not_recorded")

    regime = _tri(block, "processing_regime")
    if regime not in REGIMES:
        regime = "unknown"
    result = _shell(flags)

    if regime == "law_enforcement":
        result["screen_result"] = "different_regime"
        result["reading"] = (
            "Data (Use and Access) Act 2025 section 80(3) substitutes Data "
            "Protection Act 2018 sections 50A to 50D for the law-enforcement "
            "rules. Section 50A asks about an adverse legal effect or a similarly "
            "significant adverse effect. Article 22A does not use the word adverse. "
            "This screen does not run the law-enforcement test."
        )
        return result
    if regime == "intelligence_services":
        result["screen_result"] = "different_regime"
        result["reading"] = (
            "Section 80(4) inserts Data Protection Act 2018 section 96(4). The "
            "inserted words say a decision is based on entirely automated processing "
            "if the decision-making process does not include an opportunity for a "
            "human being to accept, reject or influence the decision. This screen "
            "does not apply that test."
        )
        return result

    if "saving_provision_may_apply" in flags:
        result["screen_result"] = "saving_provision_may_apply"
        result["reading"] = (
            "The brief records a decision date before 5 February 2026, or says "
            "the decision was taken before that day. S.I. 2026/82 regulation 5 "
            "is a saving for certain earlier decisions. This tool has not "
            "interpreted regulation 5 and does not apply Articles 22A to 22C to "
            "that decision."
        )
        result["recorded_facts"] = _recorded(block)
        return result

    personal = _tri(block, "processes_personal_data")
    human = _tri(block, "meaningful_human_involvement")
    effect = _tri(block, "significant_effect")
    if effect not in EFFECTS:
        effect = "unknown"
        flags.append("significant_effect_rejected")
    missing = [
        name
        for name, value in (
            ("processes_personal_data", personal),
            ("meaningful_human_involvement", human),
            ("significant_effect", effect),
        )
        if value == "unknown"
    ]
    if missing:
        flags.append("insufficient_facts")
        result["missing_fields"] = missing

    if block.get("profiling") == "yes":
        flags.append("profiling_recorded_article_22A_2")
    basis = block.get("lawful_basis") if isinstance(block.get("lawful_basis"), str) else ""
    if _basis_is_ea(basis):
        flags.append("article_6_1_ea_recorded")

    solely = human == "no"
    significant = effect in ("legal", "similarly_significant")
    special = _tri(block, "special_category_data")

    if solely and significant and _basis_is_ea(basis):
        flags.append("article_22B_4_restriction_may_apply")

    if solely and significant and special == "yes":
        flags.append("special_category_and_solely_automated_significant_decision")
        second = (
            _tri(block, "contract_or_authorised_by_law") == "yes"
            and _tri(block, "article_9_2_g") == "yes"
        )
        if _tri(block, "explicit_consent") == "yes":
            flags.append("explicit_consent_recorded_not_verified")
        if second:
            flags.append("article_22B_second_condition_recorded_not_verified")
        else:
            flags.append("article_22B_1_restriction_may_apply")
    elif solely and significant and special == "unknown":
        flags.append("special_category_unknown")

    safeguard_keys = (
        "safeguard_information",
        "safeguard_representations",
        "safeguard_human_intervention",
        "safeguard_contest",
    )
    if solely and significant and personal != "no":
        if all(_tri(block, key) == "yes" for key in safeguard_keys):
            flags.append("article_22C_safeguards_recorded")
        else:
            flags.append("article_22C_safeguards_incomplete")

    result["flags"] = flags
    result["recorded_facts"] = _recorded(block)
    result["screen_result"] = _code(flags, personal, human, effect, solely, significant)
    result["reading"] = _reading(result["screen_result"])
    return result


def _recorded(block: dict) -> dict:
    keys = (
        "processing_regime",
        "processes_personal_data",
        "meaningful_human_involvement",
        "significant_effect",
        "profiling",
        "special_category_data",
        "lawful_basis",
        "explicit_consent",
        "contract_or_authorised_by_law",
        "article_9_2_g",
        "safeguard_information",
        "safeguard_representations",
        "safeguard_human_intervention",
        "safeguard_contest",
        "decision_taken_before_5_february_2026",
        "decision_date",
    )
    recorded = {}
    for key in keys:
        if key in block and block[key] not in (None, ""):
            recorded[key] = block[key]
    return recorded


def _restriction(flags: list[str]) -> bool:
    return (
        "article_22B_1_restriction_may_apply" in flags
        or "article_22B_4_restriction_may_apply" in flags
    )


def _code(flags: list[str], personal: str, human: str, effect: str, solely: bool, significant: bool) -> str:
    if personal == "no" and "special_category_and_solely_automated_significant_decision" in flags:
        return "insufficient_facts"
    if personal == "no" and "insufficient_facts" not in flags:
        return "personal_data_not_recorded"
    if "insufficient_facts" in flags and not _restriction(flags):
        return "insufficient_facts"
    if _restriction(flags):
        return "restriction_may_apply"
    if "article_22C_safeguards_incomplete" in flags:
        return "safeguards_incomplete"
    if (
        "article_22B_second_condition_recorded_not_verified" in flags
        or "explicit_consent_recorded_not_verified" in flags
    ):
        return "human_must_confirm_recorded_conditions"
    if solely and significant and "article_22C_safeguards_recorded" in flags:
        return "safeguards_recorded_not_a_clearance"
    if human == "yes" and "profiling_recorded_article_22A_2" in flags and significant:
        return "profiling_needs_human_assessment"
    if human == "yes" and effect == "none":
        return "significant_decision_not_recorded"
    if human == "yes":
        return "human_involvement_recorded"
    if not significant and personal == "yes":
        return "significant_decision_not_recorded"
    return "insufficient_facts"


def _reading(code: str) -> str:
    readings = {
        "personal_data_not_recorded": (
            "The brief records that this processing does not use personal data. "
            "Articles 22B and 22C were read as applying where a significant "
            "decision is based on personal data and solely on automated processing. "
            "A person must confirm that record. This is not a finding."
        ),
        "insufficient_facts": (
            "Article 22A uses two tests: meaningful human involvement, and a "
            "legal or similarly significant effect. " + ARTICLE_22A_1 + " "
            "One of the facts needed to apply that text is not recorded."
        ),
        "restriction_may_apply": (
            "The recorded facts engage Article 22B(1) or Article 22B(4), or both. "
            "Article 22B(4) refers to processing that relies on Article 6(1)(ea). "
            "Article 6 was not re-opened for this experiment. This screen does not "
            "decide that a condition is met and does not authorise the decision."
        ),
        "safeguards_incomplete": (
            "Article 22C(1) applies where a significant decision is based entirely "
            "or partly on personal data and solely on automated processing. "
            "Article 22C(2) describes information, representations, human "
            "intervention, and contesting the decision. At least one is not "
            "recorded as in place. This is not a finding that the safeguard is "
            "absent in the real process."
        ),
        "profiling_needs_human_assessment": (
            "A person is recorded as involved, and profiling is also recorded. "
            "Article 22A(2) says that, when considering meaningful human "
            "involvement, a person must consider the extent to which the decision "
            "is reached by means of profiling. This tool does not make that judgement."
        ),
        "human_involvement_recorded": (
            "Meaningful human involvement is recorded. That is not a finding that "
            "the involvement meets Article 22A(1)(a)."
        ),
        "significant_decision_not_recorded": (
            "The brief does not record a legal or similarly significant effect "
            "for this processing. The wider process may still have that effect. "
            "This screen does not cover a decision a person makes after reading "
            "the draft."
        ),
        "human_must_confirm_recorded_conditions": (
            "Some Article 22B facts are recorded. Article 22B(2) requires the "
            "decision to be based entirely on the consented processing. Article "
            "22B(3) requires both the contract-or-law limb and Article 9(2)(g). "
            "This tool does not confirm either condition."
        ),
        "safeguards_recorded_not_a_clearance": (
            "The four Article 22C(2) measures are recorded as present. Article "
            "22D allows regulations to add to those measures. No such regulations "
            "were read. This does not clear the processing."
        ),
    }
    return readings.get(code, "No completed reading.")


def _shell(flags: list[str]) -> dict:
    return {
        "document_status": "draft",
        "approved": False,
        "determination": "not_a_legal_determination",
        "lawful": None,
        "screen_result": None,
        "flags": list(flags),
        "missing_fields": [],
        "recorded_facts": {},
        "commencement_note": COMMENCEMENT_NOTE,
        "sources": [
            {"name": "DUAA 2025 section 80", "url": DUAA_SECTION_80_URL},
            {"name": "UK GDPR Article 22A", "url": UK_GDPR_ARTICLE_22A_URL},
            {"name": "UK GDPR Article 22B", "url": UK_GDPR_ARTICLE_22B_URL},
            {"name": "UK GDPR Article 22C", "url": UK_GDPR_ARTICLE_22C_URL},
            {"name": "UK GDPR Article 22D", "url": UK_GDPR_ARTICLE_22D_URL},
            {"name": "S.I. 2026/82 regulation 5", "url": SI_2026_82_REG_5_URL},
        ],
        "actions_taken": [],
    }
