# Which harness

Both harnesses call the same register, the same manifest, and the same tests. The difference is who the agent is for, and how much reasoning sits around that call.

Pages opened on 24 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview)
- [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness)
- [Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)
- [Add and manage an uploaded skill](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing)

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

There is a third harness, Customer Conversation, for customer voice and chat. This experiment does not use it. Staff policy questions are an internal topic, not a public contact centre.

## Lead: standard harness

Use it for the member of staff. The question types are known. The path is the same every time: pass the question and the as-of date, show the JSON, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". The costs page says standard-harness agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 channels. That matches a staff assistant inside Teams or Microsoft 365. The guide is `copilot-studio/README.md`. There is no skill on that path, and there is no SharePoint knowledge source. The register is the only source.

## Policy-owner path: GitHub Copilot harness

Use it when a policy owner wants the agent to work through the register: coverage, conflicts, stale policies, and a draft change note in the sandbox.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The upload page says a skill file has the name and description in YAML front matter, then Markdown instructions. It links to "Create an agent (preview)". That article was not opened. Treat the authoring click-path as preview. The harness overview page itself did not use the word preview for the harness.

The skills under `skills/` tell the agent to call `src/review.py` and to stop. They do not tell it to publish a policy.

## Cost and licensing

Only what those pages say. No prices are copied here. The billing overview shows a diagram of credit ranges by task complexity. The numbers on that diagram were not transcribed.

| | Standard harness (staff Q&A, the lead) | GitHub Copilot harness (policy owner) |
|---|---|---|
| What Microsoft says it is for | Rule-based agents and structured conversations | Longer, multi-step work, tools, files, skills |
| Billing page | The billing overview says the standard harness starts billing after publish. The costs page says it is covered by a Microsoft 365 Copilot licence in Microsoft 365 channels, and billed when the user has no such licence or the agent is used outside Microsoft 365. | Usage-based Copilot Credits. The billing overview says credits cover LLM tokens, tools (including knowledge and MCPs), and the harness, and that this harness charges from the moment you start building, including testing and evaluation. The costs page says a Microsoft 365 Copilot licence does not cover it. |
| Stopping spend | The costs page says the capacity controls apply across Copilot Studio, not only to one harness. | An administrator can set an agent monthly limit and turn on stop-usage. Azure budgets and alerts on pay-as-you-go notify. The page says they do not stop Copilot Studio consumption. |

The costs page, opened 24 October 2026, has a section titled "Prepare for the end of preview billing". It says developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. The page still describes steps to take before that date. Confirm the tenant. This starter does not know a tenant's billing state.

The full article "Licensing for agents powered by the standard harness", linked from the harness overview, was not opened. Do not treat the table above as a complete licence opinion.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/answer.py` is the only producer of staff quotations, refusals, and "I don't know".
- `src/review.py` is the only producer of coverage, conflict rows, stale flags, and change notes.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A0 on both. Neither harness is given a tool that approves a source, publishes a note, writes a production record, sends, spends, or answers from a clinical system.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the register. An administrator control to disable memory was not found on the pages opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control, described in the security note, and is not applied here.
- Customer Conversation harness. Not used.
