"""Pinned pages opened for Experiment 28 on 2 November 2026.

The runner does not download the pages. Billing pages were not opened and
are not listed. No price and no credit quantity is stored.
"""

from __future__ import annotations

from datetime import date

DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: list[dict] = [
    {
        "id": "owasp-llm-top-10",
        "title": "OWASP Top 10 for LLM Applications, 2025 listing",
        "url": "https://genai.owasp.org/llm-top-10/",
        "last_verified": "2026-11-02",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Listing headings fetched on 2 November 2026. The ten titles are "
            "stored in src/owasp.py. The vulnerability essays were not opened. "
            "Text under each heading was truncated in the fetch and is not copied. "
            "The mapping from a suite class to a title is this starter's reading."
        ),
    },
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": "2026-11-02",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. The GitHub Copilot harness is a Copilot "
            "Studio authoring and orchestration framework, not the GitHub Copilot "
            "service. Customer data is not sent to the GitHub Copilot service when "
            "agents run in Copilot Studio. The harness can take a goal, break it "
            "into steps, use skills and memory, create and edit Word, Excel, "
            "PowerPoint, and PDF files, and run in a sandbox. Agents on it use "
            "Copilot Credits. No quantity is copied. The overview does not mark "
            "the harness as preview. The standard harness follows topics and rules "
            "the maker defines. The Customer Conversation harness is described for "
            "customer voice and chat and is not built here."
        ),
    },
    {
        "id": "foundry-ai-red-teaming-agent",
        "title": "AI Red Teaming Agent",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent",
        "last_verified": "2026-11-02",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. The page says the agent uses PyRIT and "
            "Microsoft Foundry Risk and Safety Evaluations to scan, score Attack "
            "Success Rate, and report. It says that rate can be non-deterministic "
            "and that results should be reviewed before mitigation. Agentic "
            "categories named for cloud runs include prohibited actions, sensitive "
            "data leakage, and task adherence, plus indirect prompt injection. "
            "Supported targets named on the page are Foundry-hosted prompt agents "
            "and container agents with Azure tool calls. Non-Foundry agents are "
            "listed as not supported. Cloud regions named: East US 2, France "
            "Central, Sweden Central, Switzerland West, and US North Central. A "
            "UK region was not in that list. This starter does not call the agent "
            "and does not compute Attack Success Rate."
        ),
    },
    {
        "id": "foundry-prompt-shields",
        "title": "Prompt Shields in Microsoft Foundry",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields",
        "last_verified": "2026-11-02",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. User prompt attack detection is on by "
            "default. Document attack detection is off by default. Tool-response "
            "scanning for agents, and Spotlighting, are marked preview. The page "
            "says the service is powered by Azure AI Content Safety, which is the "
            "name written there. This starter does not call Prompt Shields."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue row G006",
        "url": "",
        "last_verified": "2026-11-02",
        "reopened_for_this_experiment": False,
        "stale_applicable": False,
        "notes": (
            "Not a Microsoft page. Stack FND + CS-GH, autonomy A0, human "
            "checkpoint: a security reviewer assesses the findings. Not stale-tested."
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
