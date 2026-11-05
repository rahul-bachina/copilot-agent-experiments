# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness: an authoring and orchestration framework, not the GitHub Copilot service. The overview was opened on 5 November 2026. A last-updated date was not in the text retrieved. The overview did not mark the harness as preview.

Use it when the handler wants the draft and then a follow-up question. The standard harness is the one-topic path. See [harness-comparison.md](harness-comparison.md).

## Skills

| Skill | When |
|---|---|
| `skills/triage-claim-documents/SKILL.md` | A synthetic pack is supplied and a draft is needed. |
| `skills/explain-claim-triage/SKILL.md` | The handler asks what one field on that draft means. |
| `skills/score-claim-summary/SKILL.md` | A summary written elsewhere needs the three-part scorecard. |

Generative orchestration, where it is on, selects a skill from its description. This folder does not assign a weight to a phrase. A Learn page on that behaviour was not opened on 5 November 2026. The exact behaviour is unverified.

Each description is a single line and starts with "Use when".

## What the skills must not do

- Call `record_handler_classification`. The handler records a class outside the skill. The record still does not accept the claim or write a system.
- Call `accept_claim`, `decline_claim`, `settle_claim`, `tell_customer`, or `write_claims_system`. They always raise.
- Add faithfulness, completeness, and unsupported coverage into one number.
- Turn a prompt into a finding, or add a word about conduct.
- Draft a customer message.
- Store the pack in memory. The overview says this harness supports memory. A control to turn memory off was not on the page opened on 5 November 2026.
- Recommend autonomy A3.

## Sandbox file

A skill may write `draft-claim-triage.json` in the sandbox. It is the tool JSON, unchanged. Creating that file does not need approval. It has no external effect. Copying it into a claims system does, and there is no tool that performs the copy.

Microsoft's overview, opened 5 November 2026, says this harness can create and edit Word, Excel, PowerPoint, and PDF files. A file of the brief is still a draft. Put on the first line that nothing was accepted, declined, settled, sent, or written.

## Credits

The overview says agents and workflows on this harness use Copilot Credits. The billing article was not opened. No price is copied.
