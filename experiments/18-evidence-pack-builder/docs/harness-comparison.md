# Which harness

Both harnesses call the same pack builder, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page retrieved on 28 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The note on the page also says the harness shares underlying technology and SDK components with GitHub Copilot. This repository cannot see a tenant's traffic.

The overview describes three harnesses. This experiment uses two of them.

| Harness | Used here | What the overview says it is for |
|---|---|---|
| GitHub Copilot harness | Yes. Two skills around `build_pack()`. | Reasoning-heavy, multi-step work. Files, skills, and memory. |
| Standard harness | Yes. One topic and one flow. | Rule-based agents. You define the topics and paths. |
| Customer Conversation harness | No. | Customer voice and chat, with escalation to a person. |

These were not opened on 28 October 2026:

- The billing overview linked from the GitHub Copilot harness row of the comparison table
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill

## When to use the GitHub Copilot harness

Use it when the person wants to work through one awkward pack: run the index, then ask why an item was out of scope, which comment held an instruction, or why a privilege phrase did not apply an exemption.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The section prose says agents and workflows on this harness use Copilot Credits. The comparison table's billing cell points at a separate overview, which was not opened. No price is copied here. The skills tell the agent to call `build_pack()` and to stop. They do not tell it to approve the list, email an ombudsman, or disclose the records.

The overview did not use the word preview for the harness. The skills page it might link to was not opened. Treat the authoring click-path as something to confirm in the tenant.

## When to use the standard harness

Use it when every pack goes through the same topic: paste the JSON, type the scopes and the search period, run the builder, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. The comparison table says files, skills, and memory are "Not a focus". That matches this builder. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | The section prose says Copilot Credits. The comparison table points at a separate billing overview, which was not opened. | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page retrieved 28 October 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

Credit ranges and stop-usage controls were on pages that were not opened for this experiment. Confirm them in the tenant before a build consumes credits.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/pack.py` is the only producer of the scope check, the hash, the page proposal, the review flags, and the empty approval.
- Experiment 12 is called from that core, and Experiment 12 calls Experiment 08. Neither harness reimplements the detectors.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A1 on both. An evidence pack approver records the exact item list and the redaction decisions. Neither harness is given a tool that does that step, writes a production record, releases redacted text, or sends.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the items.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Customer Conversation harness. It is for customer voice and chat. This experiment does not use it. A data subject chatting with it would be a different product.
