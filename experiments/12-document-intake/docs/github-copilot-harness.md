# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, retrieved 27 October 2026, says it is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for a person who drops in one batch and then asks follow-up questions: why a file was left unread, which phrase was hidden in a comment, why two classes tied. The standard harness is the fixed topic. Both call `src/intake.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened on 27 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 27 October 2026. Treat the authoring click-path as something to confirm in the tenant.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent.

| Skill | Calls | Stops |
|---|---|---|
| `inventory-documents` | `intake()` in `src/intake.py` | When the JSON is shown. `files_confirmed` and `purpose_confirmed` are false. `reviewer_decision` is null. |
| `explain-intake-finding` | No second classifier and no second redactor. It reads the JSON. | When the explanation is tied to fields that are already there. |

The tool `inventory_documents` has no side effect. There is no tool that confirms the files, sets the purpose, accepts a routing suggestion, writes a queue, releases redacted text, or sends a message. Do not add one. Do not call `record_user_confirmation` or `record_reviewer_decision`. Those functions exist for tests. They are not agent tools, and they still do not write a queue.

## What the person sees

1. Injection signals, including where the phrase was hidden, before the class suggestion.
2. Unread, empty, oversized, and checksum-failed files, before any class.
3. Stale, missing, future, and invalid document dates, and whether the purpose catalogue is stale.
4. The keyword class, the checklist preview, and the Experiment 08 entity types. `sufficient` is false. The text is not described as anonymised.
5. A line that nothing was confirmed, queued, written, or sent.

A sandbox file `draft-intake.json` is the tool JSON. It is not an acceptance. The user confirms the file list and the permitted purpose outside the agent. An intake reviewer then accepts, returns, or rejects the routing suggestion, also outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page retrieved on 27 October 2026. The skills say not to store the file text, the identifiers, or the hashes. Assume memory is a risk and do not use it.

## What this note does not verify

- Credit amounts, monthly limits, or the date any preview billing ended. The billing article linked from the overview was not opened on 27 October 2026.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
- The Customer Conversation harness. It is for customer voice and chat, with escalation to a person. This experiment does not use it. The user is staff doing intake. A customer chatting with it would be a different product.
- The exact skill-upload schema. The approval headings copy `agent-manifest.yaml`. They are not claimed as a Microsoft schema.
