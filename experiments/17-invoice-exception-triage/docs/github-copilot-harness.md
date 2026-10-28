# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.

The harness overview, retrieved 28 October 2026, says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. It says this harness can take a goal, break it into steps, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run each task in a sandbox. It says agents and workflows on this harness use Copilot Credits. It does not state a price. The page uses an accounts-payable example. This experiment's skills still stop before any payment.

The overview did not mark the harness as preview. The skills-upload page was not opened. Treat the click-path as something to confirm in the tenant.

## Skills

| Skill | When the reviewer is asking |
|---|---|
| `skills/triage-invoice-exception/SKILL.md` | What class is this invoice, and what resolution should I read? |
| `skills/explain-invoice-exception/SKILL.md` | Why did the draft say that, using the JSON already on screen? |

Both skills tell the agent to call `triage()` or to read its JSON, and to stop. They tell it not to call `record_ap_reviewer_decision` or `record_bank_route`. Those functions exist so a test can show the role check. They are not tools of the agent.

## What the agent must not do

- Post, approve, hold, or pay an invoice.
- Change supplier bank details, or treat a fingerprint match as verification.
- Decide that an invoice is valid, undisputed, or a duplicate.
- Decide that input tax can be recovered.
- Send a question to a supplier or a buyer.
- Clear a stale date because the invoice says it is current.
- Treat a `last_day_of_period` as an instruction to pay.
- Describe the text as anonymised.

## Sandbox

A file written in the sandbox is still a draft. Name it `draft-invoice-resolution.json`. Do not name it `paid`. Copying it into a finance system is a different act, and this agent has no tool for it.

Memory is documented for this harness. This starter does not use it. Whether an administrator can turn memory off was not verified. Do not give the agent a memory of other suppliers' bank details.
