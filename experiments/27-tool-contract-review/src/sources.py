"""Pinned pages for the tool-contract reviewer.

The pages below were opened on 2 November 2026. The reviewer does not
download them. No price, credit quantity, or recommended call volume is stored.
The 20-calls example on the rate-limit page is not a limit this reviewer sets.
"""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-11-02"
DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: list[dict] = [
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. The GitHub Copilot harness is a Copilot "
            "Studio authoring and orchestration framework, not the GitHub Copilot "
            "service. The page says it can take a goal, break it into steps, call "
            "tools across connectors, knowledge, MCP, and connected agents, create "
            "and edit Word, Excel, PowerPoint, and PDF files, and support skills "
            "and memory. Agents and workflows on it use Copilot Credits. No "
            "quantity is copied. The page does not mark that harness as preview. "
            "It says customer data is not sent to or processed by the GitHub "
            "Copilot service when agents run in Copilot Studio. That is Microsoft's "
            "statement. This repository cannot see a tenant's traffic."
        ),
    },
    {
        "id": "cs-choose-harness",
        "title": "Compare Copilot Studio agent harnesses",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. Choose the standard harness when the work "
            "is relatively short and bounded. Choose the GitHub Copilot harness "
            "when the task is long-running or reasoning-intensive. Customers should "
            "validate required features and channels as the experience matures. "
            "GitHub Copilot harness solutions use usage-based billing for AI-based "
            "creation and use. Standard harness agents retain the pre-existing "
            "Copilot Studio licensing model. No rate is copied. The billing "
            "overview was not opened for this experiment."
        ),
    },
    {
        "id": "apim-policies",
        "title": "Azure API Management policy reference",
        "url": "https://learn.microsoft.com/en-us/azure/api-management/api-management-policies",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. Limit call rate by subscription and set "
            "usage quota by subscription depend on the subscription key. Limit "
            "call rate by key is listed as not supported on the Consumption "
            "gateway. Authenticate with managed identity is listed as not "
            "supported on the workspace gateway. Validate Microsoft Entra token, "
            "Validate JWT, and Validate parameters are listed. The element name "
            "for limit-by-key was not on this page, so proposed XML uses rate-limit "
            "only."
        ),
    },
    {
        "id": "apim-rate-limit",
        "title": "API Management rate-limit policy",
        "url": "https://learn.microsoft.com/en-us/azure/api-management/rate-limit-policy",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. The rate-limit policy limits call rate per "
            "subscription. Above the limit the caller receives HTTP 429. calls and "
            "renewal-period are required. renewal-period is seconds and the maximum "
            "allowed value is 300. Policy expressions are not allowed for those "
            "attributes. The policy is only applied when an API is accessed using "
            "a subscription key. The page says rate limiting is never completely "
            "accurate. The example of 20 calls per 90 seconds is not a limit this "
            "reviewer sets."
        ),
    },
    {
        "id": "apim-authentication-managed-identity",
        "title": "API Management authentication-managed-identity policy",
        "url": "https://learn.microsoft.com/en-us/azure/api-management/authentication-managed-identity-policy",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. The policy obtains a token for the managed "
            "identity and sets Authorization: Bearer. Omitting client-id on a "
            "managed gateway uses the system-assigned identity. The customer is "
            "responsible for forwarding the token only to an intended backend. "
            "The usage line lists classic, v2, consumption, and self-hosted. The "
            "policy index lists the workspace gateway as not supported. Both "
            "statements are what the pages said."
        ),
    },
    {
        "id": "apim-validate-parameters",
        "title": "API Management validate-parameters policy",
        "url": "https://learn.microsoft.com/en-us/azure/api-management/validate-parameters-policy",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened on 2 November 2026. The policy validates header, query, or "
            "path parameters against the API schema. Actions are ignore, prevent, "
            "and detect. A prevent action on an inbound policy returns HTTP 400. "
            "The maximum schema size stated for the validation policy is 4 MB. "
            "The page says validation can reduce throughput and recommends load "
            "tests. This reviewer does not run one."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue boundary for this reviewer",
        "url": "",
        "last_verified": LAST_VERIFIED,
        "body_opened_by": "experiment-27",
        "reopened_for_this_experiment": False,
        "stale_applicable": False,
        "notes": (
            "Not a Microsoft page. Autonomy of this reviewer is A0. The "
            "security/API owner approves the contract. The reviewer does not "
            "modify a contract, publish a policy, or deploy."
        ),
    },
]


def currency(as_of: str, stale_after_days: int = DEFAULT_STALE_AFTER_DAYS) -> list[dict]:
    """Mark a pinned page stale when it is older than the threshold."""
    as_of_date = date.fromisoformat(as_of)
    rows = []
    for source in SOURCES:
        verified = date.fromisoformat(source["last_verified"])
        age = (as_of_date - verified).days
        stale = bool(source["stale_applicable"] and age > stale_after_days)
        row = dict(source)
        row["age_days"] = age
        row["stale"] = stale
        rows.append(row)
    return rows
