"""Draft the assurance artefacts. Every artefact stays a draft."""

from __future__ import annotations

from typing import Any

from catalogue import (
    ATRS_CONTACT,
    ATRS_FIELDS,
    ATRS_GUIDANCE_URL,
    ATRS_REPOSITORY_URL,
    ATRS_RETRIEVED_ON,
    ATRS_SCOPE_URL,
    ATRS_TEMPLATE_FILE,
    ATRS_TEMPLATE_URL,
    ATRS_TEMPLATE_VERSION,
    DPIA_STEPS,
    DUAA_RETRIEVED_ON,
    DUAA_SECTION_80_URL,
    FCA_AI_PRACTICE_PUBLISHED,
    FCA_AI_PRACTICE_UPDATED,
    FCA_AI_PRACTICE_URL,
    GAP_TEXT,
    ICO_DPIA_RETRIEVED_ON,
    ICO_DPIA_URL,
    PLAYBOOK_COLLECTION_URL,
    PLAYBOOK_PRINCIPLES,
    PLAYBOOK_PUBLISHED,
    PLAYBOOK_RETRIEVED_ON,
    PLAYBOOK_URL,
    UK_GDPR_ARTICLE_22A_URL,
    UK_GDPR_ARTICLE_6_URL,
)


def draft_atrs(record: dict[str, Any]) -> dict[str, Any]:
    fields = [_draft_field(record, spec) for spec in ATRS_FIELDS]
    return {
        "document_status": "draft",
        "approved": False,
        "standard": "Algorithmic Transparency Recording Standard",
        "template_version": ATRS_TEMPLATE_VERSION,
        "template_retrieved_on": ATRS_RETRIEVED_ON,
        "template_url": ATRS_TEMPLATE_URL,
        "template_file": ATRS_TEMPLATE_FILE,
        "guidance_url": ATRS_GUIDANCE_URL,
        "scope_policy_url": ATRS_SCOPE_URL,
        "repository_url": ATRS_REPOSITORY_URL,
        "submission_status": "not_submitted",
        "may_be_emailed": False,
        "do_not_email": ATRS_CONTACT,
        "this_is_not_a_published_atrs_record": True,
        "single_model_block": True,
        "model_block_note": (
            "The v4.0 template says to duplicate the model sheet when a tool "
            "has more than one model. This draft has one model block."
        ),
        "applicability": _applicability(record),
        "fields": fields,
        "actions_taken": [],
    }


def draft_playbook(record: dict[str, Any]) -> dict[str, Any]:
    principles = []
    for principle in PLAYBOOK_PRINCIPLES:
        evidence = []
        for key in principle.evidence_keys:
            quote = _text(record, key)
            if quote is not None:
                evidence.append({"inventory_key": key, "quote": quote})
        principles.append(
            {
                "number": principle.number,
                "title": principle.title,
                "heading_variant": principle.heading_variant,
                "source_url": PLAYBOOK_URL,
                "coverage": "evidence_recorded" if evidence else "gap",
                "evidence": evidence,
                "assessment": "draft_mapping",
                "met": None,
                "approved": False,
            }
        )
    return {
        "document_status": "draft",
        "approved": False,
        "source_url": PLAYBOOK_URL,
        "collection_url": PLAYBOOK_COLLECTION_URL,
        "published": PLAYBOOK_PUBLISHED,
        "retrieved_on": PLAYBOOK_RETRIEVED_ON,
        "wording_note": (
            "Titles are the principles list on the HTML page. Principles 4, 5, "
            "and 9 also have a different section heading on that page. Both "
            "were read on 24 October 2026. This mapping does not score compliance."
        ),
        "principles": principles,
        "actions_taken": [],
    }


