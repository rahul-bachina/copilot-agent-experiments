# Which harness

Both harnesses call the same checker, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Pages opened on 30 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview)
- [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness)
- [Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)
- [Add and manage an uploaded skill](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## Lead: GitHub Copilot harness

Use it when the reviewer drops in a draft and wants the agent to work through it: read the text, call the checker, and leave a draft file in the sandbox.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The skills overview says a skill is a name, a description, and Markdown instructions. The upload page says an upload is a Markdown file, or a zip that contains `SKILL.md`, with the name and description in YAML front matter. That page's prerequisite still links to an article titled "Create an agent (preview)". That article was not opened. Treat the authoring click-path as preview unless the tenant's own documentation says otherwise. The harness overview page itself, on the day it was opened, did not use the word preview for the harness.

This experiment's skills are under `skills/`. They tell the agent to call the checker and to stop. They do not tell it to approve a promotion or to draft a replacement.

## Lighter path: standard harness

Use it when the reviewer wants the same topic every time: paste one draft, type the as-of date, run the checker, show the JSON, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. The comparison table says files, skills, and memory are "Not a focus" on this harness. That matches this intake. The guide is `copilot-studio/README.md`. There is no skill on that path.

## Cost and licensing

Only what those pages say. No prices are copied here. The billing overview shows a diagram of credit ranges by task complexity. The numbers on that diagram were not transcribed.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What Microsoft says it is for | Longer, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing page | Usage-based Copilot Credits. Credits cover LLM tokens, tools (including knowledge and MCPs), and the harness. Charged from the moment you start building, including testing and evaluation. | The billing overview says the standard harness starts billing after publish. |
| Microsoft 365 Copilot licence | The costs page says GitHub Copilot harness agents are not covered. Creation and runtime consume Copilot Credits regardless of the user's licence. | The same page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the agent is used outside Microsoft 365. |
| Stopping spend | An administrator can set an agent monthly limit and turn on stop-usage. Azure budgets and alerts on pay-as-you-go notify. The page says they do not stop Copilot Studio consumption. | The capacity controls are described as applying across Copilot Studio, not only to one harness. |

The costs page, opened 30 October 2026, has a section titled "Prepare for the end of preview billing". It says developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. Confirm the tenant. This starter does not know a tenant's billing state.

The full article "Licensing for agents powered by the standard harness", linked from the harness overview, was not opened. Do not treat the table above as a complete licence opinion.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/precheck.py` is the only producer of the checklist, the citations, and the stale-data flag.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A0 on both. Neither harness is given a tool that approves, publishes, rewrites, or gives a compliance opinion.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the draft as an approval. An administrator control to disable memory was not found on the pages opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control, described in the security note, and is not applied here.
- Customer Conversation harness. The overview describes it for customer voice and chat. This experiment does not use it. A customer asking the agent whether a promotion is allowed would be a different product, and this agent does not give that opinion.
