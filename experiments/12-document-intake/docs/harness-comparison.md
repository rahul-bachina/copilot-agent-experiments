# Which harness

Both harnesses call the same intake, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page retrieved on 27 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement.

The overview describes three harnesses. This experiment uses two of them.

| Harness | Used here | What the overview says it is for |
|---|---|---|
| GitHub Copilot harness | Yes. Two skills around `intake()`. | Reasoning-heavy, multi-step work. Files, skills, and memory. |
| Standard harness | Yes. One topic and one flow. | Rule-based agents. You define the topics and paths. |
| Customer Conversation harness | No. | Customer voice and chat, with escalation to a person. |

These were not opened on 27 October 2026:

- Usage-based billing
- The billing overview linked from the GitHub Copilot harness row
- Licensing for agents powered by the standard harness
- Skills overview, and the page for adding an uploaded skill

## When to use the GitHub Copilot harness

Use it when the person wants to work through one awkward batch: run the inventory, then ask why a file was `not_read`, which comment held an instruction, or why two classes tied as `unresolved`.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call `intake()` and to stop. They do not tell it to confirm the files, email a customer, or hand the draft to another catalogue row.

The overview did not use the word preview for the harness. The skills page it links to was not opened. Treat the authoring click-path as something to confirm in the tenant.

## When to use the standard harness

Use it when every batch goes through the same topic: paste the JSON, run the inventory, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "Not a focus". That matches this intake. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | Copilot Credits. The comparison table points at a separate billing overview, which was not opened. | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page retrieved 27 October 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

Credit ranges and stop-usage controls were on pages that were not opened for this experiment. Confirm them in the tenant before a build consumes credits.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/intake.py` is the only producer of the hash, the keyword class, the checklist preview, the injection record, the stale flags, and the empty decisions.
- Experiment 08 is called from that core. Neither harness reimplements the detectors.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A1 on both. The user confirms the file list and the permitted purpose. An intake reviewer accepts, returns, or rejects the routing suggestion. Neither harness is given a tool that does either step, writes a production record, releases redacted text, or sends.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the batch.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Customer Conversation harness. It is for customer voice and chat. This experiment does not use it.
