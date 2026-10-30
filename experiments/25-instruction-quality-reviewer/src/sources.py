"""Pinned harness sentences for the instruction reviewer.

Experiment 14 opened these pages on 27 October 2026 and stored the sentences.
Experiment 25 did not re-open them. last_verified stays that date.
reopened_for_this_experiment stays false. The reviewer does not download
the pages. No price, credit quantity, or pack size is stored.
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
        "body_opened_by": "experiment-14",
        "reopened_for_this_experiment": False,
        "stale_applicable": True,
        "notes": (
            "Stored by Experiment 14 after a page open on 27 October 2026. "
            "Not re-opened for Experiment 25. The page describes three harnesses. "
            "The GitHub Copilot harness is a Copilot Studio authoring and "
            "orchestration framework, not the GitHub Copilot service. It can take "
            "a goal, break it into steps, use skills and memory, create and edit "
            "files, and run in a sandbox. Agents on it use Copilot Credits. The "
            "page does not mark that harness as preview. Customer data is not sent "
            "to the GitHub Copilot service when the agent runs in Copilot Studio. "
            "That is Microsoft's statement, as stored. This repository cannot see "
            "a tenant's traffic."
        ),
    },
    {
        "id": "cs-choose-harness",
        "title": "Compare Copilot Studio agent harnesses",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-14",
        "reopened_for_this_experiment": False,
        "stale_applicable": True,
        "notes": (
            "Stored by Experiment 14. Not re-opened for Experiment 25. Choose the "
            "standard harness when the work is short and bounded. Choose the "
            "GitHub Copilot harness when the task is long-running or "
            "reasoning-intensive. The page says customers should validate features "
            "and channels as the experience matures. That is a maturity caveat, "
            "not a preview label on the harness. No rate is copied."
        ),
    },
    {
        "id": "cs-usage-billing",
        "title": "Overview of usage-based billing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-14",
        "reopened_for_this_experiment": False,
        "stale_applicable": True,
        "notes": (
            "Stored by Experiment 14. Not re-opened for Experiment 25. The GitHub "
            "Copilot harness charges Copilot Credits from the moment you start "
            "building, including testing. The standard harness starts billing after "
            "publish. No diagram and no rate from that page is copied."
        ),
    },
    {
        "id": "cs-gh-cost-management",
        "title": "Manage costs for agents powered by the GitHub Copilot harness",
        "url": "https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-14",
        "reopened_for_this_experiment": False,
        "stale_applicable": True,
        "notes": (
            "Stored by Experiment 14. Not re-opened for Experiment 25. Consumption "
            "for this harness is not included with a Microsoft 365 Copilot licence. "
            "Experiment 14 also stored a different sentence from the standard-harness "
            "licensing page. The two sentences are not merged. No quantity is copied. "
            "Developer environments and trial environments move to usage-based billing "
            "on 1 September 2026. That date is before the pin. Confirm the tenant."
        ),
    },
    {
        "id": "foundry-prompt-shields",
        "title": "Prompt Shields in Microsoft Foundry",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-14",
        "reopened_for_this_experiment": False,
        "stale_applicable": True,
        "notes": (
            "Stored by Experiment 14. Not re-opened for Experiment 25. User prompt "
            "attack detection is on by default. Document attack detection is off by "
            "default. Tool-response scanning and Spotlighting are marked preview. "
            "The page says the service is Azure AI Content Safety. This checker "
            "does not call Prompt Shields."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue boundary for this reviewer",
        "url": "",
        "last_verified": "2026-10-30",
        "body_opened_by": "experiment-25",
        "reopened_for_this_experiment": False,
        "stale_applicable": False,
        "notes": (
            "Not a Microsoft page. Autonomy of this reviewer is A0. The agent "
            "owner approves prompt changes. The reviewer does not apply a diff."
        ),
    },
]


def currency(as_of: str, stale_after_days: int = DEFAULT_STALE_AFTER_DAYS) -> list[dict]:
    """Mark a pinned page stale when it is older than the threshold.

    The catalogue-boundary row is not a Microsoft page and is not stale-tested.
    A page Experiment 25 did not re-open can still be inside the threshold.
    The report says it was not re-opened either way.
    """
    as_of_date = date.fromisoformat(as_of)
    rows = []
    for source in SOURCES:
        verified = date.fromisoformat(source["last_verified"])
        age = (as_of_date - verified).days
        stale = bool(source["stale_applicable"] and age > stale_after_days)
        row = dict(source)
        row["age_days"] = age
        row["stale"] = stale
        row["reopened_for_this_experiment"] = False
        rows.append(row)
    return rows