def draft_dpia(record: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for number, title, keys in DPIA_STEPS:
        facts = []
        for key in keys:
            quote = _text(record, key)
            if quote is not None:
                facts.append({"inventory_key": key, "quote": quote})
        steps.append(
            {
                "step": number,
                "title": title,
                "prompt": _dpia_prompt(number),
                "recorded_facts": facts,
                "answer_state": "facts_copied" if facts else "gap",
                "approved": False,
            }
        )
    high_residual = _high_residual(record)
    return {
        "document_status": "draft",
        "approved": False,
        "signed_off": False,
        "source_url": ICO_DPIA_URL,
        "retrieved_on": ICO_DPIA_RETRIEVED_ON,
        "what_this_is": (
            "A skeleton with the seven steps on the ICO's 'How do we do a DPIA?' "
            "page. It is not a DPIA and it is not DPO advice."
        ),
        "steps": steps,
        "sign_off": {
            "measures_approved_by": None,
            "residual_risks_approved_by": None,
            "dpo_advice": None,
            "dpo_advice_accepted_or_overruled_by": None,
            "consultation_responses_reviewed_by": None,
            "kept_under_review_by": None,
            "ico_prior_consultation": None,
        },
        "high_residual_risk_recorded_in_inventory": high_residual,
        "ico_note": (
            "The ICO says that if a high residual risk remains, you need to "
            "consult the ICO before you go ahead with the processing. This "
            "skeleton does not decide whether that threshold is met."
            if high_residual
            else
            "No inventory risk row records a High residual risk. That is not "
            "a finding that residual risk is low, and it is not a decision "
            "about prior consultation."
        ),
        "actions_taken": [],
    }


def screen_duaa(record: dict[str, Any]) -> dict[str, Any]:
    """Screen recorded facts against Articles 22A to 22D. Not a legal opinion."""
    flags: list[str] = ["article_22D_regulations_not_read"]
    regime = record.get("processing_regime", "unknown")
    result = _screen_shell(record, flags)

    if regime == "law_enforcement":
        result["screen_result"] = "different_regime"
        result["reading"] = (
            "DUAA 2025 section 80(3) substitutes Data Protection Act 2018 "
            "sections 50A to 50D for the law-enforcement automated-decision "
            "rules. Section 50A asks about an adverse legal effect or a "
            "similarly significant adverse effect. Article 22A does not use "
            "the word adverse. This screen does not run the law-enforcement test."
        )
        return result
    if regime == "intelligence_services":
        result["screen_result"] = "different_regime"
        result["reading"] = (
            "DUAA 2025 section 80(4) and (5) amend Data Protection Act 2018 "
            "sections 96 and 97. Section 96(4), as inserted, says a decision "
            "is based on entirely automated processing if the decision-making "
            "process does not include an opportunity for a human being to "
            "accept, reject or influence the decision. This screen does not "
            "apply that test."
        )
        result["verified_quote"] = {
            "source": "Data Protection Act 2018 section 96(4), as inserted by DUAA 2025 section 80(4)",
            "url": DUAA_SECTION_80_URL,
            "text": (
                "a decision is based on entirely automated processing if the "
                "decision-making process does not include an opportunity for a "
                "human being to accept, reject or influence the decision."
            ),
        }
        return result

    personal = record.get("processes_personal_data", "unknown")
    human = record.get("meaningful_human_involvement", "unknown")
    effect = record.get("significant_effect", "unknown")
    missing = [
        name
        for name, value in (
            ("processes_personal_data", personal),
            ("meaningful_human_involvement", human),
            ("significant_effect", effect),
        )
        if value in (None, "", "unknown")
    ]
    if missing:
        flags.append("insufficient_facts")
        result["missing_fields"] = missing

    if record.get("profiling") == "yes":
        flags.append("profiling_recorded_article_22A_2")
    if _basis_is_ea(record.get("lawful_basis", "")):
        flags.append("article_6_1_ea_recorded")
        if record.get("sector") == "public":
            flags.append("article_6_public_authority_limit_check")

    solely = human == "no"
    significant = effect in ("legal", "similarly_significant")
    if solely and significant and _basis_is_ea(record.get("lawful_basis", "")):
        flags.append("article_22B_4_restriction_may_apply")

    if solely and significant and record.get("special_category_data") == "yes":
        flags.append("special_category_and_solely_automated_significant_decision")
        second = (
            record.get("contract_or_authorised_by_law") == "yes"
            and record.get("article_9_2_g") == "yes"
        )
        consent = record.get("explicit_consent") == "yes"
        if consent:
            flags.append("explicit_consent_recorded_entirely_not_verified")
        if second:
            flags.append("article_22B_second_condition_recorded_not_verified")
        if not second:
            # Consent alone is not treated as meeting Article 22B(2). The
            # article also requires the decision to be based entirely on that
            # processing. This tool cannot see the processing.
            flags.append("article_22B_1_restriction_may_apply")
    elif solely and significant and record.get("special_category_data") == "unknown":
        flags.append("special_category_unknown")

    if solely and significant and personal != "no":
        safeguard_keys = (
            "safeguard_information",
            "safeguard_representations",
            "safeguard_human_intervention",
            "safeguard_contest",
        )
        if all(record.get(key) == "yes" for key in safeguard_keys):
            flags.append("article_22C_safeguards_recorded")
        else:
            flags.append("article_22C_safeguards_incomplete")

    if personal == "no" and record.get("special_category_data") == "yes":
        flags.append("personal_data_flags_conflict")
        result["screen_result"] = "insufficient_facts"
    elif personal == "no" and "insufficient_facts" not in flags:
        result["screen_result"] = "personal_data_not_recorded"
    elif "insufficient_facts" in flags and not _restriction(flags):
        result["screen_result"] = "insufficient_facts"
    elif _restriction(flags):
        result["screen_result"] = "restriction_may_apply"
    elif "article_22C_safeguards_incomplete" in flags:
        result["screen_result"] = "safeguards_incomplete"
    elif (
        "article_22B_second_condition_recorded_not_verified" in flags
        or "explicit_consent_recorded_entirely_not_verified" in flags
    ):
        result["screen_result"] = "human_must_confirm_recorded_conditions"
    elif solely and significant and "article_22C_safeguards_recorded" in flags:
        result["screen_result"] = "safeguards_recorded_not_a_clearance"
    elif human == "yes" and record.get("profiling") == "yes" and significant:
        result["screen_result"] = "profiling_needs_human_assessment"
    elif human == "yes" and effect == "none":
        result["screen_result"] = "significant_decision_not_recorded"
        if _text(record, "significant_effect_note"):
            flags.append("wider_process_not_screened")
    elif human == "yes":
        result["screen_result"] = "human_involvement_recorded"
        if _text(record, "significant_effect_note"):
            flags.append("wider_process_not_screened")
    elif not significant and personal == "yes":
        result["screen_result"] = "significant_decision_not_recorded"
    else:
        result["screen_result"] = "insufficient_facts"

    result["reading"] = _reading(result["screen_result"])
    return result


def draft_fca(record: dict[str, Any]) -> dict[str, Any]:
    environment = _environment(record)
    sector = record.get("sector")
    if sector == "fca_firm":
        audience = (
            "Structured from the FCA's good-practice examples on inventories "
            "of AI use cases, models, owners, access, and controls. The FCA "
            "has not published a prescribed inventory form. This is not a return."
        )
    else:
        audience = (
            "The FCA examples are about firms. This row is a field map for a "
            "record that is not an FCA-regulated firm. It is not a return."
        )
    return {
        "document_status": "draft",
        "approved": False,
        "scheme_status": "not_an_fca_prescribed_return",
        "source_url": FCA_AI_PRACTICE_URL,
        "source_published": FCA_AI_PRACTICE_PUBLISHED,
        "source_updated": FCA_AI_PRACTICE_UPDATED,
        "audience_note": audience,
        "use_case_name": _or_gap(record, "name"),
        "models": _or_gap(record, "model_name"),
        "experimental_or_production": environment,
        "owner": _or_gap(record, "team"),
        "accountable_role_recorded": _or_gap(record, "senior_responsible_owner_role"),
        "smf_mapping": GAP_TEXT,
        "systems_and_data": _or_gap(record, "system_input"),
        "controls": _or_gap(record, "human_review"),
        "third_party_arrangements": _or_gap(record, "third_party_name"),
        "information_sharing": _or_gap(record, "third_party_data_access_terms"),
        "human_oversight_recorded": record.get("meaningful_human_involvement", "unknown"),
        "agent_recorded_as_live": environment == "production_recorded",
        "live_flag_is_not_an_approval": True,
        "actions_taken": [],
    }


def _draft_field(record: dict[str, Any], spec: Any) -> dict[str, Any]:
    base = {
        "reference": spec.reference,
        "section": spec.section,
        "tier": spec.tier,
        "field": spec.name,
        "inventory_key": spec.inventory_key,
        "approved": False,
    }
    raw = _text(record, spec.inventory_key)
    if raw is None:
        return {**base, "answer": GAP_TEXT, "answer_state": "gap", "grounded_in": []}
    if spec.allowed and raw not in spec.allowed:
        return {
            **base,
            "answer": GAP_TEXT,
            "answer_state": "rejected_not_in_template_list",
            "grounded_in": [],
            "source_value": raw,
        }
    return {
        **base,
        "answer": raw,
        "answer_state": "draft_from_inventory",
        "grounded_in": [spec.inventory_key],
    }


def _applicability(record: dict[str, Any]) -> dict[str, Any]:
    sector = record.get("sector")
    common = {
        "mandatory_scope_decided_by_this_tool": False,
        "may_be_emailed_to_dsit": False,
        "scope_policy_url": ATRS_SCOPE_URL,
        "guidance_url": ATRS_GUIDANCE_URL,
    }
    if sector == "public":
        return {
            **common,
            "code": "public_sector_spoc_must_decide",
            "note": (
                "The guidance says the ATRS is mandatory for government "
                "departments and for arm's-length bodies which deliver public "
                "or frontline services, or directly interact with the public, "
                "and for in-scope tools. The scope and exemptions policy is a "
                "separate publication. This draft does not decide scope. A "
                "single point of contact, where the organisation has one, "
                "coordinates with the ATRS team."
            ),
        }
    if sector == "fca_firm":
        return {
            **common,
            "code": "not_a_public_sector_body",
            "note": (
                "The ATRS guidance is written for public sector organisations. "
                "A firm does not complete an ATRS record by holding this draft. "
                "The fields are filled so the shape is visible. Do not email "
                "the draft to the ATRS team."
            ),
        }
    return {
        **common,
        "code": "sector_not_public",
        "note": (
            "Sector is not recorded as a public body. Do not treat this draft "
            "as an ATRS submission."
        ),
    }


def _dpia_prompt(step: int) -> str:
    prompts = {
        1: "Record why a DPIA is being considered, and the stage of the work. The ICO says a DPIA should start early, before processing begins.",
        2: "Describe the nature, scope, context, and purposes of the processing, including what is collected, stored, deleted, and shared.",
        3: "Record who will be consulted, including individuals where that is possible, or why it is not. Consultation is not completed by this skeleton.",
        4: "Record the lawful basis the organisation is considering, why the processing is needed, and how data minimisation, quality, privacy information, rights, processors, and transfers will be handled. Do not invent a basis.",
        5: "Record risks to individuals. Likelihood and severity are for the organisation's assessment, not this skeleton.",
        6: "Record measures that would reduce those risks. Listing a measure here does not mean it is in place.",
        7: "The ICO's sign-off records who approved the measures, who approved residual risk, what the DPO advised, and who keeps the DPIA under review. Those names are left blank.",
    }
    return prompts[step]


def _high_residual(record: dict[str, Any]) -> bool:
    rows = record.get("risk_rows") or []
    return any(isinstance(row, dict) and row.get("residual_risk") == "High" for row in rows)


def _environment(record: dict[str, Any]) -> str:
    phase = record.get("atrs_phase")
    lifecycle = record.get("lifecycle_status")
    if phase == "Production" and lifecycle == "approved_for_limited_use":
        return "production_recorded"
    if phase in ("Private Beta", "Public Beta") or lifecycle == "pilot":
        return "experimental_or_pilot_recorded"
    if phase in ("Pre-deployment", "Retired") or lifecycle in (
        "proposed",
        "in_design",
        "assurance_drafted",
        "awaiting_governance_owner",
        "suspended",
        "retired",
    ):
        return "not_production"
    return "not_recorded"


def _basis_is_ea(basis: str) -> bool:
    text = basis.lower().replace(" ", "")
    return "6(1)(ea)" in text or "6(1)(ea)".replace(" ", "") in text or "(ea)" in text


def _restriction(flags: list[str]) -> bool:
    return (
        "article_22B_1_restriction_may_apply" in flags
        or "article_22B_4_restriction_may_apply" in flags
    )


def _reading(screen_result: str) -> str:
    readings = {
        "personal_data_not_recorded": (
            "The inventory records that this use does not process personal "
            "data. Articles 22B and 22C were read as applying where a "
            "significant decision is based on personal data and solely on "
            "automated processing. A person must confirm the 'no personal "
            "data' record. This is not a finding."
        ),
        "insufficient_facts": (
            "Article 22A uses two tests: whether there is meaningful human "
            "involvement, and whether the decision has a legal effect or a "
            "similarly significant effect. One of those facts is not recorded. "
            "No screen result is given beyond that gap."
        ),
        "restriction_may_apply": (
            "The recorded facts engage Article 22B(1) or Article 22B(4), or "
            "both. Read section 80. This screen does not decide that a "
            "condition is met and does not authorise the decision."
        ),
        "safeguards_incomplete": (
            "Article 22C(2) describes information, representations, human "
            "intervention, and contesting the decision. At least one is not "
            "recorded as in place. This is not a finding that the safeguard "
            "is absent in the real process."
        ),
        "profiling_needs_human_assessment": (
            "A person is recorded as involved, and profiling is also recorded. "
            "Article 22A(2) says that, when considering meaningful human "
            "involvement, a person must consider the extent to which the "
            "decision is reached by means of profiling. This tool does not "
            "make that judgement."
        ),
        "human_involvement_recorded": (
            "Meaningful human involvement is recorded. That is not a finding "
            "that the involvement meets Article 22A."
        ),
        "significant_decision_not_recorded": (
            "The inventory does not record a legal effect or a similarly "
            "significant effect for this agent's own output. The wider process "
            "may still have that effect. This screen does not cover a decision "
            "a person makes after reading the draft."
        ),
        "human_must_confirm_recorded_conditions": (
            "Some Article 22B facts are recorded. Article 22B(2) also requires "
            "the decision to be based entirely on the consented processing, and "
            "Article 22B(3) requires both the contract-or-law limb and Article "
            "9(2)(g). This tool does not confirm either condition."
        ),
        "safeguards_recorded_not_a_clearance": (
            "The four Article 22C(2) measures are recorded as present. Article "
            "22D allows regulations to add to those measures. This screen has "
            "not read any regulations and does not clear the processing."
        ),
    }
    return readings.get(screen_result, "No completed reading.")


def _screen_shell(record: dict[str, Any], flags: list[str]) -> dict[str, Any]:
    return {
        "document_status": "draft",
        "approved": False,
        "determination": "not_a_legal_determination",
        "lawful": None,
        "screen_result": None,
        "flags": flags,
        "missing_fields": [],
        "commencement_note": (
            "Data (Use and Access) Act 2025 section 80 was in force at Royal "
            "Assent for specified purposes (section 142(1)(2)(h)). It came "
            "into force on 5 February 2026 in so far as not already in force, "
            "by S.I. 2026/82, regulation 2(j), with regulation 5. This tool "
            "has not interpreted regulation 5."
        ),
        "sources": [
            {"name": "DUAA 2025 section 80", "url": DUAA_SECTION_80_URL},
            {"name": "UK GDPR Article 22A", "url": UK_GDPR_ARTICLE_22A_URL},
            {"name": "UK GDPR Article 6", "url": UK_GDPR_ARTICLE_6_URL},
        ],
        "retrieved_on": DUAA_RETRIEVED_ON,
        "inventory_id": record.get("inventory_id"),
        "actions_taken": [],
    }


def _text(record: dict[str, Any], key: str) -> str | None:
    if key not in record:
        return None
    value = record[key]
    if value is None:
        return None
    text = value if isinstance(value, str) else str(value)
    if not text.strip():
        return None
    return text.strip()


def _or_gap(record: dict[str, Any], key: str) -> str:
    return _text(record, key) or GAP_TEXT
