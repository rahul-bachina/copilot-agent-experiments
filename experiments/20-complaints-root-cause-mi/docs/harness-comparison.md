# Which harness

Both harnesses call the same `draft_report()`, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 29 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

A last-updated date was not in the text retrieved for this experiment.

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement.

The overview describes three harnesses. This experiment uses two of them. It does not use the Customer Conversation harness. This draft is internal management information, not a public chat.

| Harness | Used here | What the overview says it is for |
|---|---|---|
| GitHub Copilot harness | Yes. Two skills around `draft_report()`. | Reasoning-heavy, multi-step work. Files, skills, and memory. |
| Standard harness | Yes. One topic and one flow, for a complaints owner. | Rule-based agents. You define the topics and paths. |
| Customer Conversation harness | No. | Customer voice and chat, with escalation to a person. |

These were not opened on 29 October 2026:

- The billing overview linked from the GitHub Copilot harness row of the comparison table
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill

## When to use the GitHub Copilot harness

Use it when the complaints owner wants to work through one awkward batch: run the draft, then ask which comment held an instruction, why a record is unassigned, or why a figure is not a rate.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The GitHub Copilot harness section says agents and workflows on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened. No price is copied here.

The overview did not use the word preview for the harness. The skills page it links to was not opened. Treat the authoring click-path as something to confirm in the tenant. Do not upload these skills onto a standard-harness agent.

## When to use the standard harness

Use it when every batch goes through the same topic: paste the JSON, run the draft, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "Not a focus". That matches this report. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion. The comparison-table cell for the standard harness says "Described in Licensing for agents powered by the standard harness". The Customer Conversation cell says "Copilot Credits (usage-based)". This experiment does not use that harness.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | The harness section says Copilot Credits. The comparison table points at a billing overview, which was not opened. | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page opened on 29 October 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

Credit ranges and stop-usage controls were on pages that were not opened for this experiment. Confirm them in the tenant before a build consumes credits.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/report.py` is the only producer of the clusters, the figures, the narrative, the injection record, and the stale flag.
- Experiment 02 `analyse()` and Experiment 08 `propose()` are called from that core. Neither harness reimplements them.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A0 on both. The complaints owner validates the clusters and the narrative. Neither harness is given a tool that does that, confirms compliance, or submits a return.
