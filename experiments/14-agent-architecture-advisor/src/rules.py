"""Decision table for platform options and catalogue autonomy.

The architect confirms every option. Nothing in this module sets selected.
Autonomy A3 is not a return value.
"""

from __future__ import annotations

from typing import Any

SUITABLE = "suitable_to_consider"
CONDITIONAL = "possible_with_conditions"
NOT = "not_indicated"

OPTION_ORDER = (
    "copilot_studio_standard",
    "copilot_studio_github_harness",
    "foundry_agent_service",
    "power_automate",
    "no_agent",
)

OPTION_NAMES = {
    "copilot_studio_standard": "Copilot Studio standard harness",
    "copilot_studio_github_harness": "Copilot Studio GitHub Copilot harness",
    "foundry_agent_service": "Microsoft Foundry Agent Service",
    "power_automate": "Power Automate",
    "no_agent": "No agent",
}

LICENCE_KEY = {
    "copilot_studio_standard": "copilot_studio",
    "copilot_studio_github_harness": "copilot_studio",
    "foundry_agent_service": "foundry",
    "power_automate": "power_automate",
}

ACTION_KEYS = (
    "read",
    "draft",
    "classify",
    "create_files",
    "fixed_workflow",
    "multi_step_reasoning",
    "long_running",
    "needs_custom_code",
    "needs_model_choice",
    "needs_private_network",
    "needs_evaluations",
    "production_write",
    "external_send",
    "spend",
    "approve_or_reject",
    "regulated_decision",
)

CONSEQUENTIAL_ACTIONS = (
    "production_write",
    "external_send",
    "spend",
    "approve_or_reject",
    "regulated_decision",
)

FOUNDRY_NEEDS = (
    "needs_custom_code",
    "needs_model_choice",
    "needs_private_network",
    "needs_evaluations",
)

CLASSIFICATIONS = ("official", "official_sensitive", "secret_or_above", "synthetic", "unknown")
AUDIENCES = ("internal_staff", "customers", "public", "mixed")
CHANNELS = ("teams", "web", "voice", "email", "api", "none")
LICENCE_VALUES = ("yes", "no", "unknown")
AUTONOMY_REQUESTS = ("A0", "A1", "A2", "A3")

RULE_TABLE: list[dict[str, str]] = [
    {
        "id": "R1",
        "when": "Classification is secret_or_above.",
        "effect": "Only no agent is suitable. The other four are not indicated. Catalogue rule, not a Microsoft Learn sentence.",
    },
    {
        "id": "R2",
        "when": "Channel is voice and the audience is customers, the public, or mixed.",
        "effect": "No agent is suitable. Foundry voice is preview, so Foundry is conditional. The Customer Conversation harness is not scored.",
    },
    {
        "id": "R3",
        "when": "The steps are a fixed, bounded workflow with no open-ended reasoning, long run, file creation, or custom code.",
        "effect": "Power Automate is suitable, subject to licence. The agent harnesses are not indicated.",
    },
    {
        "id": "R4",
        "when": "The work is long-running, multi-step, large or multi-source, creates files, or needs custom code.",
        "effect": "The GitHub Copilot harness is suitable, subject to licence. The standard harness is conditional. Foundry is suitable only when a Foundry capability was asked for.",
    },
    {
        "id": "R5",
        "when": "The work is a short, bounded, rule-based agent.",
        "effect": "The standard harness is suitable, subject to licence. The GitHub Copilot harness is not indicated.",
    },
    {
        "id": "R6",
        "when": "Autonomy A3 was requested, or a consequential action has no named approver.",
        "effect": "No agent is suitable for the unsupervised design. A platform that was suitable becomes conditional, for a reduced scope that leaves the action off.",
    },
    {
        "id": "R7",
        "when": "The organisation recorded no for the licence that option needs, and the option was still open.",
        "effect": "That option is not indicated. No purchase is recommended.",
    },
    {
        "id": "R8",
        "when": "The licence was recorded as unknown, and the option was still open.",
        "effect": "A suitable option becomes conditional. The architect confirms the licence.",
    },
    {
        "id": "R9",
        "when": "The record says the GitHub Copilot service is held and Copilot Studio was not recorded as held.",
        "effect": "Both Copilot Studio harnesses are not indicated. The harness is not the GitHub Copilot service.",
    },
    {
        "id": "R10",
        "when": "No consequential action remains in scope, there is no named approver, or the architect asked for A0.",
        "effect": "Recommended autonomy is A0.",
    },
    {
        "id": "R11",
        "when": "A consequential action remains, a named approver was recorded, and A2 was not requested.",
        "effect": "Recommended autonomy is A1. A request for A3 is lowered to A1.",
    },
    {
        "id": "R12",
        "when": "A2 was requested, a named approver was recorded, and a consequential action remains.",
        "effect": "Recommended autonomy is A2. The skeleton still leaves the action disabled.",
    },
    {
        "id": "R13",
        "when": "A3 was requested.",
        "effect": "A3 is refused. a3_recommended is false.",
    },
    {
        "id": "R14",
        "when": "All four product options are not indicated.",
        "effect": "No agent is suitable.",
    },
]


