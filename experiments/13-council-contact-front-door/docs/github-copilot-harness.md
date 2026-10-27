# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, opened 27 October 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for an adviser who pastes one enquiry and then asks a follow-up: why this page, why the handover, which citation is stale. The standard harness is the fixed topic. Both call `src/front_door.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. It is billed in Copilot Credits. The separate billing article was not opened on 27 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 27 October 2026. Treat the authoring click-path as something to confirm in the tenant.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent.

| Skill | Calls | Stops |
|---|---|---|
| `answer-from-catalogue` | `triage()` in `src/front_door.py` | When the JSON is shown. `human_approval` is null. |
| `prepare-warm-handover` | `record_adviser_review()`, and only when the adviser has given the separate review object | When the review is recorded or refused. Nothing is sent. |

The tool `triage_enquiry` has no side effect. There is no tool that decides eligibility, writes a case, sends a message, takes a payment, or calls 999. Do not add one. The review tool's schema, `schema/adviser_review_tool.schema.json`, accepts only `accept_draft`, `reject_draft`, and `take_handover`.

## What the adviser sees

1. Injection and stale flags, before the answer.
2. `outcome`, and `answer.text` only when the JSON already contains it.
3. Citations, with review dates. A stale citation has no body.
4. A line that nothing was decided, sent, or written to a case.

A sandbox file `draft-front-door.json` is the tool JSON. It is not a case record. The adviser's decision is made outside the agent, in the council's own process, except for the review call above, which still does not send.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 27 October 2026. The skills say not to store the enquiry. Assume memory is a risk and do not use it for residents' words.

## What this note does not verify

- Credit amounts, monthly limits, or the date any preview billing ended.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
- The Customer Conversation harness detail page. The overview, which was opened, describes that harness for customer voice and chat, with escalation to a person, billed in Copilot Credits. This experiment does not implement it. An unattended resident chat would be a different product, and it would still need the same approval gates.
