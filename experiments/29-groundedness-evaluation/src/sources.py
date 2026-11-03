"""Pinned pages opened for Experiment 29 on 3 November 2026.

The checker does not download the pages. Billing pages were not opened and
are not listed. No price and no credit quantity is stored.
"""

from __future__ import annotations

from datetime import date

DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: list[dict] = [
    {
        "id": "foundry-rag-evaluators",
        "title": "Retrieval-Augmented Generation (RAG) Evaluators for Generative AI",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators",
        "last_verified": "2026-11-03",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The comparison table calls Groundedness a "
            "system evaluation for a well-rounded groundedness definition that works "
            "with agent inputs, using the caller's own GPT models as the LLM-judge. "
            "It measures how well the generated response aligns with the given context "
            "without fabricating content, and it calls that the precision aspect. The "
            "output column says binary pass or fail based on a threshold on a 1-5 scale. "
            "The example-output section says these evaluators return scores from 1 to 5, "
            "where 1 is very poor and 5 is excellent, and that the default pass threshold "
            "is 3. Scores at or above the threshold are considered passing. The example "
            "object shows score 4, threshold 3, and passed true. Required inputs on the "
            "page are response and context, with context described as optional and "
            "recommended, and query optional for enhanced scoring. A second input shape "
            "is query and response for agent response mode, plus tool_definitions. The "
            "required parameter is deployment_name. A tip says that for best Groundedness "
            "results the caller should provide query, response, and context. "
            "Groundedness Pro is marked preview. The table says it is a strict definition "
            "powered by Azure AI Content Safety, and the output column says binary true "
            "or false. Required inputs are query, response, and context. Required "
            "parameters are none. The example for Groundedness Pro has a label and passed, "
            "and no numeric score. The page says Groundedness Pro uses the Azure AI "
            "Content Safety service. No UK region is named on the page. This starter "
            "does not call either evaluator and does not map its own rate onto the 1-5 scale."
        ),
    },
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": "2026-11-03",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 3 November 2026. The GitHub Copilot harness is a Copilot "
            "Studio authoring and orchestration framework, not the GitHub Copilot "
            "service. Customer data is not sent to or processed by the GitHub "
            "Copilot service when agents run in Copilot Studio. The harness can "
            "take a goal, break it into steps, call tools across connectors, "
            "knowledge, MCP, and connected agents, create and edit Word, Excel, "
            "PowerPoint, and PDF files, and use skills and memory. Each task runs "
            "in a sandbox governed by Copilot Studio. Agents and workflows on it "
            "use Copilot Credits. No quantity is copied. The overview does not mark "
            "the harness as preview. The standard harness follows the topics and "
            "rules the maker defines. The Customer Conversation harness is described "
            "for customer voice and chat and is not built here. An administrator "
            "control to turn memory off was not on the page. Billing pages linked "
            "from the overview were not opened."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue row G007",
        "url": "",
        "last_verified": "2026-11-03",
        "reopened_for_this_experiment": False,
        "stale_applicable": False,
        "notes": (
            "Not a Microsoft page. Stack FND, autonomy A0, human checkpoint: an "
            "evaluation owner approves thresholds. Experiment 03 keeps a narrower "
            "G007 check inside the assurance pack. Not stale-tested."
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