def _blank_options() -> dict[str, dict[str, Any]]:
    options = {}
    for option_id in OPTION_ORDER:
        options[option_id] = {
            "id": option_id,
            "name": OPTION_NAMES[option_id],
            "suitability": NOT,
            "selected": False,
            "reasons": [],
            "preview_notes": [],
        }
    return options


def _add(option: dict[str, Any], rule_id: str, text: str, source_ids: list[str]) -> None:
    option["reasons"].append({"rule_id": rule_id, "text": text, "source_ids": source_ids})


def _foundry_need(actions: dict[str, bool]) -> bool:
    return any(actions[key] for key in FOUNDRY_NEEDS)


def work_shape(case: dict[str, Any]) -> str:
    if case["data"]["classification"] == "secret_or_above":
        return "blocked_data"
    audience = case["users"]["audience"]
    if case["users"]["channel"] == "voice" and audience in {"customers", "public", "mixed"}:
        return "customer_voice"
    actions = case["actions"]
    fixed = (
        actions["fixed_workflow"]
        and not actions["multi_step_reasoning"]
        and not actions["long_running"]
        and not actions["create_files"]
        and not actions["needs_custom_code"]
        and case["data"]["volume"] == "bounded"
    )
    if fixed:
        return "fixed_flow"
    heavy = (
        actions["multi_step_reasoning"]
        or actions["long_running"]
        or actions["create_files"]
        or actions["needs_custom_code"]
        or case["data"]["volume"] in {"large_files", "multi_source"}
    )
    if heavy:
        return "reasoning_heavy"
    return "bounded"


def is_consequential(case: dict[str, Any]) -> bool:
    if case["risk"]["significant_automated_decision"]:
        return True
    return any(case["actions"][key] for key in CONSEQUENTIAL_ACTIONS)


def unsupervised(case: dict[str, Any]) -> bool:
    if case["risk"]["requested_autonomy"] == "A3":
        return True
    if is_consequential(case) and not case["risk"]["named_approver"]:
        return True
    return False


