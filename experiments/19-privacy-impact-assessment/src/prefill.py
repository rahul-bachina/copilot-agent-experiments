"""Copy facts from an Experiment 03 inventory or a permissions manifest.

Copied text is marked as copied. Screening answers are not inferred. A
manifest that disables a regulated decision is not treated as meaningful
human involvement under Article 22A.
"""

from __future__ import annotations

from copy import deepcopy

AUTOMATED_KEYS = (
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
)

DESCRIPTION_FROM_INVENTORY = (
    ("nature", "operational_process"),
    ("scope", "frequency_and_scale"),
    ("context", "public_description"),
    ("purposes", "one_sentence_description"),
    ("legitimate_interest", "benefits"),
)

NARRATIVE_FROM_INVENTORY = (
    ("necessity", "purpose_helped", "benefits"),
    ("necessity", "other_reasonable_way", "alternatives_considered"),
    ("consultation", "individuals_reason_if_not", "appeals_and_review"),
)


def _blank(value: object) -> bool:
    return value is None or value == "" or value == "unknown"


def apply_inventory(brief: dict, inventory: dict) -> tuple[dict, list[dict]]:
    """Fill empty fields from an inventory record. Do not overwrite a real answer."""

    updated = deepcopy(brief)
    notes: list[dict] = []
    if not isinstance(inventory, dict):
        return updated, notes

    if _blank(updated.get("project_name")) and _text(inventory, "name"):
        updated["project_name"] = _text(inventory, "name")
        notes.append({"field": "project_name", "from": "inventory.name"})
    if _blank(updated.get("organisation_name")) and _text(inventory, "organisation_name"):
        updated["organisation_name"] = _text(inventory, "organisation_name")
        notes.append({"field": "organisation_name", "from": "inventory.organisation_name"})

    description = dict(updated.get("description") or {})
    for dest, source in DESCRIPTION_FROM_INVENTORY:
        if _blank(description.get(dest)) and _text(inventory, source):
            description[dest] = _text(inventory, source)
            notes.append({"field": f"description.{dest}", "from": f"inventory.{source}"})
    updated["description"] = description

    for section, dest, source in NARRATIVE_FROM_INVENTORY:
        block = dict(updated.get(section) or {})
        if _blank(block.get(dest)) and _text(inventory, source):
            block[dest] = _text(inventory, source)
            notes.append({"field": f"{section}.{dest}", "from": f"inventory.{source}"})
        updated[section] = block

    necessity = dict(updated.get("necessity") or {})
    if _blank(necessity.get("lawful_basis_considered")) and _text(inventory, "lawful_basis"):
        necessity["lawful_basis_considered"] = _text(inventory, "lawful_basis")
        notes.append({"field": "necessity.lawful_basis_considered", "from": "inventory.lawful_basis"})
    updated["necessity"] = necessity

    automated = dict(updated.get("automated_decision") or {})
    for key in AUTOMATED_KEYS:
        if _blank(automated.get(key)) and not _blank(inventory.get(key)):
            automated[key] = inventory[key]
            notes.append({"field": f"automated_decision.{key}", "from": f"inventory.{key}"})
    updated["automated_decision"] = automated

    if not updated.get("risks") and isinstance(inventory.get("risk_rows"), list):
        copied = []
        for row in inventory["risk_rows"]:
            if not isinstance(row, dict):
                continue
            copied.append(
                {
                    "id": row.get("id") or "inventory-risk",
                    "description": row.get("risk") or "",
                    "source": "Copied from an Experiment 03 inventory risk row. Not re-scored.",
                    "likelihood": row.get("likelihood") if row.get("likelihood") in {"Low", "Medium", "High"} else "unknown",
                    "severity": row.get("impact") if row.get("impact") in {"Low", "Medium", "High"} else "unknown",
                    "harm_types": [],
                    "mitigation": "",
                    "effect_of_mitigation": "unknown",
                    "residual": row.get("residual_risk") if row.get("residual_risk") in {"Low", "Medium", "High"} else "unknown",
                    "prefilled_from": "inventory.risk_rows",
                }
            )
        if copied:
            updated["risks"] = copied
            notes.append({"field": "risks", "from": "inventory.risk_rows"})
            if _blank(updated.get("residual_risk_overall")):
                if any(item["residual"] == "High" for item in copied):
                    updated["residual_risk_overall"] = "High"
                    notes.append({"field": "residual_risk_overall", "from": "inventory.risk_rows"})

    return updated, notes


def apply_manifest(brief: dict, manifest: dict) -> tuple[dict, dict]:
    """Copy identity and a recorded basis. Do not infer screening or Article 22A."""

    updated = deepcopy(brief)
    notes: list[dict] = []
    section = {
        "present": isinstance(manifest, dict),
        "autonomy_level_recorded": None,
        "regulated_decision_enabled": None,
        "meaningful_human_involvement_inferred": False,
        "note": (
            "A manifest that disables a regulated decision is not a finding of "
            "meaningful human involvement under Article 22A(1)(a). Screening "
            "answers are not copied from a manifest."
        ),
    }
    if not isinstance(manifest, dict):
        return updated, {"copied": notes, "agent_section": section}

    agent = manifest.get("agent") if isinstance(manifest.get("agent"), dict) else {}
    if _blank(updated.get("project_name")) and _text(agent, "name"):
        updated["project_name"] = _text(agent, "name")
        notes.append({"field": "project_name", "from": "manifest.agent.name"})
    description = dict(updated.get("description") or {})
    if _blank(description.get("purposes")) and _text(agent, "description"):
        description["purposes"] = _text(agent, "description")
        notes.append({"field": "description.purposes", "from": "manifest.agent.description"})
    reads = manifest.get("data_access") if isinstance(manifest.get("data_access"), dict) else {}
    read_rows = reads.get("reads") if isinstance(reads.get("reads"), list) else []
    resources = [
        row.get("resource")
        for row in read_rows
        if isinstance(row, dict) and isinstance(row.get("resource"), str)
    ]
    if _blank(description.get("scope")) and resources:
        description["scope"] = "Manifest reads: " + "; ".join(resources)
        notes.append({"field": "description.scope", "from": "manifest.data_access.reads"})
    updated["description"] = description

    autonomy = manifest.get("autonomy") if isinstance(manifest.get("autonomy"), dict) else {}
    level = autonomy.get("level")
    if level in {"A0", "A1", "A2"}:
        section["autonomy_level_recorded"] = level
    high = manifest.get("high_risk_actions") if isinstance(manifest.get("high_risk_actions"), dict) else {}
    regulated = high.get("regulated_decision") if isinstance(high.get("regulated_decision"), dict) else {}
    if "enabled" in regulated:
        section["regulated_decision_enabled"] = bool(regulated.get("enabled"))

    uk = manifest.get("uk_gdpr") if isinstance(manifest.get("uk_gdpr"), dict) else {}
    basis = uk.get("lawful_basis") if isinstance(uk.get("lawful_basis"), dict) else {}
    primary = basis.get("primary")
    necessity = dict(updated.get("necessity") or {})
    if (
        _blank(necessity.get("lawful_basis_considered"))
        and isinstance(primary, str)
        and primary.strip()
        and primary.strip().lower() != "not asserted"
    ):
        necessity["lawful_basis_considered"] = primary.strip()
        notes.append({"field": "necessity.lawful_basis_considered", "from": "manifest.uk_gdpr.lawful_basis.primary"})
    updated["necessity"] = necessity
    return updated, {"copied": notes, "agent_section": section}


def _text(row: dict, key: str) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None
