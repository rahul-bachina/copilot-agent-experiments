# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, retrieved 28 October 2026, says it is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for a person who drops in one request and then asks follow-up questions: why an item was out of scope, which phrase was hidden in a comment, why a privilege flag did not apply an exemption. The standard harness is the fixed topic. Both call `src/pack.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The section prose says agents and workflows on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened on 28 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 28 October 2026. Treat the authoring click-path as something to confirm in the tenant.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent.

| Skill | Calls | Stops |
|---|---|---|
| `assemble-evidence-pack` | `build_pack()` in `src/pack.py` | When the JSON is shown. `export_approved` and `redactions_approved` are false. |
| `explain-pack-finding` | No second classifier and no second redactor. It reads the JSON. | When the explanation is tied to fields that are already there. |

The tool `build_evidence_pack` has no side effect. There is no tool that records the exact list, produces the export, applies an exemption, writes a record, releases redacted text, or sends a message. Do not add one. Do not call `record_export_approval` or `produce_export`. Those functions exist for tests. They are not agent tools, and they still do not send.

## What the person sees

1. Injection signals, including where the phrase was hidden, before the proposed pages.
2. Out-of-scope items, with no hash and no body.
3. Held items: possible privilege, possible third-party personal data, and injection. `exemption_applied` is false.
4. The proposed index: page, source, date, and hash. It is a proposal.
5. A line that nothing was approved, exported, written, or sent.

A sandbox file `draft-evidence-pack.json` is the tool JSON. It is not an approval. An evidence pack approver records the exact list and the redaction decisions outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page retrieved on 28 October 2026. The skills say not to store the item text, the identifiers, or the hashes. Assume memory is a risk and do not use it.

## What this note does not verify

- Credit amounts, monthly limits, or the date any preview billing ended. The billing article linked from the overview was not opened on 28 October 2026.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
- The Customer Conversation harness. It is for customer voice and chat, with escalation to a person. This experiment does not use it. The user is staff assembling a pack.