def _apply_shape(options: dict[str, dict[str, Any]], case: dict[str, Any], shape: str) -> None:
    actions = case["actions"]
    if shape == "blocked_data":
        _add(
            options["no_agent"],
            "R1",
            "Classification was recorded as secret or above. This catalogue does not put that material into a generative agent or a cloud flow. No Microsoft Learn page is cited as a classification rule.",
            ["catalogue-boundary"],
        )
        options["no_agent"]["suitability"] = SUITABLE
        for option_id in OPTION_ORDER:
            if option_id == "no_agent":
                continue
            _add(
                options[option_id],
                "R1",
                "Not indicated while the use case is recorded as secret or above.",
                ["catalogue-boundary"],
            )
            options[option_id]["suitability"] = NOT
        return

    if shape == "customer_voice":
        _add(
            options["no_agent"],
            "R2",
            "The channel is customer or public voice. This advisor does not select a production voice agent. The architect confirms that a person remains available.",
            ["catalogue-boundary"],
        )
        options["no_agent"]["suitability"] = SUITABLE
        _add(
            options["foundry_agent_service"],
            "R2",
            "The Foundry Agent Service overview describes voice-based prompt agents and marks them as preview, including some related monitoring, evaluation, avatar, WebRTC, and telephony capabilities. Preview is not a production selection. The overview says preview capabilities are not recommended for production workloads until support, security, compliance, and availability have been reviewed.",
            ["foundry-agent-service"],
        )
        options["foundry_agent_service"]["suitability"] = CONDITIONAL
        _add(
            options["copilot_studio_standard"],
            "R2",
            "The harness overview gives customer voice and chat to the Customer Conversation harness. That harness is not one of the five options this advisor scores. The standard harness is not indicated for this voice channel.",
            ["cs-harnesses-overview"],
        )
        _add(
            options["copilot_studio_github_harness"],
            "R2",
            "The harness overview does not describe the GitHub Copilot harness as the voice channel. It is not indicated for this voice use case. It remains a Copilot Studio framework, not the GitHub Copilot service.",
            ["cs-harnesses-overview"],
        )
        _add(
            options["power_automate"],
            "R2",
            "The cloud-flows overview describes event, button, and schedule triggers. It does not describe a voice agent. Power Automate is not indicated as the voice channel.",
            ["pa-cloud-flows"],
        )
        return

    if shape == "fixed_flow":
        _add(
            options["power_automate"],
            "R3",
            "The steps are a known sequence on bounded data. The cloud-flows overview describes automated flows started by an event, instant flows started by a button, and scheduled flows. An approval in Teams or SharePoint is given there as an example of a person using a button, not of a flow deciding. A cloud flow is not an agent.",
            ["pa-cloud-flows"],
        )
        options["power_automate"]["suitability"] = SUITABLE
        _add(
            options["no_agent"],
            "R3",
            "A cloud flow is not an agent. A person can also run a written procedure. Neither is selected.",
            ["catalogue-boundary", "pa-cloud-flows"],
        )
        options["no_agent"]["suitability"] = CONDITIONAL
        for option_id, text in (
            (
                "copilot_studio_standard",
                "The comparison page says to choose the standard harness for short, bounded, rule-based work, and it also says a harness can overwork a job whose steps are already fixed. An agent is not indicated when the procedure is already a flow.",
            ),
            (
                "copilot_studio_github_harness",
                "The comparison page says the GitHub Copilot harness can add reasoning, latency, and Copilot Credit consumption on a simple scenario. No rate is copied. It is not indicated for a fixed sequence.",
            ),
        ):
            _add(options[option_id], "R3", text, ["cs-choose-harness"])
        _add(
            options["foundry_agent_service"],
            "R3",
            "The use case does not ask for custom code, a chosen model, a private network, or Foundry evaluations. Foundry Agent Service is not indicated for a fixed cloud flow.",
            ["foundry-agent-service"],
        )
        return

    if shape == "reasoning_heavy":
        _add(
            options["copilot_studio_github_harness"],
            "R4",
            "The harness overview describes the GitHub Copilot harness for reasoning-heavy, multi-step work: a goal broken into steps, tools, skills, memory, and creating or editing Word, Excel, PowerPoint, and PDF files, in a sandbox governed by Copilot Studio. The comparison page describes longer-running tasks, larger files, and agentic loops. It is a Copilot Studio framework, not the GitHub Copilot service. Agents on this harness use Copilot Credits. No rate is copied.",
            ["cs-harnesses-overview", "cs-choose-harness"],
        )
        options["copilot_studio_github_harness"]["suitability"] = SUITABLE
        _add(
            options["copilot_studio_standard"],
            "R4",
            "The comparison page says the standard harness can run multistep work when makers author the paths, and that complex scenarios can need extensive custom routing. It is conditional: only if the architect will bound the task and accept that authoring. It is not the lead fit for this shape.",
            ["cs-choose-harness"],
        )
        options["copilot_studio_standard"]["suitability"] = CONDITIONAL
        if _foundry_need(actions):
            _add(
                options["foundry_agent_service"],
                "R4",
                "The use case records custom code, a chosen model, a private network, or evaluations. The Foundry Agent Service overview describes prompt agents and hosted agents, with tracing, evaluations, Application Insights, Microsoft Entra identity, and private-network controls. Agent optimizer is marked preview and is not a reason to choose the service. A UK region list was not on the page.",
                ["foundry-agent-service"],
            )
            options["foundry_agent_service"]["suitability"] = SUITABLE
        else:
            _add(
                options["foundry_agent_service"],
                "R4",
                "Foundry Agent Service is conditional. The overview describes it for a managed runtime, custom code, a model from the catalogue, evaluations, and network controls. None of those was recorded as a requirement. It is not indicated as a substitute for the Copilot Studio harness on its own.",
                ["foundry-agent-service"],
            )
            options["foundry_agent_service"]["suitability"] = CONDITIONAL
        _add(
            options["power_automate"],
            "R4",
            "The cloud-flows overview describes a deterministic trigger: an event, a button, or a schedule. A flow can hold such a step beside an agent, for example an approval a person completes. It is not the reasoning runtime.",
            ["pa-cloud-flows"],
        )
        options["power_automate"]["suitability"] = CONDITIONAL
        _add(
            options["no_agent"],
            "R4",
            "The architect may decide not to build. That option is conditional, not a selection.",
            ["catalogue-boundary"],
        )
        options["no_agent"]["suitability"] = CONDITIONAL
        return

    _add(
        options["copilot_studio_standard"],
        "R5",
        "The harness overview describes the standard harness for rule-based agents and structured, repeatable conversations, with topics and paths the maker defines. The comparison page says to choose it when the work is relatively short and bounded and explicit control matters.",
        ["cs-harnesses-overview", "cs-choose-harness"],
    )
    options["copilot_studio_standard"]["suitability"] = SUITABLE
    _add(
        options["copilot_studio_github_harness"],
        "R5",
        "The comparison page says the GitHub Copilot harness may add reasoning, latency, and Copilot Credit consumption when the scenario is simple, without a better result. No rate is copied. It is not indicated for this bounded use case. The harness overview also says it is not the GitHub Copilot service.",
        ["cs-choose-harness", "cs-harnesses-overview"],
    )
    if _foundry_need(actions):
        _add(
            options["foundry_agent_service"],
            "R5",
            "A Foundry capability was recorded on an otherwise bounded use case. The overview describes evaluations, the model catalogue, and private networking. Foundry is conditional: only if that capability is the requirement. The conversational fit on the pages opened is still the standard harness. Agent optimizer is marked preview and is not a reason to choose the service.",
            ["foundry-agent-service"],
        )
        options["foundry_agent_service"]["suitability"] = CONDITIONAL
    else:
        _add(
            options["foundry_agent_service"],
            "R5",
            "No custom code, chosen model, private network, or Foundry evaluation was recorded. Foundry Agent Service is not indicated for this bounded use case.",
            ["foundry-agent-service"],
        )
    _add(
        options["power_automate"],
        "R5",
        "The use case is not only a fixed sequence of connector steps. The cloud-flows overview is not the fit for a conversational or drafting agent. Power Automate is not indicated as the agent.",
        ["pa-cloud-flows"],
    )
    _add(
        options["no_agent"],
        "R5",
        "The architect may decide not to build. That option is conditional, not a selection.",
        ["catalogue-boundary"],
    )
    options["no_agent"]["suitability"] = CONDITIONAL


