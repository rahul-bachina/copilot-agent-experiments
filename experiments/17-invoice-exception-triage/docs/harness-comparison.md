# Which harness

Both harnesses call the same triage, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page retrieved on 28 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page did not use the word preview for the harness itself.

The overview describes three harnesses. This experiment uses two of them.

| Harness | Used here | What the overview says it is for |
|---|---|---|
| GitHub Copilot harness | Yes. Two skills around `triage()`. | Reasoning-heavy, multi-step work. Files, skills, and memory. The page gives an accounts-payable example: read invoices, match them to purchase orders, and route exceptions for approval. |
| Standard harness | Yes. One topic and one flow. | Rule-based agents. You define the topics and paths. |
| Customer Conversation harness | No. | Customer voice and chat, with escalation to a person. |

This experiment's skills still stop before approval. Microsoft's accounts-payable example is not a statement that this agent posts, pays, or changes a bank record. Those actions are disabled.

These were not opened on 28 October 2026:

- The billing overview linked from the GitHub Copilot harness row of the comparison table
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill

No prices are copied. Anything about a credit amount is unverified here.

## When to use the GitHub Copilot harness

Use it when the reviewer wants to work through one awkward invoice: run the triage, then ask why a bank-detail phrase outranked a price difference, which comment held an instruction, or why the 30-day arithmetic did not produce a payment day.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The overview says agents and workflows on this harness use Copilot Credits. It does not state a price. This experiment's skills tell the agent to call `triage()` and to stop. They do not tell it to pay, post, or update a supplier bank record.

The overview did not use the word preview for the harness. The skills page it would need for an upload was not opened. Treat the authoring click-path as something to confirm in the tenant.

## When to use the standard harness

Use it when every exception goes through the same topic: paste the JSON, run the triage, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "Not a focus". That matches the one-topic review. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | The prose says agents and workflows on this harness use Copilot Credits. The comparison table points at a separate billing overview, which was not opened. | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page retrieved 28 October 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

Credit ranges and stop-usage controls were on pages that were not opened for this experiment. Confirm them in the tenant before a build consumes credits.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/triage.py` is the only producer of the exception classes, the evidence, the resolution code, the prompt-payment arithmetic, and the empty payment flags.
- Experiment 12 is called from that core, and Experiment 08 is called from Experiment 12. Neither harness reimplements those.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A1 on both. The AP reviewer approves the resolution. A bank-detail flag goes to a bank-detail verifier first. Neither harness is given a tool that posts, holds, pays, changes a bank record, or sends.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing other invoices.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Customer Conversation harness. It is for customer voice and chat. This experiment does not use it. A supplier must not be given this agent as a chat.
