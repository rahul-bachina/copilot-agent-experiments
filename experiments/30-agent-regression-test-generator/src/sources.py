"""Pages opened for Experiment 30 on 3 November 2026.

The generator does not download the pages. Billing pages, Prompt Shields,
Entra Agent ID, Conditional Access, Purview, and Key Vault were not opened
and are not listed. No price and no credit quantity is stored.
"""

from __future__ import annotations

from datetime import date

DEFAULT_STALE_AFTER_DAYS = 90
VERIFIED_ON = "2026-11-03"

SOURCES: list[dict] = [
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": VERIFIED_ON,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The GitHub Copilot harness is a Copilot "
            "Studio authoring and orchestration framework, not the GitHub Copilot "
            "service. Customer data is not sent to or processed by the GitHub "
            "Copilot service when agents run in Copilot Studio. The harness can "
            "take a goal, break it into steps, call tools, use skills and memory, "
            "create and edit Word, Excel, PowerPoint, and PDF files, and run in a "
            "sandbox. Agents and workflows on it use Copilot Credits. No quantity "
            "is copied. The overview does not mark the harness as preview. The "
            "standard harness follows topics and rules the maker defines. The "
            "Customer Conversation harness is described for customer voice and "
            "chat and is not built here."
        ),
    },
    {
        "id": "cs-generative-orchestration",
        "title": "Orchestrate agent behavior with generative AI",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions",
        "last_verified": VERIFIED_ON,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The page says it describes features used "
            "in agents or agent flows powered by the standard harness. Generative "
            "orchestration selects topics based on the description of their "
            "purpose. Classic orchestration selects topics based on matching a "
            "user query with trigger phrases. The most important factor named "
            "for selection is the description. This generator does not implement "
            "either selector and does not assign a routing weight. Whether the "
            "GitHub Copilot harness uses the same rule was not on this page. "
            "That point is unverified."
        ),
    },
    {
        "id": "foundry-evaluate-agent",
        "title": "Evaluate your AI agents",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent",
        "last_verified": VERIFIED_ON,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The page describes an agent-targeted "
            "evaluation against a Foundry agent or hosted agent. A dataset line "
            "is a JSON object with a query field. The service sends each query "
            "to the agent. A rubric evaluator is described as the recommended "
            "primary measure, with built-in evaluators layered on. The page "
            "gives an 85 percent task-adherence passing rate as an example of a "
            "threshold a team might set. This generator does not set a threshold. "
            "The page says some features, including rubric generation and risk "
            "and safety evaluators, have regional restrictions, and points at "
            "another page for the list. That region page was not opened. UK "
            "region availability is unverified. This generator does not call "
            "the service."
        ),
    },
    {
        "id": "foundry-agent-evaluators",
        "title": "Agent evaluators",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators",
        "last_verified": VERIFIED_ON,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The page says items marked preview are "
            "in preview and are not recommended for production workloads. Task "
            "Completion, Customer Satisfaction, Task Adherence, and Intent "
            "Resolution are marked preview. Task Navigation Efficiency, Tool "
            "Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output "
            "Utilization, and Tool Call Success are not marked preview in the "
            "table. Output Quality and Tool Use Quality are marked preview. "
            "Quality Grader is described as deprecated and no longer runnable. "
            "This generator does not run any of them."
        ),
    },
    {
        "id": "foundry-hosted-eval-quickstart",
        "title": "Quickstart: Evaluate your hosted agent",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent",
        "last_verified": VERIFIED_ON,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The page says the Azure Developer CLI "
            "evaluation experience is currently in preview. It says evaluation "
            "runs against a deployed, invokable hosted agent. The eval.yaml "
            "example points dataset.local_uri at a JSONL file of query objects "
            "and lists built-in evaluators. This generator does not deploy an "
            "agent and does not run that command."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue row G008",
        "url": "",
        "last_verified": VERIFIED_ON,
        "reopened_for_this_experiment": False,
        "stale_applicable": False,
        "notes": (
            "Not a Microsoft page. Stack in the catalogue is Microsoft Foundry "
            "plus GitHub. Autonomy A1. Human checkpoint: a maintainer approves "
            "generated tests and the pull request. Not stale-tested."
        ),
    },
]


def currency(as_of: str, stale_after_days: int = DEFAULT_STALE_AFTER_DAYS) -> list[dict]:
    opened = date.fromisoformat(as_of)
    rows = []
    for source in SOURCES:
        verified = date.fromisoformat(source["last_verified"])
        age = (opened - verified).days
        stale = bool(source["stale_applicable"] and age > stale_after_days)
        row = dict(source)
        row["age_days"] = age
        row["stale"] = stale
        rows.append(row)
    return rows
