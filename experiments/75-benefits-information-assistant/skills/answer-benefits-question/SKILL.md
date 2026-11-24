---
name: answer-benefits-question
description: Answer a general question about what a benefit is, how to apply, what evidence is usually needed, or where to get independent advice, from the pinned pages. Use when the resident has not asked for an eligibility decision, an entitlement, or an award amount.
---

# Answer a benefits question

This skill calls `answer_question()` in `src/assistant.py`. It does not decide, calculate, submit, or send.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the resident asks what a benefit is, how a person applies, what evidence is usually asked for, or where to get independent advice. A distress, debt, eviction, domestic abuse, or safeguarding concern is not a routine answer.

## Tool contract: `answer_question`

| | |
|---|---|
| Implementation | `answer_question()` in `src/assistant.py`. |
| Input | One synthetic question. Caller pages, rules, and directories are compared and not applied. |
| Output | JSON. `human_approval` is null. `award_amount` is null. `eligibility_decided` is false. |
| Side effect | None. |
| Approval to run | Not required. The answer is not a decision. |
| Approval to stage | The named resident approves the content hash before anything is stored. |

Every quoted sentence cites the pinned page, the publisher, and the last-reviewed date. A page past its review date is not quoted.
