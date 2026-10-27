#!/usr/bin/env python3
"""Draft platform options for one proposed agent. Do not select or deploy.

The same use case and the same as-of date produce the same JSON. Free text
is not an input to the rules. Autonomy A3 is never the recommendation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import scan_strings, strip_prohibited
    from manifest_skeleton import draft_skeleton
    from rules import RULE_TABLE, is_consequential, normalise, score
    from sources import DEFAULT_STALE_AFTER_DAYS, currency
else:
    from .injection import scan_strings, strip_prohibited
    from .manifest_skeleton import draft_skeleton
    from .rules import RULE_TABLE, is_consequential, normalise, score
    from .sources import DEFAULT_STALE_AFTER_DAYS, currency

LABEL = "DRAFT FOR ARCHITECT REVIEW"
CATALOGUE_ID = "G002"

_ACTION_POINTS = (
    ("production_write", "Change a production record"),
    ("external_send", "Send externally"),
    ("spend", "Spend or transact"),
    ("approve_or_reject", "Approve or reject"),
    ("regulated_decision", "Make a regulated decision"),
)


def _approval_points(case: dict[str, Any], stale: bool) -> list[dict[str, Any]]:
    role = case["risk"]["approver_role"] or "Named approver, role not recorded"
    if not case["risk"]["named_approver"]:
        role = "No approver was recorded"
    points = [
        {
            "action": "Confirm each platform option, including no agent",
            "approver": "Architect",
            "mandatory": True,
            "rationale": "The advisor has selected none. platform_selected stays null.",
        },
        {
            "action": "Confirm the catalogue autonomy level",
            "approver": "Architect",
            "mandatory": True,
            "rationale": "A3 is not available. A0, A1, and A2 are recommendations, not a decision.",
        },
        {
            "action": "Approve the permissions manifest before anyone relies on it",
            "approver": "Governance owner",
            "mandatory": True,
            "rationale": "The skeleton is a draft. approved is false.",
        },
    ]
    for key, label in _ACTION_POINTS:
        if case["actions"][key]:
            points.append(
                {
                    "action": label,
                    "approver": role,
                    "mandatory": True,
                    "rationale": "The skeleton leaves this action disabled. This draft does not turn it on.",
                }
            )
    if case["risk"]["significant_automated_decision"]:
        points.append(
            {
                "action": "Decide whether a significant automated decision is even in scope",
                "approver": role,
                "mandatory": True,
                "rationale": "The advisor does not make that decision and does not recommend autonomy A3.",
            }
        )
    if case["data"]["personal_data"] or case["data"]["special_category"]:
        points.append(
            {
                "action": "Confirm the Article 6 basis before any live processing",
                "approver": "Data protection officer",
                "mandatory": True,
                "rationale": "The skeleton does not choose a basis.",
            }
        )
    if case["data"]["special_category"]:
        points.append(
            {
                "action": "Confirm an Article 9 condition",
                "approver": "Data protection officer",
                "mandatory": True,
                "rationale": "No Article 9 condition is asserted.",
            }
        )
    if case["data"]["classification"] in {"unknown", "official_sensitive"}:
        points.append(
            {
                "action": "Confirm the data classification and the tenant boundary",
                "approver": "Architect",
                "mandatory": True,
                "rationale": "This advisor does not cite a Microsoft classification scheme.",
            }
        )
    if case["data"]["residency"] == "uk":
        points.append(
            {
                "action": "Confirm a UK region before any deployment",
                "approver": "Architect",
                "mandatory": True,
                "rationale": "A UK region list was not on the Foundry overview opened on 27 October 2026. Unverified.",
            }
        )
    if stale:
        points.append(
            {
                "action": "Re-open the pinned Microsoft Learn pages before relying on a citation",
                "approver": "Architect",
                "mandatory": True,
                "rationale": "At least one pinned page is older than the stale threshold.",
            }
        )
    return points


def _licensing_notes(case: dict[str, Any]) -> list[dict[str, Any]]:
    notes = [
        {
            "text": (
                "Licence flags are the architect's statement. This advisor does not open an admin centre. "
                "The assign-licences page says creating and managing standard-harness agents needs a user licence "
                "and a tenant licence, and that a trial can test in the chat panel but cannot publish. "
                "The standard-harness licensing page uses a different list, including a Microsoft 365 Copilot licence, "
                "and says that licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. "
                "The cost-management page says GitHub Copilot harness consumption is not included with a Microsoft 365 "
                "Copilot licence, and that standard-harness agents are covered by that licence in Microsoft 365 channels "
                "and billed outside that case. The sentences are not merged. No quantity or price is copied."
            ),
            "source_ids": ["cs-assign-licences", "cs-standard-licensing", "cs-gh-cost-management"],
        },
        {
            "text": (
                "The usage-based billing overview says the GitHub Copilot harness charges Copilot Credits from the "
                "moment you start building, including testing, and that the standard harness starts billing after publish. "
                "No diagram and no rate from that page is copied."
            ),
            "source_ids": ["cs-usage-billing"],
        },
        {
            "text": (
                "The Power Automate licence-types page describes user licences and capacity licences and points to a "
                "pricing page. That pricing page was not opened. A recorded yes does not say which licence is held, "
                "and it does not say that premium connectors are included."
            ),
            "source_ids": ["pa-licence-types"],
        },
        {
            "text": (
                "The Foundry Agent Service overview describes cost as per-call inference plus tool usage for prompt "
                "agents, and that plus container compute for hosted agents. It points to a pricing page for voice. "
                "That page was not opened. No figure is copied."
            ),
            "source_ids": ["foundry-agent-service"],
        },
    ]
    licences = case["organisation"]["licences"]
    if licences["microsoft_365_copilot"] == "yes":
        notes.append(
            {
                "text": (
                    "The organisation recorded a Microsoft 365 Copilot licence. That record is not treated as a "
                    "Copilot Studio tenant licence, and it is not treated as covering GitHub Copilot harness consumption. "
                    "See the two sentences above. The architect confirms both in the tenant."
                ),
                "source_ids": ["cs-standard-licensing", "cs-gh-cost-management"],
            }
        )
    if licences["github_copilot_service_only"] and licences["copilot_studio"] == "yes":
        notes.append(
            {
                "text": (
                    "The GitHub Copilot service was recorded as well as Copilot Studio. The service is still not the "
                    "harness. Copilot Studio was recorded as held, so the harness options were not blocked by that confusion."
                ),
                "source_ids": ["cs-harnesses-overview"],
            }
        )
    return notes


def _autonomy_rationale(level: str, case: dict[str, Any]) -> str:
    requested = case["risk"]["requested_autonomy"]
    if requested == "A3":
        return (
            f"Autonomy A3 was requested and is refused. The catalogue recommendation is {level}. "
            "The skeleton uses that level and leaves consequential actions disabled. "
            "The architect confirms the level. The advisor does not."
        )
    if level == "A0":
        return (
            "Recommended autonomy is A0. Either no consequential action is in scope, no approver was named, "
            "or the architect asked for A0 so those actions stay out of scope. The advisor takes no action."
        )
    if level == "A1":
        return (
            "Recommended autonomy is A1. A consequential action remains and a named approver was recorded. "
            "A1 means a person approves every such action. The skeleton still leaves the action disabled."
        )
    return (
        "Recommended autonomy is A2. A2 was requested, a named approver was recorded, and a consequential action "
        "remains. A2 still requires a person for that action. The skeleton leaves it disabled until a person edits "
        "a later manifest and the schema still passes. This draft is not that edit."
    )


def advise(
    case: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    approve: bool = False,
) -> dict[str, Any]:
    base = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "14-agent-architecture-advisor",
        "as_of": as_of,
        "model_called": False,
        "network_called": False,
        "deployed": False,
        "decision": None,
        "platform_selected": None,
        "architect_confirmed": False,
        "manifest_approved": False,
        "actions_taken": [],
        "a3_recommended": False,
        "catalogue_autonomy_levels": ["A0", "A1", "A2"],
    }
    if approve:
        base.update(
            {
                "errors": ["The advisor cannot mark a manifest approved."],
                "recommended_autonomy": None,
                "manifest_skeleton": {
                    "validation_passed": False,
                    "approved": False,
                    "may_be_relied_on": False,
                    "autonomy_level": None,
                    "errors": ["The advisor cannot mark a manifest approved."],
                    "yaml": None,
                },
            }
        )
        return base

    cleaned, ignored_keys = strip_prohibited(case)
    normalised, input_notes = normalise(cleaned)
    signals = scan_strings(cleaned)
    sources = currency(as_of, stale_after_days)
    stale = any(row["stale"] for row in sources)
    scored = score(normalised)
    level = scored["recommended_autonomy"]
    if level not in {"A0", "A1", "A2"} or scored["a3_recommended"] is not False:
        raise RuntimeError("Autonomy A3 must not be recommended")
    skeleton = draft_skeleton(normalised, level, as_of, approve=False)
    if skeleton["autonomy_level"] not in {"A0", "A1", "A2"}:
        skeleton["validation_passed"] = False
        skeleton["yaml"] = None
    unscored = [
        {
            "text": (
                "The harness overview also describes a Customer Conversation harness for customer voice and chat, "
                "using Copilot Credits. It is not one of the five options. This advisor does not select it."
            ),
            "source_ids": ["cs-harnesses-overview"],
        },
        {
            "text": (
                "A procurement route is not scored. G-Cloud, DOS, and RM6200 were not opened for this run."
            ),
            "source_ids": [],
        },
        {
            "text": (
                "Microsoft Entra Conditional Access, Microsoft Purview, a Data Loss Prevention policy, and Key Vault "
                "were not opened for this revision. Treat any claim about those controls as unverified. "
                "The Foundry overview does describe Microsoft Entra identity, role-based access control, and "
                "virtual network isolation for Agent Service. Application Insights is named there for traces."
            ),
            "source_ids": ["foundry-agent-service"],
        },
    ]
    base.update(
        {
            "case_id": normalised["case_id"],
            "errors": [],
            "input_notes": input_notes,
            "recommended_autonomy": level,
            "autonomy_rationale": _autonomy_rationale(level, normalised),
            "a3_requested": normalised["risk"]["requested_autonomy"] == "A3",
            "a3_refused": normalised["risk"]["requested_autonomy"] == "A3",
            "consequential_action_recorded": is_consequential(normalised),
            "work_shape": scored["work_shape"],
            "rules_fired": scored["rules_fired"],
            "options": scored["options"],
            "decision_table": [
                {"id": row["id"], "when": row["when"], "effect": row["effect"]} for row in RULE_TABLE
            ],
            "approval_points": _approval_points(normalised, stale),
            "licensing_notes": _licensing_notes(normalised),
            "unscored_context": unscored,
            "prompt_injection": {
                "detected": bool(signals),
                "followed": False,
                "signals": signals,
                "prohibited_payload_keys_ignored": ignored_keys,
                "narrative_used_as_instruction": False,
            },
            "scored_fields": {
                "organisation": {
                    "sector": normalised["organisation"]["sector"],
                    "licences": normalised["organisation"]["licences"],
                },
                "users": normalised["users"],
                "data": {
                    "personal_data": normalised["data"]["personal_data"],
                    "special_category": normalised["data"]["special_category"],
                    "classification": normalised["data"]["classification"],
                    "volume": normalised["data"]["volume"],
                    "residency": normalised["data"]["residency"],
                },
                "actions": normalised["actions"],
                "risk": normalised["risk"],
            },
            "sources_stale": stale,
            "do_not_rely": stale,
            "sources": sources,
            "manifest_skeleton": skeleton,
        }
    )
    return base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft architecture options for one use case. Never selects or deploys."
    )
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Refused. Present so a caller cannot pass it quietly.",
    )
    args = parser.parse_args(argv)
    try:
        from datetime import date

        date.fromisoformat(args.as_of)
    except ValueError:
        print("as-of must be YYYY-MM-DD", file=sys.stderr)
        return 2
    payload = json.loads(args.case.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        print("Pass one use case, not the fixture list.", file=sys.stderr)
        return 2
    result = advise(
        payload,
        args.as_of,
        stale_after_days=args.stale_after_days,
        approve=args.approve,
    )
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output and not args.approve and result.get("manifest_skeleton", {}).get("validation_passed"):
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    if args.approve:
        return 2
    skeleton = result.get("manifest_skeleton") or {}
    if skeleton.get("validation_passed") is not True:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