def _apply_unsupervised(options: dict[str, dict[str, Any]]) -> None:
    options["no_agent"]["suitability"] = SUITABLE
    _add(
        options["no_agent"],
        "R6",
        "The use case asks for autonomy A3, or for a consequential action with no named approver. This catalogue does not build that unsupervised design. No agent is suitable for it.",
        ["catalogue-boundary"],
    )
    reduced = (
        "Only for a reduced scope that drops the unsupervised action. The action stays off in the manifest skeleton. "
        "This is not a selection, and it does not authorise the action."
    )
    for option_id in OPTION_ORDER:
        if option_id == "no_agent":
            continue
        if options[option_id]["suitability"] == SUITABLE:
            options[option_id]["suitability"] = CONDITIONAL
        if options[option_id]["suitability"] == CONDITIONAL:
            _add(options[option_id], "R6", reduced, ["catalogue-boundary"])


def _apply_service_confusion(options: dict[str, dict[str, Any]], case: dict[str, Any]) -> None:
    licences = case["organisation"]["licences"]
    if not licences["github_copilot_service_only"]:
        return
    if licences["copilot_studio"] == "yes":
        return
    text = (
        "The record says the GitHub Copilot service is held and Copilot Studio was not recorded as held. "
        "The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, "
        "not the GitHub Copilot service, and that customer data is not sent to that service."
    )
    for option_id in ("copilot_studio_standard", "copilot_studio_github_harness"):
        options[option_id]["suitability"] = NOT
        _add(options[option_id], "R9", text, ["cs-harnesses-overview"])


