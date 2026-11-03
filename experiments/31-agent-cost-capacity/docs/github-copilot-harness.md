# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness, as described on the harness overview opened on 3 November 2026. It is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. Customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement.

The overview says agents on this harness use Copilot Credits, can use skills and memory, can create and edit files, and run each task in a sandbox. The page does not mark the harness as preview. It does not describe a control to turn memory off. The skills below say not to store the telemetry or the rate card.

The billing overview says this harness charges Copilot Credits from the moment you start building, including testing, and that those credits are charged for large language model tokens, tools, and the harness. The cost-management page says that consumption is not included with a Microsoft 365 Copilot licence. The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for this harness. The two sentences are not merged. No quantity is copied.

## Skills

Run them in this order. Each one stops.

1. `skills/read-usage-and-rate-card/SKILL.md` reads the two files.
2. `skills/report-agent-cost/SKILL.md` calls `report_agent_cost` and shows the JSON.
3. `skills/explain-cost-report/SKILL.md` reads that JSON and names the approval points.

The tool contract is `schema/tools.json`. `record_rate_validation`, `record_forecast_validation`, `change_quota`, `change_budget`, and `change_subscription` always raise. They are not attached.

## What the maker does not add

- A connector to the Power Platform admin centre, Azure Cost Management, or a subscription.
- A tool that buys Copilot Credits.
- A tool that writes a quota, a budget, or a Dataverse row.
- A pricing-page browse, including learn.microsoft.com.

If a tool is not in `agent-manifest.yaml`, it should not be on the agent.

## Approval

Showing the JSON does not need approval. The FinOps owner validates rates and the forecast outside the agent. A stale card or a stale pin is re-opened before anyone relies on a figure. A quota, budget, or subscription change is an administrator's action outside this agent, or it does not happen.
