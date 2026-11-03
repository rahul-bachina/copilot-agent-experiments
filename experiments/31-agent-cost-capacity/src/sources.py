"""Microsoft Learn sentences opened for this experiment on 3 November 2026.

No price, pack size, or credit quantity from those pages is stored.
reopened_for_this_experiment is true only for pages fetched that day.
The catalogue row is not a Microsoft page and is not stale-tested.
"""

from __future__ import annotations

LAST_VERIFIED = "2026-11-03"
DEFAULT_STALE_AFTER_DAYS = 90

# Caller-supplied forecast band used only when the bundle does not set one.
# It is not a Microsoft estimate and it is not a statistical interval.
DEFAULT_FORECAST_BAND = "0.20"
DEFAULT_HEADROOM_TIGHT_BELOW = "0.15"
DEFAULT_SPIKE_MULTIPLE = "3"
MIN_AGENTS_FOR_SPIKE = 3

SOURCES: list[dict] = [
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened 3 November 2026. The GitHub Copilot harness is a Copilot "
            "Studio authoring and orchestration framework, not the GitHub "
            "Copilot service. Customer data is not sent to or processed by the "
            "GitHub Copilot service when agents run in Copilot Studio. The "
            "standard harness powers rule-based agents and agent flows and "
            "follows the topics and rules the maker defines. Agents on the "
            "GitHub Copilot harness use Copilot Credits. The page does not mark "
            "that harness as preview. No rate is copied."
        ),
    },
    {
        "id": "cs-usage-billing",
        "title": "Overview of usage-based billing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview",
        "last_verified": LAST_VERIFIED,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened 3 November 2026. Agents, workflows, and apps powered by the "
            "GitHub Copilot harness use usage-based billing measured in Copilot "
            "Credits. For those experiences, Copilot Credits are charged for "
            "large language model tokens, tools including knowledge and MCP, "
            "and the harness. The standard harness starts billing after publish. "
            "The GitHub Copilot harness charges credits from the moment you "
            "start building, including testing and evaluation. A diagram of "
            "ranges was on the page. No number from that diagram is copied. "
            "The article's scope statement covers the GitHub Copilot harness "
            "and customer conversations, not the standard harness."
        ),
    },
    {
        "id": "cs-gh-cost-management",
        "title": "Manage costs for agents powered by the GitHub Copilot harness",
        "url": "https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness",
        "last_verified": LAST_VERIFIED,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened 3 November 2026. GitHub Copilot harness consumption is not "
            "included with a Microsoft 365 Copilot licence. Creation and runtime "
            "are billed regardless of the user's licence. The same page says "
            "standard-harness agents are covered in Microsoft 365 channels, and "
            "billed when the user has no such licence or the channel is outside "
            "Microsoft 365. Azure budgets and alerts send notifications but do "
            "not stop Copilot Studio consumption. An agent monthly limit can "
            "stop usage when that control is turned on. That control is not "
            "called here. Developer environments and trial environments move to "
            "usage-based billing on 1 September 2026. The page says non-billed "
            "credit information is not a billing estimate. No quantity is copied."
        ),
    },
    {
        "id": "cs-standard-licensing",
        "title": "Standard harness licensing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing",
        "last_verified": LAST_VERIFIED,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened 3 November 2026. Copilot Credits are the common currency "
            "across Copilot Studio capabilities. The page says the currency "
            "changed from messages to Copilot Credits on 1 September 2025. Pack "
            "sizes and pay-as-you-go rates are not copied. The page says a "
            "Microsoft 365 Copilot licence lets you use Copilot Studio to build "
            "agents for the GitHub Copilot harness. That sentence is not merged "
            "with the cost-management page, which says consumption for that "
            "harness is not included. The Licensing Guide and the billing-rates "
            "article named on the page were not opened. Those rates are unverified."
        ),
    },
    {
        "id": "foundry-manage-costs",
        "title": "Plan and manage costs in Microsoft Foundry",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs",
        "last_verified": LAST_VERIFIED,
        "reopened_for_this_experiment": True,
        "stale_applicable": True,
        "notes": (
            "Opened 3 November 2026. Foundry resources are charged for the "
            "Azure services used. Pay-as-you-go is described as billed according "
            "to usage. Token billing units and rates vary by model, deployment "
            "type, and meter. The page points at a pricing page for current "
            "rates. No rate is copied. The invoice and the meter records are "
            "the source of truth. Foundry has no dedicated page in the Azure "
            "pricing calculator because it is composed of optional services. "
            "Cost records can be delayed. Provisioned throughput hourly billing "
            "was not opened in full for this experiment and is unverified here."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue row G009",
        "url": "",
        "last_verified": LAST_VERIFIED,
        "reopened_for_this_experiment": False,
        "stale_applicable": False,
        "notes": (
            "Not a Microsoft page. Catalogue ID G009. Autonomy A0. The FinOps "
            "owner validates rates and the forecast. The catalogue stack is "
            "Fabric and Power Platform. This starter does not connect to Fabric. "
            "The score in the catalogue is marked as an estimate and is not "
            "repeated here."
        ),
    },
]

