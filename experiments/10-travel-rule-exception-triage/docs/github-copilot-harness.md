# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, opened 26 October 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for an analyst who drops in one transfer and then asks follow-up questions: which field is missing, why return was proposed, what the sunrise wording was. The standard harness is the fixed topic. Both call `src/triage.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. It is billed in Copilot Credits. The separate billing article was not opened on 26 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 26 October 2026. Treat the authoring click-path as something to confirm in the tenant.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent.

| Skill | Calls | Stops |
|---|---|---|
| `triage-transfer` | `triage()` in `src/triage.py` | When the JSON is shown. `analyst_decision` is null. |
| `explain-travel-rule-exception` | No second checker. It reads the JSON. | When the explanation is tied to fields that are already there. |

The tool `triage_transfer` has no side effect. There is no tool that holds, returns, releases, files a suspicious activity report, or contacts a counterparty. Do not add one.

## What the analyst sees

1. Injection and stale flags, before the categories.
2. Missing fields and mismatches, with the provision already on the row.
3. Hold, return, and escalate, each marked proposed or not, with the reason from the JSON.
4. A line that nothing was held, returned, released, filed, or sent.

A sandbox file `draft-triage.json` is the tool JSON. It is not a decision record. The analyst's decision is made outside the agent, in the firm's own process.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 26 October 2026. The skills say not to store the transfer. Assume memory is a risk and do not use it for names or wallet strings.

## What this note does not verify

- Credit amounts, monthly limits, or the date any preview billing ended. Experiment 04 recorded sentences from the billing pages on 24 October 2026. Those pages were not re-opened for this experiment.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
- The Customer Conversation harness. It is for customer voice and chat. This experiment does not use it. An analyst is the user. A customer chatting with it would be a different product.