def _apply_licences(options: dict[str, dict[str, Any]], case: dict[str, Any]) -> list[str]:
    fired = []
    licences = case["organisation"]["licences"]
    saw_no = False
    saw_unknown = False
    for option_id, key in LICENCE_KEY.items():
        option = options[option_id]
        if option["suitability"] == NOT:
            continue
        recorded = licences[key]
        if recorded == "no":
            option["suitability"] = NOT
            _add(
                option,
                "R7",
                "The organisation recorded that it does not hold the licence this option needs. This advisor does not quote a price and does not recommend a purchase. A recorded yes or no is the architect's statement, not a lookup in an admin centre.",
                ["catalogue-boundary"],
            )
            saw_no = True
        elif recorded == "unknown":
            if option["suitability"] == SUITABLE:
                option["suitability"] = CONDITIONAL
            _add(
                option,
                "R8",
                "The licence was recorded as unknown. The architect confirms it before anyone builds. This advisor does not look the licence up and does not quote a price.",
                ["catalogue-boundary"],
            )
            saw_unknown = True
    if saw_no:
        fired.append("R7")
    if saw_unknown:
        fired.append("R8")
    return fired


def _apply_r14(options: dict[str, dict[str, Any]]) -> bool:
    products = [option_id for option_id in OPTION_ORDER if option_id != "no_agent"]
    if any(options[option_id]["suitability"] != NOT for option_id in products):
        return False
    options["no_agent"]["suitability"] = SUITABLE
    _add(
        options["no_agent"],
        "R14",
        "None of the four product options is indicated on the recorded facts. No agent is suitable. The architect can still confirm a different scope later. This draft does not build one.",
        ["catalogue-boundary"],
    )
    return True


def recommend_autonomy(case: dict[str, Any], shape: str) -> tuple[str, list[str]]:
    requested = case["risk"]["requested_autonomy"]
    named = case["risk"]["named_approver"]
    fired: list[str] = []
    if requested == "A3":
        fired.append("R13")
    if shape == "blocked_data" or not is_consequential(case) or not named or requested == "A0":
        fired.append("R10")
        return "A0", fired
    if requested == "A2":
        fired.append("R12")
        return "A2", fired
    fired.append("R11")
    return "A1", fired


def _preview_notes(case: dict[str, Any], shape: str) -> dict[str, list[dict[str, Any]]]:
    notes: dict[str, list[dict[str, Any]]] = {option_id: [] for option_id in OPTION_ORDER}
    notes["copilot_studio_github_harness"].append(
        {
            "text": (
                "The harness overview opened on 27 October 2026 does not mark the GitHub Copilot harness as preview. "
                "The comparison page says customers should validate required features and channels as the experience matures. "
                "That is a maturity caveat, not a preview label."
            ),
            "source_ids": ["cs-harnesses-overview", "cs-choose-harness"],
        }
    )
    notes["copilot_studio_github_harness"].append(
        {
            "text": (
                "The cost-management page says developer environments and trial environments move to usage-based billing "
                "on 1 September 2026. That date is before this retrieval. Confirm the tenant. No price is copied."
            ),
            "source_ids": ["cs-gh-cost-management"],
        }
    )
    notes["foundry_agent_service"].append(
        {
            "text": "Agent optimizer is marked preview on the Foundry Agent Service overview. It is not a reason to choose the service.",
            "source_ids": ["foundry-agent-service"],
        }
    )
    if shape == "customer_voice":
        notes["foundry_agent_service"].append(
            {
                "text": (
                    "Voice-based prompt agents, and some related monitoring, evaluation, avatar, WebRTC, and telephony "
                    "capabilities, are marked preview. The overview says preview is not recommended for production "
                    "workloads until the organisation has reviewed support, security, compliance, and availability."
                ),
                "source_ids": ["foundry-agent-service"],
            }
        )
    notes["foundry_agent_service"].append(
        {
            "text": (
                "Prompt Shields are described on a separate page. User prompt attack detection is on by default. "
                "Document attack detection is off by default. Tool-response scanning for agents, and Spotlighting, "
                "are marked preview. This advisor does not call Prompt Shields."
            ),
            "source_ids": ["foundry-prompt-shields"],
        }
    )
    return notes