ASSUMPTIONS: list[dict] = [
    {
        "id": "B1",
        "text": (
            "A Copilot Studio agent is priced only from its copilot_credits "
            "quantity times one matching rate-card line. Input tokens, output "
            "tokens, tool calls, and conversations on that agent are usage. "
            "They are not added unless that rate line sets additive to true. "
            "The usage-based billing overview opened on 3 November 2026 says "
            "Copilot Credits for GitHub Copilot harness experiences are charged "
            "for large language model tokens, tools, and the harness. That "
            "sentence is about that harness. Using the same non-additive rule "
            "for the standard harness is this starter's double-count guard, "
            "not that sentence."
        ),
    },
    {
        "id": "B2",
        "text": (
            "A Microsoft Foundry agent is priced only from input_tokens and "
            "output_tokens lines that match the platform and, when the line "
            "names one, the model deployment. Copilot Credits on a Foundry row "
            "are not priced. No Microsoft token price is stored. If tokens and "
            "foundry_usage disagree, the meter is not priced and the two "
            "quantities are not added together."
        ),
    },
    {
        "id": "B3",
        "text": (
            "The period total is the sum of agent costs after duplicate agent "
            "ids are dropped. The first row is kept. A period_rollup figure is "
            "compared and is never added. A rate card embedded in the telemetry "
            "file is ignored."
        ),
    },
    {
        "id": "B4",
        "text": (
            "A missing rate, two matching rates, a negative quantity, or a "
            "JSON float leaves that cost null. Null is not stored as zero. "
            "totals.cost is null when any used agent is incomplete. "
            "partial_cost adds only the complete agents and is not the total."
        ),
    },
    {
        "id": "B5",
        "text": (
            "The currency code comes from the rate card. Nothing in the code "
            "fills one in. price_per_unit has to be a string."
        ),
    },
    {
        "id": "B6",
        "text": (
            "The forecast multiplies the period cost by horizon_days divided "
            "by the inclusive day count of the observed period. It assumes the "
            "same daily run-rate and the same mix. Low and high are that point "
            "times one minus the band and one plus the band. The band is 0.20 "
            "only when the caller does not set one. It is not a statistical "
            "interval and it is not a Microsoft estimate."
        ),
    },
    {
        "id": "B7",
        "text": (
            "A rate card is stale when as_of minus effective_date is more than "
            "stale_after_days. The default threshold is 90 days. A stale card "
            "is still applied so the arithmetic can be seen, and do_not_rely "
            "is true. A card dated after as_of is not applied."
        ),
    },
    {
        "id": "B8",
        "text": (
            "rates_validated and forecast_validated stay false. quota_changed, "
            "budget_changed, and subscription_changed stay false. The FinOps "
            "owner validates rates and the forecast outside this tool. The "
            "tool does not change a quota, a budget, or a subscription."
        ),
    },
]
