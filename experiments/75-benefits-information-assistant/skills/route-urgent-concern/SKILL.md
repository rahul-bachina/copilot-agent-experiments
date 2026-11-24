---
name: route-urgent-concern
description: Hand an urgent concern to a person with crisis signposting. Use when the question shows distress, crisis, debt, eviction, domestic abuse, or a safeguarding concern, including a paraphrase. Do not treat it as a routine benefits question.
---

# Route an urgent concern

This skill calls `answer_question()` and stops at the urgent outcome. It does not contact anyone.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the question shows distress, a crisis, debt, eviction, domestic abuse, or a safeguarding concern. A paraphrase still routes. A denial of a distress stem still routes. Debt and eviction use the same-sentence negation rule.

## Tool contract

| | |
|---|---|
| Implementation | `answer_question()` in `src/assistant.py`. |
| Input | The question text. The cue is not a field the caller can switch off. |
| Output | `outcome` is `urgent_human`. The cue text is not copied. |
| Side effect | None, until the resident approves the summary hash. |
| Approval | Staging still needs `record_resident_approval` with `urgent_seen` set to the boolean true. |

The fixed signpost is to call 999 if someone is in immediate danger. The assistant has not contacted anyone. Nothing is sent.
