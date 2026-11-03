# Copilot Studio standard harness

One topic. The FinOps owner points at a usage file and a rate card. The topic calls `report_agent_cost` and shows the JSON. Then it stops.

The standard harness, on the overview opened on 3 November 2026, powers rule-based agents and agent flows and follows the topics and rules the maker defines. This topic is that shape. There is no skill on this path. The GitHub Copilot harness for the same report is `docs/github-copilot-harness.md`. That harness is not the GitHub Copilot service.

The billing overview says the standard harness starts billing after publish. The cost-management page says standard-harness agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 channels, and billed when the user has no such licence or the channel is outside Microsoft 365. No quantity is copied. Confirm the tenant before anyone relies on that sentence. This starter does not look up a licence.

## Build it

1. Create an agent on the standard harness. Paste `copilot-studio/system-prompt.md` as the instructions.
2. Add one tool, `report_agent_cost`, that runs `src/report.py` with the two files and the as-of date. The contract is `schema/tools.json`.
3. Do not add a connector to the Power Platform admin centre, Azure Cost Management, a subscription, email, or Dataverse. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Ask for the usage file, the rate card, and the as-of date. In this repository the samples are `examples/sample_bundle.json` and `examples/sample_rate_card.json`. Both have `synthetic` true. If a file is not marked synthetic, the tool returns a refusal and no cost.
5. Show the label `DRAFT FOR FINOPS REVIEW`. Say that the FinOps owner validates rates and the forecast.
6. Stop. Do not offer to change a quota.

## Inputs

| Input | Required | What it is |
|---|---|---|
| `bundle` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `rate_card` | Yes | One JSON file with `effective_date` and string prices. Not a Microsoft price list. |
| `as_of` | Yes | The date the FinOps owner types, `YYYY-MM-DD`. |

## What this topic does not do

It does not validate the rates. It does not change a quota, a budget, or a subscription. It does not browse a pricing page. It does not add the period rollup to the agent lines.
