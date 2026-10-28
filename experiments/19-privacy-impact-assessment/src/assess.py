#!/usr/bin/env python3
"""Draft a data protection impact assessment. Do not approve it.

The same brief and the same as-of date produce the same JSON. Free text is
passed through Experiment 08 before it is copied into the draft. The draft
is not anonymised, not signed off, and not sent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from automated import screen_automated
    from injection import neutralise, scan_fields
    from prefill import apply_inventory, apply_manifest
    from screening import screen
    from sources import (
        ARTICLE_35_2,
        ARTICLE_35_7,
        ARTICLE_36_1,
        COMMISSION_NOTE,
        GAP_TEXT,
        HARM_TYPES,
        ICO_CONSULT_URL,
        ICO_HOW_URL,
        ICO_RESIDUAL_NOTE,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        UK_GDPR_ARTICLE_35_URL,
        UK_GDPR_ARTICLE_36_URL,
    )
else:
    from .automated import screen_automated
    from .injection import neutralise, scan_fields
    from .prefill import apply_inventory, apply_manifest
    from .screening import screen
    from .sources import (
        ARTICLE_35_2,
        ARTICLE_35_7,
        ARTICLE_36_1,
        COMMISSION_NOTE,
        GAP_TEXT,
        HARM_TYPES,
        ICO_CONSULT_URL,
        ICO_HOW_URL,
        ICO_RESIDUAL_NOTE,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        UK_GDPR_ARTICLE_35_URL,
        UK_GDPR_ARTICLE_36_URL,
    )

CALLER = "exp-19-privacy-impact-assessment"
CATALOGUE_ID = "L006"
LABEL = "DRAFT FOR PRIVACY OFFICER REVIEW"

STRIPPED_KEYS = (
    "approved",
    "rejected",
    "signed_off",
    "residual_risk_accepted",
    "prior_consultation_sent",
    "dpia_required",
    "article_36_consultation_required",
    "lawful",
    "actions_taken",
    "output_is_anonymised",
    "agent_may_release",
)

DESCRIPTION_FIELDS = ("nature", "scope", "context", "purposes", "legitimate_interest")
NECESSITY_FIELDS = (
    "purpose_helped",
    "other_reasonable_way",
    "lawful_basis_considered",
    "function_creep",
    "data_quality",
    "data_minimisation",
    "privacy_information",
    "individual_rights",
    "processor_measures",
    "transfer_safeguards",
)
LEVELS = {"Low", "Medium", "High", "unknown"}
EFFECTS = {"eliminated", "reduced", "accepted", "unknown"}

_propose = None


class NotSynthetic(ValueError):
    """This starter reads synthetic project briefs only."""


class AssessmentForbidden(RuntimeError):
    """The assistant has no approve, reject, sign-off, accept, or send path."""


def approve_assessment(*_args, **_kwargs) -> None:
    raise AssessmentForbidden("the agent does not approve a DPIA")


def reject_assessment(*_args, **_kwargs) -> None:
    raise AssessmentForbidden("the agent does not reject a DPIA")


def sign_off_assessment(*_args, **_kwargs) -> None:
    raise AssessmentForbidden("the agent does not sign off a DPIA")


def accept_residual_risk(*_args, **_kwargs) -> None:
    raise AssessmentForbidden("the agent does not accept residual risk")


def send_prior_consultation(*_args, **_kwargs) -> None:
    raise AssessmentForbidden("the agent does not send a prior consultation")


def write_production_record(*_args, **_kwargs) -> None:
    raise AssessmentForbidden("the agent does not write a production record")


def _load_propose():
    gateway_src = (
        Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    )
    if not gateway_src.is_dir():
        raise RuntimeError(
            "Experiment 08 is required at experiments/08-uk-pii-redaction-gateway. "
            "This assistant does not carry its own copy."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _gateway():
    global _propose
    if _propose is None:
        _propose = _load_propose()
    return _propose


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _strip(brief: dict) -> tuple[dict, list[str]]:
    cleaned = deepcopy(brief)
    removed = [key for key in STRIPPED_KEYS if key in cleaned]
    for key in removed:
        cleaned.pop(key, None)
    return cleaned, removed


def _strings(brief: dict) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    def walk(value: object, prefix: str) -> None:
        if isinstance(value, str):
            found.append((prefix, value))
        elif isinstance(value, dict):
            for key, item in value.items():
                walk(item, f"{prefix}.{key}" if prefix else str(key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{prefix}[{index}]")

    for key in ("project_name", "organisation_name", "description", "necessity", "consultation", "risks"):
        if key in brief:
            walk(brief[key], key)
    return found


def _neutralise_brief(brief: dict) -> dict:
    updated = deepcopy(brief)

    def walk(value: object) -> object:
        if isinstance(value, str):
            return neutralise(value)
        if isinstance(value, dict):
            return {key: walk(item) for key, item in value.items()}
        if isinstance(value, list):
            return [walk(item) for item in value]
        return value

    for key in ("project_name", "organisation_name", "description", "necessity", "consultation", "risks"):
        if key in updated:
            updated[key] = walk(updated[key])
    return updated


def _redact_text(text: str) -> tuple[str, dict]:
    proposal = _gateway()(
        text,
        caller=CALLER,
        apply_model_suggestions=False,
        reversible=False,
    )
    redacted = proposal["redacted_text"]
    banner, _, body = redacted.partition("\n")
    if not banner.startswith("[REDACTION PROPOSAL"):
        body = redacted
    summary = {
        "gateway": proposal["gateway"],
        "catalogue_id": proposal["catalogue_id"],
        "output_is_anonymised": False,
        "agent_may_release": False,
        "finding_count": len(proposal["audit_log"]["findings"]),
        "entity_types": sorted({row["entity_type"] for row in proposal["audit_log"]["findings"]}),
        "input_sha256": proposal["audit_log"]["input_sha256"],
        "rules_pinned_on": proposal["audit_log"]["rules_pinned_on"],
        "raw_values_logged": False,
    }
    if summary["output_is_anonymised"] or proposal["anonymisation"]["output_is_anonymised"]:
        raise AssessmentForbidden("Experiment 08 must not be treated as anonymisation")
    return body, summary


def _redact_brief(brief: dict) -> tuple[dict, dict]:
    updated = deepcopy(brief)
    summaries = []

    def apply(container: dict, key: str, path: str) -> None:
        value = container.get(key)
        if not isinstance(value, str) or not value:
            return
        body, summary = _redact_text(value)
        summary["field"] = path
        container[key] = body
        summaries.append(summary)

    description = dict(updated.get("description") or {})
    for key in DESCRIPTION_FIELDS:
        apply(description, key, f"description.{key}")
    updated["description"] = description

    necessity = dict(updated.get("necessity") or {})
    for key in NECESSITY_FIELDS:
        apply(necessity, key, f"necessity.{key}")
    updated["necessity"] = necessity

    consultation = dict(updated.get("consultation") or {})
    for key in ("individuals_reason_if_not", "dpo_advice_recorded"):
        apply(consultation, key, f"consultation.{key}")
    updated["consultation"] = consultation

    risks = []
    for index, row in enumerate(updated.get("risks") or []):
        if not isinstance(row, dict):
            continue
        copied = dict(row)
        for key in ("description", "source", "mitigation"):
            apply(copied, key, f"risks[{index}].{key}")
        risks.append(copied)
    updated["risks"] = risks

    project_name = updated.get("project_name")
    if isinstance(project_name, str) and project_name:
        body, summary = _redact_text(project_name)
        summary["field"] = "project_name"
        updated["project_name"] = body
        summaries.append(summary)

    return updated, {
        "called": True,
        "experiment": "08-uk-pii-redaction-gateway",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "reversible": False,
        "model_suggestions_applied": False,
        "fields": summaries,
    }


def _field(block: dict, key: str, *, prefilled: set[str], path: str) -> dict:
    value = block.get(key)
    if not isinstance(value, str) or not value.strip():
        return {"name": key, "text": GAP_TEXT, "state": "gap", "prefilled_from": None}
    state = "copied_from_linked_record" if path in prefilled else "copied_from_brief"
    return {"name": key, "text": value.strip(), "state": state, "prefilled_from": path if path in prefilled else None}


def _section(number: int, title: str, article: str, fields: list[dict]) -> dict:
    return {
        "step": number,
        "title": title,
        "article": article,
        "ico_step_url": ICO_HOW_URL,
        "fields": fields,
        "approved": False,
    }


def _harms(raw: object) -> list[dict]:
    if not isinstance(raw, list):
        return []
    rows = []
    for item in raw:
        if not isinstance(item, str):
            continue
        rows.append(
            {
                "text": item,
                "on_ico_step_5_list": item in HARM_TYPES,
            }
        )
    return rows


def _risk_rows(rows: object) -> list[dict]:
    if not isinstance(rows, list):
        return []
    drafted = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        likelihood = row.get("likelihood") if row.get("likelihood") in LEVELS else "unknown"
        severity = row.get("severity") if row.get("severity") in LEVELS else "unknown"
        residual = row.get("residual") if row.get("residual") in LEVELS else "unknown"
        effect = row.get("effect_of_mitigation") if row.get("effect_of_mitigation") in EFFECTS else "unknown"
        mitigation = row.get("mitigation") if isinstance(row.get("mitigation"), str) else ""
        drafted.append(
            {
                "id": row.get("id") if isinstance(row.get("id"), str) else "unlabelled",
                "description": row.get("description") if isinstance(row.get("description"), str) and row.get("description") else GAP_TEXT,
                "source": row.get("source") if isinstance(row.get("source"), str) and row.get("source") else GAP_TEXT,
                "likelihood": likelihood,
                "severity": severity,
                "harm_types": _harms(row.get("harm_types")),
                "mitigation": mitigation if mitigation else GAP_TEXT,
                "mitigation_in_place": False,
                "effect_of_mitigation": effect,
                "residual": residual,
                "scored_by_this_tool": False,
                "prefilled_from": row.get("prefilled_from"),
            }
        )
    return drafted


def _consultation_flag(risks: list[dict], overall: str) -> dict:
    residuals = [row["residual"] for row in risks]
    if overall not in LEVELS:
        overall = "unknown"
    any_high = overall == "High" or any(value == "High" for value in residuals)
    any_unknown = overall == "unknown" or any(value == "unknown" for value in residuals) or not risks
    if any_high:
        code = "high_residual_recorded"
    elif any_unknown:
        code = "cannot_tell"
    else:
        code = "high_residual_not_recorded"
    return {
        "code": code,
        "article_36_1_quote": ARTICLE_36_1,
        "article_36_consultation_required": None,
        "consultation_required_decided_by_this_tool": False,
        "sent_by_agent": False,
        "statutory_addressee": "the Commission",
        "commission_note": COMMISSION_NOTE,
        "ico_page_note": ICO_RESIDUAL_NOTE,
        "ico_consult_url": ICO_CONSULT_URL,
        "email_on_the_ico_page_is_not_a_tool": "dpiaconsultation@ico.org.uk",
    }


def _inventory_note(inventory: dict | None) -> str | None:
    if not isinstance(inventory, dict):
        return None
    profiling = inventory.get("profiling") == "yes"
    effect = inventory.get("significant_effect") in {"legal", "similarly_significant"}
    if profiling and effect:
        return (
            "The linked inventory records profiling and a legal or similarly "
            "significant effect. Article 35(3)(a) also asks whether the evaluation "
            "is systematic and extensive. This tool does not convert the inventory "
            "into an Article 35(3)(a) answer."
        )
    return None


def _sources_stale(as_of: date) -> bool:
    return (as_of - SOURCES_PINNED_ON).days > STALE_AFTER_DAYS


def assess(
    brief: dict,
    *,
    as_of: str,
    inventory: dict | None = None,
    manifest: dict | None = None,
) -> dict:
    """Return one draft DPIA. Approval flags stay false."""

    if not isinstance(brief, dict):
        raise TypeError("brief must be an object")
    if brief.get("synthetic") is not True:
        raise NotSynthetic("synthetic must be true")
    day = _parse_as_of(as_of)
    cleaned, stripped = _strip(brief)
    working, inventory_notes = apply_inventory(cleaned, inventory or {})
    working, manifest_result = apply_manifest(working, manifest or {})
    prefilled = {note["field"] for note in inventory_notes}
    prefilled.update(note["field"] for note in manifest_result["copied"])

    injection = scan_fields(_strings(working))
    working = _neutralise_brief(working)
    redacted, gateway = _redact_brief(working)
    screening_block = redacted.get("screening") if isinstance(redacted.get("screening"), dict) else {}
    view = screening_block.get("article_35_1_controller_view", "unknown")
    screening_result = screen(screening_block, article_35_1_view=view if isinstance(view, str) else "unknown")
    if redacted.get("exemption_claimed") == "yes":
        screening_result["flags"] = list(screening_result["flags"]) + ["exemption_not_applied"]
        screening_result["exemption_note"] = (
            "The brief claims an exception. Article 35(10) and the ICO when-page "
            "describe cases where a DPIA may already have been done. This tool "
            "does not apply either exception. The ICO page says the ICO has not "
            "issued a list of processing that does not require a DPIA."
        )

    automated = screen_automated(
        redacted.get("automated_decision") if isinstance(redacted.get("automated_decision"), dict) else {},
        as_of=day,
    )
    description = redacted.get("description") if isinstance(redacted.get("description"), dict) else {}
    necessity = redacted.get("necessity") if isinstance(redacted.get("necessity"), dict) else {}
    consultation = redacted.get("consultation") if isinstance(redacted.get("consultation"), dict) else {}
    risks = _risk_rows(redacted.get("risks"))
    overall = redacted.get("residual_risk_overall", "unknown")
    prior = _consultation_flag(risks, overall if isinstance(overall, str) else "unknown")

    linked_note = _inventory_note(inventory)
    agent_section = manifest_result["agent_section"]
    agent_section["inventory_id"] = inventory.get("inventory_id") if isinstance(inventory, dict) else None
    agent_section["copied_fields"] = sorted(prefilled)
    agent_section["inventory_note"] = linked_note

    sections = [
        _section(
            1,
            "Identify whether a DPIA is being considered",
            "UK GDPR Article 35(1) and (3). The minimum contents are Article 35(7).",
            [
                {
                    "name": "screening",
                    "text": screening_result["reading"],
                    "state": "screened_from_recorded_answers",
                    "prefilled_from": None,
                }
            ],
        ),
        _section(
            2,
            "Describe the processing",
            "UK GDPR Article 35(7)(a): " + ARTICLE_35_7["a"],
            [_field(description, key, prefilled=prefilled, path=f"description.{key}") for key in DESCRIPTION_FIELDS],
        ),
        _section(
            3,
            "Consultation",
            "UK GDPR Article 35(2) and (9). " + ARTICLE_35_2,
            [
                {
                    "name": "individuals",
                    "text": consultation.get("individuals_consulted")
                    if consultation.get("individuals_consulted") in {"yes", "no", "not_appropriate", "unknown"}
                    else "unknown",
                    "state": "recorded_answer",
                    "prefilled_from": None,
                },
                _field(consultation, "individuals_reason_if_not", prefilled=prefilled, path="consultation.individuals_reason_if_not"),
                {
                    "name": "dpo_designated",
                    "text": consultation.get("dpo_designated")
                    if consultation.get("dpo_designated") in {"yes", "no", "unknown"}
                    else "unknown",
                    "state": "recorded_answer",
                    "prefilled_from": None,
                },
                _field(consultation, "dpo_advice_recorded", prefilled=prefilled, path="consultation.dpo_advice_recorded"),
                {
                    "name": "dpo_advice",
                    "text": None,
                    "state": "left_blank",
                    "prefilled_from": None,
                },
            ],
        ),
        _section(
            4,
            "Necessity and proportionality",
            "UK GDPR Article 35(7)(b): " + ARTICLE_35_7["b"],
            [_field(necessity, key, prefilled=prefilled, path=f"necessity.{key}") for key in NECESSITY_FIELDS],
        ),
        _section(
            5,
            "Risks to individuals",
            "UK GDPR Article 35(7)(c): " + ARTICLE_35_7["c"],
            [
                {
                    "name": "risks",
                    "text": f"{len(risks)} risk row or rows copied. This tool does not score the ICO matrix.",
                    "state": "copied_from_brief" if risks else "gap",
                    "prefilled_from": "inventory.risk_rows" if "risks" in prefilled else None,
                }
            ],
        ),
        _section(
            6,
            "Measures",
            "UK GDPR Article 35(7)(d): " + ARTICLE_35_7["d"],
            [
                {
                    "name": "mitigations",
                    "text": "A mitigation string is a note of what the brief says. mitigation_in_place is false on every row.",
                    "state": "copied_from_brief" if any(row["mitigation"] != GAP_TEXT for row in risks) else "gap",
                    "prefilled_from": None,
                }
            ],
        ),
        _section(
            7,
            "Outcomes left for the privacy officer and the project owner",
            "ICO step 7 asks who approved the measures and the residual risk. Those names are left blank.",
            [
                {"name": "sign_off", "text": None, "state": "left_blank", "prefilled_from": None},
            ],
        ),
    ]

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "19-privacy-impact-assessment",
        "autonomy": "A1",
        "document_status": "draft",
        "approved": False,
        "rejected": False,
        "signed_off": False,
        "residual_risk_accepted": False,
        "prior_consultation_sent": False,
        "dpia_required": None,
        "article_36_consultation_required": None,
        "lawful": None,
        "determination": "not_a_legal_determination",
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "project_name": redacted.get("project_name") or GAP_TEXT,
        "organisation_name": redacted.get("organisation_name") or GAP_TEXT,
        "as_of": day.isoformat(),
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_stale": _sources_stale(day),
        "stale_after_days": STALE_AFTER_DAYS,
        "screening": screening_result,
        "automated_decision_screen": automated,
        "sections": sections,
        "risks": risks,
        "prior_consultation": prior,
        "sign_off": {
            "measures_approved_by": None,
            "residual_risks_accepted_by": None,
            "dpo_advice": None,
            "dpo_advice_accepted_or_overruled_by": None,
            "individuals_views_reviewed_by": None,
            "kept_under_review_by": None,
            "prior_consultation_sent_by": None,
        },
        "agent_sections": agent_section,
        "prefill": {
            "inventory": inventory_notes,
            "manifest": manifest_result["copied"],
            "screening_inferred": False,
        },
        "prompt_injection": injection,
        "stripped_keys": stripped,
        "redaction": gateway,
        "not_legal_advice": True,
    }
    draft["checksum"] = draft_checksum(draft)
    return draft


def draft_checksum(draft: dict) -> str:
    copy = deepcopy(draft)
    copy.pop("checksum", None)
    copy.pop("external_attestation", None)
    payload = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_external_attestation(draft: dict, *, role: str, checksum: str, caller: str) -> dict:
    """Record that a person outside the agent named a role. Effect is none.

    The skills say the agent must not call this. ``caller`` must be
    ``human_outside_agent``. The returned copy is still a draft.
    """

    if caller != "human_outside_agent":
        raise AssessmentForbidden("the agent must not record an attestation")
    if role not in {"Privacy officer", "Data protection officer", "Project owner"}:
        raise AssessmentForbidden("role is not an approver named in the manifest")
    if checksum != draft_checksum(draft):
        raise AssessmentForbidden("checksum does not match the draft")
    copy = deepcopy(draft)
    copy["external_attestation"] = {
        "role": role,
        "effect": "none",
        "approved": False,
        "signed_off": False,
        "residual_risk_accepted": False,
        "note": (
            "A person outside the agent supplied this role. This starter does "
            "not record the DPIA as approved and does not record residual risk "
            "as accepted."
        ),
    }
    copy["approved"] = False
    copy["rejected"] = False
    copy["signed_off"] = False
    copy["residual_risk_accepted"] = False
    copy["prior_consultation_sent"] = False
    copy["document_status"] = "draft"
    copy["actions_taken"] = []
    return copy


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a DPIA. Do not approve it.")
    parser.add_argument("--input", required=True, help="Synthetic project brief JSON")
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD, typed outside the brief")
    parser.add_argument("--inventory", help="Optional Experiment 03 inventory JSON")
    parser.add_argument("--manifest", help="Optional agent-manifest.yaml")
    parser.add_argument("--output", help="Write the draft JSON here. Default is stdout.")
    args = parser.parse_args(argv)
    brief = _load_json(args.input)
    inventory = _load_json(args.inventory) if args.inventory else None
    manifest = None
    if args.manifest:
        import yaml

        with open(args.manifest, encoding="utf-8") as handle:
            manifest = yaml.safe_load(handle)
    try:
        draft = assess(brief, as_of=args.as_of, inventory=inventory, manifest=manifest)
    except NotSynthetic as exc:
        print(str(exc), file=sys.stderr)
        return 2
    text = json.dumps(draft, indent=2, ensure_ascii=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
