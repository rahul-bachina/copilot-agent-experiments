# Copilot Studio GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. It is an authoring and orchestration framework. It is not the GitHub Copilot service.

The harness overview was opened on 27 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

Microsoft says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. The prose says agents on this harness use Copilot Credits. No price is stated on that page. The linked billing article was not opened.

The skills page was not opened. The `name` and `description` fields in each `SKILL.md` follow the overview's description of skills. Treat the upload click-path as something to confirm in the tenant.

## What this harness is for here

An HR lead working through one pack: which sections are in force, which evidence is recorded, and why the draft still has an empty decision. The standard harness is the better fit when every pack takes the same path. See [harness-comparison.md](harness-comparison.md).

The overview says this harness can break a goal into steps and adjust when a step fails. These skills do not allow that adjustment to become a dismissal, a policy publication, or a message. If the checklist is unavailable, the skill says stop.

## Skills

| Skill | File | Stops when |
|---|---|---|
| Review the pack | [../skills/review-employer-pack/SKILL.md](../skills/review-employer-pack/SKILL.md) | The JSON is on screen and `hr_decision` is null |
| Read a handbook quotation | [../skills/answer-from-handbook/SKILL.md](../skills/answer-from-handbook/SKILL.md) | The quotation is the excerpt, or the status says there is nothing to quote |
| Read an anonymised note | [../skills/summarise-anonymised-report/SKILL.md](../skills/summarise-anonymised-report/SKILL.md) | The route is HR review, or the report was refused |

There is one tool the agent may call: `review_employer_pack`, which is `review()` in `src/review.py`. `record_hr_decision` is in [../schema/tools.json](../schema/tools.json) and `callable_by_agent` is false. It is not implemented.

## Approval

The gates are copied in each skill from `agent-manifest.yaml`. Viewing a draft does not need approval. Treating it as the employer's assessment does. The HR lead is the approver for that step. A named HR role approves any action on a triage note. The policy owner approves reliance on a stale excerpt.

Approving a sentence in the chat does not publish a policy or write a personnel record. The agent has no tool for either.

## Sandbox and memory

A sandbox file `draft-hr-review.json` may hold the tool JSON. It is a draft. The overview says this harness can create Word, Excel, PowerPoint, and PDF files. Those files are drafts too.

Do not store the pack in memory. The overview says the harness supports memory. It does not say whether memory can be turned off. That point is unverified.

## What not to add

- A mail connector, a Teams send action, or an Acas contact.
- A Dataverse or HR-system write, including a training-attestation row.
- SharePoint as a live knowledge source. Citations are in the JSON, from `src/sources.py`.
- A worker-facing channel. This agent is for an HR lead.
