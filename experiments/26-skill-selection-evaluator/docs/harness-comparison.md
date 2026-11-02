# Which harness runs this evaluator

Both harnesses call the same evaluator, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

This note is about running Experiment 26. It is not a decision about which harness a skill under review should use. If the bundle includes a structured use case, Experiment 14 may draft options. `platform_selected` stays null. The architect confirms that draft. This folder does not.

Pages stored from Experiment 14's open on 27 October 2026. Experiment 26 did not re-open them:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Compare Copilot Studio agent harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness)
- [Assign user licenses and manage access](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing)
- [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing)
- [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview)
- [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness)

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## Lead: GitHub Copilot harness

Use it when the maintainer drops in several skills and then asks follow-up questions: which pair is confusable, why an utterance tied, what the proposed description would add.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The comparison page describes longer-running tasks, larger files, agentic loops, and persistent memory. It also says customers should validate required features and channels as the experience matures. That is a maturity caveat. The overview does not mark the harness itself as preview.

This experiment's skills are under `skills/`. They tell the agent to call `evaluate_skill_routing` and to stop. They do not tell it to edit a skill or to apply the diff. Whether memory can be switched off was not on the page. The skills say not to store the skill text.

## Lighter path: standard harness

Use it when the maintainer wants the same topic every time: point at the skill files, point at the labelled utterances, run the evaluator, show the JSON, stop.

Microsoft's overview describes the standard harness for rule-based agents and structured conversations. The comparison page says to choose it when the work is relatively short and bounded and explicit control matters. The guide is `copilot-studio/README.md`. There is no skill on that path.

## Cost and licensing

Only what those pages say, as stored by Experiment 14. No prices are copied here. The billing overview had a diagram of ranges. The numbers on that diagram were not transcribed.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What Microsoft says it is for | Reasoning-heavy, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing page | Usage-based Copilot Credits. Credits cover model tokens, tools including knowledge and MCP, and the harness. Charged from the moment you start building, including testing and evaluation. | The billing overview says the standard harness starts billing after publish. |
| Microsoft 365 Copilot licence | The cost-management page says consumption is not included. Creation and runtime are billed regardless of the user's licence. The standard-harness licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for this harness. The two sentences are not merged. | The cost-management page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the channel is outside Microsoft 365. |

Developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before the pin. Confirm the tenant.

The Customer Conversation harness is described on the overview for customer voice and chat. It is not built in this folder.

## What both harnesses share

The deterministic Python core, `agent-manifest.yaml`, `schema/tools.json`, and the tests. A change to the router is a change to both. Neither harness is allowed to set `maintainer_validated` or `diff_applied`.
