"""Pinned Microsoft Learn pages for the architecture advisor.

The advisor does not download these pages. A person opened them on
27 October 2026. Update last_verified only after opening the page again.

Notes store the sentences the rules rely on. They do not store a price,
a credit quantity, a pack size, or a currency amount.
"""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-10-27"
DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: list[dict] = [
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [],
        "notes": (
            "Opened 27 October 2026. Three harnesses are described: GitHub Copilot "
            "for reasoning-heavy multi-step work, Customer Conversation for customer "
            "voice and chat, and standard for rule-based agents and agent flows. "
            "The GitHub Copilot harness can take a goal, break it into steps, call "
            "tools across connectors, knowledge, MCP, and connected agents, create "
            "and edit Word, Excel, PowerPoint, and PDF files, and it supports skills "
            "and memory. Each task runs in a sandbox governed by Copilot Studio. "
            "Agents on that harness use Copilot Credits. An important note says the "
            "GitHub Copilot harness is a Copilot Studio authoring and orchestration "
            "framework, not the GitHub Copilot service, and that customer data is "
            "not sent to the GitHub Copilot service. The page does not mark the "
            "GitHub Copilot harness itself as preview. The Customer Conversation "
            "harness is not one of the five options this advisor scores."
        ),
    },
    {
        "id": "cs-choose-harness",
        "title": "Compare Copilot Studio agent harnesses",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [
            "The page says customers should validate required features and channels as the experience matures. That is a maturity caveat, not a preview label on the harness."
        ],
        "notes": (
            "Opened 27 October 2026. Choose the standard harness when the work is "
            "relatively short and bounded and explicit control matters. Choose the "
            "GitHub Copilot harness when the task is long-running, coordination-heavy, "
            "or reasoning-intensive. The GitHub Copilot harness supports longer-running "
            "tasks, larger files and datasets, agentic loops, iterative reasoning, "
            "persistent memory, and a Bash container. The page says a more capable "
            "harness can overwork a simple problem, and that simple scenarios can "
            "add reasoning, latency, and Copilot Credit consumption. No rate is "
            "stored here. Both harnesses can keep a deterministic step: topics on "
            "the standard harness, workflows on the GitHub Copilot harness. "
            "Reasoning models and some emerging agentic capabilities are described "
            "as available only through the GitHub Copilot harness. Standard-harness "
            "agents are said to retain the pre-existing Copilot Studio licensing model. "
            "GitHub Copilot harness solutions are said to use usage-based billing."
        ),
    },
    {
        "id": "cs-assign-licences",
        "title": "Assign user licenses and manage access",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [],
        "notes": (
            "Opened 27 October 2026. The page says it describes the standard harness. "
            "It says creating and managing agents needs a user licence and a tenant "
            "licence, that users of a published agent do not need a special licence, "
            "and that a trial can be used in the test chat panel but cannot publish. "
            "It points to the Microsoft Copilot Studio Licensing Guide. That guide "
            "was not opened. No quantity is stored here."
        ),
    },
    {
        "id": "cs-standard-licensing",
        "title": "Standard harness licensing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [],
        "notes": (
            "Opened 27 October 2026. The page says it covers licensing for agents "
            "on the standard harness, and it distinguishes Azure Bot Service skills "
            "on that harness from agentic skills on the GitHub Copilot harness. "
            "It says Copilot Credits are the common currency, and that on "
            "1 September 2025 the common currency changed from messages to Copilot "
            "Credits. It says a Microsoft 365 Copilot licence lets you use Copilot "
            "Studio to build agents for the GitHub Copilot harness. It points to a "
            "licensing guide and a billing-rates page. Those were not used for "
            "figures. No quantity is stored here. Price words on the page are not stored."
        ),
    },
    {
        "id": "cs-usage-billing",
        "title": "Overview of usage-based billing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [],
        "notes": (
            "Opened 27 October 2026. The page says agents, workflows, and apps on "
            "the GitHub Copilot harness use usage-based billing measured in Copilot "
            "Credits. Credits cover model tokens, tools including knowledge and MCP, "
            "and the harness. Billing starts when you start building, including "
            "previewing, testing, and generating evaluations. The page says the "
            "standard harness starts billing after publish. A diagram of ranges was "
            "on the page and is not copied."
        ),
    },
    {
        "id": "cs-gh-cost-management",
        "title": "Manage costs for agents powered by the GitHub Copilot harness",
        "url": "https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [
            "Developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. Confirm the tenant."
        ],
        "notes": (
            "Opened 27 October 2026. The page says GitHub Copilot harness agents "
            "use consumption-based billing and that this usage is not included with "
            "a Microsoft 365 Copilot licence. Creation and runtime consume Copilot "
            "Credits regardless of the user's licence. It says standard-harness "
            "agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 "
            "channels, and billed when the user has no such licence or the channel "
            "is outside Microsoft 365. The Harness column in the admin centre shows "
            "GitHub Copilot, Standard, or Copilot Chat. Developer environments and "
            "trial environments move to usage-based billing on 1 September 2026. "
            "No credit amount is stored here. This page and the standard-harness "
            "licensing page do not use the same sentence about a Microsoft 365 "
            "Copilot licence and the GitHub Copilot harness. Both are kept."
        ),
    },
    {
        "id": "foundry-agent-service",
        "title": "What is Microsoft Foundry Agent Service?",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/agents/overview",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [
            "Agent optimizer is marked preview.",
            "Voice-based agents and some related monitoring, evaluation, avatar, WebRTC, and telephony capabilities are marked preview.",
            "A2A protocol v1.0 is described as generally available. v0.3 remains in preview.",
        ],
        "notes": (
            "Opened 27 October 2026. The page describes prompt agents, voice-based "
            "prompt agents, and hosted agents. Prompt agents are instructions, a "
            "model, and tools, run by Foundry with no application code. Hosted "
            "agents are your code, run as a container or from a zip file, with a "
            "managed endpoint, scaling, and a dedicated Microsoft Entra identity. "
            "Observability on the page includes tracing, evaluations, and "
            "Application Insights. Private networking is described for prompt "
            "agents. Hosted agents are described with bring-your-own virtual "
            "network. Content filters are described as mitigating prompt injection, "
            "including cross-prompt injection. The comparison table describes "
            "prompt-agent cost as per-call inference plus tool usage, and hosted "
            "agents as that plus container compute. It points to a pricing page "
            "for voice. That pricing page was not opened. No figure is stored. "
            "A list of UK regions was not on the page. Region availability is unverified. "
            "Agent optimizer is marked preview and is not a reason to choose the service."
        ),
    },
    {
        "id": "foundry-prompt-shields",
        "title": "Prompt Shields in Microsoft Foundry",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [
            "For Foundry Agent Service agents, document-attack scanning at the tool-response point is marked preview.",
            "Spotlighting is marked preview and is off by default. A cost note in that section is not copied.",
        ],
        "notes": (
            "Opened 27 October 2026. Prompt Shields detect user prompt attacks and "
            "document attacks. The page says they are part of Foundry guardrails. "
            "User prompt attack detection is on by default. Document attack "
            "detection is off by default. The page says Prompt Shields do not "
            "decide that content is harmful, accurate, grounded, or compliant. "
            "The local advisor does not call Prompt Shields. Its tests are the "
            "control on use-case text. The page says the service behind Prompt "
            "Shields is Azure AI Content Safety."
        ),
    },
    {
        "id": "pa-cloud-flows",
        "title": "Overview of cloud flows",
        "url": "https://learn.microsoft.com/en-us/power-automate/overview-cloud",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [],
        "notes": (
            "Opened 27 October 2026. Cloud flows connect apps and services. "
            "Without Copilot in the designer, the page lists three types: "
            "automated (an event, such as an email), instant (a button, with an "
            "approval in Teams or SharePoint given as an example), and scheduled. "
            "Copilot in the designer can suggest actions from a prompt and can be "
            "turned off by an admin. That authoring aid is not one of the five "
            "options. A cloud flow is not scored as an agent."
        ),
    },
    {
        "id": "pa-licence-types",
        "title": "Types of Power Automate licenses",
        "url": "https://learn.microsoft.com/en-us/power-platform/admin/power-automate-licensing/types",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "stale_applicable": True,
        "preview_labels": [],
        "notes": (
            "Opened 27 October 2026. The page describes user licences and capacity "
            "licences. It names Premium, Process, and Hosted Process, a 90-day "
            "trial, and a further user licence limited to standard connectors. "
            "It says other Microsoft 365, Dynamics 365, and Power Platform licences "
            "include a limited set of Power Automate capabilities, and it points "
            "to a licensing guide and a pricing page. Those were not opened. "
            "Quantities, storage sizes, and price words on the page are not stored. "
            "A recorded yes does not say which of these licences the organisation holds."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue autonomy boundary for this repository",
        "url": None,
        "last_verified": LAST_VERIFIED,
        "body_opened": False,
        "stale_applicable": False,
        "preview_labels": [],
        "notes": (
            "Not a Microsoft page. This repository permits autonomy A0, A1, and A2. "
            "A3 is never recommended. Secret material is not put into a generative "
            "agent by this catalogue. The architect confirms every platform option."
        ),
    },
]


def by_id(source_id: str) -> dict:
    for source in SOURCES:
        if source["id"] == source_id:
            return source
    raise KeyError(source_id)


def currency(as_of: str, stale_after_days: int = DEFAULT_STALE_AFTER_DAYS) -> list[dict]:
    opened = date.fromisoformat(as_of)
    rows = []
    for source in SOURCES:
        if source.get("stale_applicable", True):
            verified = date.fromisoformat(source["last_verified"])
            age = (opened - verified).days
            stale = age > stale_after_days
        else:
            age = None
            stale = False
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "body_opened": source["body_opened"],
                "age_days": age,
                "stale": stale,
                "preview_labels": list(source.get("preview_labels") or []),
                "notes": source["notes"],
            }
        )
    return rows
