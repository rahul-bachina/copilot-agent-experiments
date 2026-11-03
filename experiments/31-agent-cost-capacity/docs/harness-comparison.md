# Which harness runs this report

Both harnesses call the same report, the same manifest, and the same tests. The difference is how much reasoning sits around that call. Neither harness selects a platform for the agents being costed. The telemetry already names each row's platform. This folder does not change that label.

Pages opened on 3 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview)
- [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness)
- [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing)
- [Plan and manage costs in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs)

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## GitHub Copilot harness

Use it when the FinOps owner drops in a usage file and a rate card and then asks follow-up questions: which agent is incomplete, why a token line was not priced, what the forecast assumes.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The overview does not mark the harness itself as preview. The page does not describe a control to turn memory off. The skills say not to store the telemetry or the rate card.

This experiment's skills are under `skills/`. They tell the agent to call `report_agent_cost` and to stop. They do not tell it to validate the rates or to change a quota.

## Standard harness

Use it when the FinOps owner wants the same topic every time: point at the usage file, point at the rate card, run the report, show the JSON, stop.

Microsoft's overview says the standard harness powers rule-based agents and agent flows, and that it follows the topics and rules the maker defines. The guide is `copilot-studio/README.md`. There is no skill on that path.

## Cost and licensing

Only what those pages said on 3 November 2026. No prices are copied here. The billing overview had a diagram of ranges. The numbers on that diagram were not transcribed.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What Microsoft says it is for | Reasoning-heavy, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing page | Usage-based Copilot Credits. For these experiences, credits are charged for large language model tokens, tools including knowledge and MCP, and the harness. Charged from the moment you start building, including testing and evaluation. | The billing overview says the standard harness starts billing after publish. The cost-management page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the channel is outside Microsoft 365. |
| Microsoft 365 Copilot licence | The cost-management page says consumption is not included. Creation and runtime are billed regardless of the user's licence. The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for this harness. The two sentences are not merged. | See the cost-management sentence in the cell above. |

Developer environments and trial environments move to usage-based billing on 1 September 2026. The cost-management page says non-billed credit information is not a billing estimate. This starter does not look at a tenant, so it does not say whether that change has taken effect for anyone.

The licensing page says the common currency changed from messages to Copilot Credits on 1 September 2025. Pack sizes and pay-as-you-go rates were not opened. They are unverified.

Azure budgets and alerts send notifications but do not stop Copilot Studio consumption. An agent monthly limit can stop usage when that control is turned on in the admin centre. This starter does not call that control. Headroom in the JSON is not that limit.

This starter's own rule, assumption B1, prices a Copilot Studio row from Copilot Credits only unless the rate card marks another line additive. The billing overview's "credits cover tokens and tools" sentence is about the GitHub Copilot harness. Using the same guard on the standard harness is this starter's double-count rule, not that sentence.

Microsoft Foundry model usage is a separate meter. The Foundry cost page says token rates vary by model, deployment type, and meter. No rate is copied. The rate card is the only price this command will use.

The Customer Conversation harness is described on the overview for customer voice and chat. It is not built in this folder.

## What both harnesses share

The deterministic Python core, `agent-manifest.yaml`, `schema/tools.json`, and the tests. A change to the pricing rule is a change to both. Neither harness is allowed to set `rates_validated`, `forecast_validated`, `quota_changed`, `budget_changed`, or `subscription_changed`.
