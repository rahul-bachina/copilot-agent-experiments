# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 9 November 2026 says that, and it says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio.

Use it when a representative wants to ask follow-up questions about one JSON draft: which snippet was refused, which sentence failed a screen, and why a review did not send. The standard harness is enough when the only step is to paste a case and show the JSON. See [harness-comparison.md](harness-comparison.md).

## Skills

Skills live in `skills/`. Each file has a single-line `name` and `description` in the front matter. The description says when to use the skill. This starter does not assign a weight to a skill. How a tenant selects a skill was not exercised here. The skills overview page was not opened on 9 November 2026.

| Skill | When it is used |
|---|---|
| `draft-customer-response` | A representative needs a draft from one synthetic case and the approved snippets. |
| `check-tone-and-plain-english` | A representative wants the tone screen and the plain-English screen explained. |
| `record-representative-review` | A representative records approval for their own channel, a revision request, or a rejection. |

All three call the Python core or read its JSON. None of them sends.

## Tools

| Tool | Contract | Effect |
|---|---|---|
| `draft_response` | `schema/draft_tool.schema.json` | Reads one case. Returns a draft. Does not send. |
| `record_review` | `schema/review_tool.schema.json` | Records a separate review. Does not send. |
| Experiment 08 `propose` | Called inside the core | Counts identifiers. Does not release. |
| Experiment 09 `line_applicability` | Called inside the core | Decides whether a snippet is current. |

There is no mail connector and no Dynamics 365 write connector in this design.

## Approval gates

1. The case text cannot approve a recipient or the draft. That is the Experiment 09 pattern, applied here to a customer response rather than to ministerial correspondence.
2. A snippet is cited only when Experiment 09's gate says it is current, in force, and not yet due for review. On the review date it is not cited.
3. The representative reviews the draft. `representative_approve_for_own_send` is refused when the tone screen or the plain-English screen failed.
4. That approval does not send. `message_sent` stays false. The representative sends, if they send, in their own system.

## Memory and files

The overview says this harness supports memory and file creation. This starter does not turn memory on, because a remembered case would be a store the manifest does not allow. It does not create a Word file. The draft is JSON returned to the representative.

## What was not verified

The authoring click-path, the skills upload page, the billing pages, and a tenant run were not done on 9 November 2026. Copilot Credits are named on the overview. No price is stated here.