def score(case: dict[str, Any]) -> dict[str, Any]:
    shape = work_shape(case)
    options = _blank_options()
    _apply_shape(options, case, shape)
    fired = []
    shape_rule = {
        "blocked_data": "R1",
        "customer_voice": "R2",
        "fixed_flow": "R3",
        "reasoning_heavy": "R4",
        "bounded": "R5",
    }[shape]
    fired.append(shape_rule)
    if unsupervised(case):
        _apply_unsupervised(options)
        fired.append("R6")
    before = {option_id: options[option_id]["suitability"] for option_id in OPTION_ORDER}
    _apply_service_confusion(options, case)
    if case["organisation"]["licences"]["github_copilot_service_only"] and case["organisation"]["licences"]["copilot_studio"] != "yes":
        if any(
            before[option_id] != NOT or options[option_id]["suitability"] == NOT
            for option_id in ("copilot_studio_standard", "copilot_studio_github_harness")
        ):
            fired.append("R9")
    fired.extend(_apply_licences(options, case))
    if _apply_r14(options):
        fired.append("R14")
    level, autonomy_rules = recommend_autonomy(case, shape)
    fired.extend(autonomy_rules)
    if level not in {"A0", "A1", "A2"}:
        raise RuntimeError("Autonomy A3 must not be recommended")
    for option in options.values():
        option["selected"] = False
        option["preview_notes"] = _preview_notes(case, shape)[option["id"]]
    return {
        "work_shape": shape,
        "options": [options[option_id] for option_id in OPTION_ORDER],
        "recommended_autonomy": level,
        "rules_fired": fired,
        "a3_recommended": False,
    }


def normalise(case: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Keep only known structured fields. Booleans count only when they are True."""
    notes: list[str] = []
    raw_actions = case.get("actions") if isinstance(case.get("actions"), dict) else {}
    actions = {key: raw_actions.get(key) is True for key in ACTION_KEYS}
    raw_licences = case.get("organisation") if isinstance(case.get("organisation"), dict) else {}
    raw_licences = raw_licences.get("licences") if isinstance(raw_licences.get("licences"), dict) else {}
    licences = {}
    for key in ("copilot_studio", "microsoft_365_copilot", "power_automate", "foundry"):
        value = raw_licences.get(key, "unknown")
        if value not in LICENCE_VALUES:
            notes.append(f"Licence {key} was not yes, no, or unknown. It was treated as unknown.")
            value = "unknown"
        licences[key] = value
    licences["github_copilot_service_only"] = raw_licences.get("github_copilot_service_only") is True

    raw_users = case.get("users") if isinstance(case.get("users"), dict) else {}
    audience = raw_users.get("audience", "internal_staff")
    if audience not in AUDIENCES:
        notes.append("Audience was not a known value. It was treated as internal staff.")
        audience = "internal_staff"
    channel = raw_users.get("channel", "teams")
    if channel not in CHANNELS:
        notes.append("Channel was not a known value. It was treated as none.")
        channel = "none"

    raw_data = case.get("data") if isinstance(case.get("data"), dict) else {}
    classification = raw_data.get("classification", "unknown")
    if classification not in CLASSIFICATIONS:
        notes.append("Classification was not a known value. It was treated as unknown, which is not secret.")
        classification = "unknown"
    volume = raw_data.get("volume", "bounded")
    if volume not in {"bounded", "large_files", "multi_source"}:
        notes.append("Volume was not a known value. It was treated as bounded.")
        volume = "bounded"
    residency = raw_data.get("residency", "unknown")
    if residency not in {"uk", "any", "unknown"}:
        residency = "unknown"

    raw_risk = case.get("risk") if isinstance(case.get("risk"), dict) else {}
    requested = raw_risk.get("requested_autonomy")
    if requested is not None and requested not in AUTONOMY_REQUESTS:
        notes.append("Requested autonomy was not A0, A1, A2, or A3. It was ignored.")
        requested = None
    level = raw_risk.get("level", "not_recorded")
    if level not in {"low", "medium", "high"}:
        level = "not_recorded"

    organisation = case.get("organisation") if isinstance(case.get("organisation"), dict) else {}
    normalised = {
        "case_id": str(case.get("case_id") or "unspecified"),
        "title": str(case.get("title") or ""),
        "organisation": {
            "name": str(organisation.get("name") or ""),
            "sector": str(organisation.get("sector") or "not_recorded"),
            "licences": licences,
        },
        "users": {"audience": audience, "channel": channel},
        "data": {
            "description": str(raw_data.get("description") or ""),
            "personal_data": raw_data.get("personal_data") is True,
            "special_category": raw_data.get("special_category") is True,
            "classification": classification,
            "volume": volume,
            "residency": residency,
        },
        "actions": actions,
        "risk": {
            "level": level,
            "significant_automated_decision": raw_risk.get("significant_automated_decision") is True,
            "requested_autonomy": requested,
            "named_approver": raw_risk.get("named_approver") is True,
            "approver_role": str(raw_risk.get("approver_role") or ""),
        },
        "narrative": str(case.get("narrative") or ""),
    }
    return normalised, notes
