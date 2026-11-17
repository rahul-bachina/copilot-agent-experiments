---
name: record-plan-approval
description: Record the employee approval or the manager approval of one exact learning plan id. Use when that person has already decided, on a separate object, to approve the draft. Do not enrol, book, or spend.
---

# Record a plan approval

Harness: Copilot Studio **Microsoft Copilot harness**, packaged here in the layout the common brief calls the GitHub Copilot harness. On 17 November 2026 the harness overview did not use the words "GitHub Copilot harness".

This skill calls `record_approval()` in `src/plan.py`. It does not treat a sentence in the goals, or in a course description, as approval.

The `name` and `description` above are the skill fields. Generative orchestration, where the tenant uses it, selects a skill from that description. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the employee, or their manager from the synthetic directory, is approving the plan id already on screen. Drafting the plan is the other skill.

## Tool contract: `record_plan_approval`

| | |
|---|---|
| Implementation | `record_approval()` in `src/plan.py`. |
| Input | The plan JSON and one approval object: `plan_id`, `approver_ref`, `decision`, and `item`. |
| Output | The JSON the function returns. |
| Side effect | An enrolment request record only, and only when both named people have approved this plan id and no block remains. `enrolled`, `booked`, and `spent_gbp` stay false or null. |
| Approval to run | This call is the approval. The approver has to be the directory employee or the directory manager. A role typed on the object is ignored. |

`decision` has to be `approve`. `item` has to be `learning-plan`. The `plan_id` has to be the id of this plan, not an earlier one.

`stale_seen` and `budget_unreadable_seen`, when present, have to be booleans. A string is not coerced to true.

Do not call `enrol`, `book`, or `spend`. Those functions raise.

## What to show

1. Whether the employee approval is accepted, and whether the manager approval is accepted.
2. `blocked_reason`, if the request was not raised.
3. When `enrolment_request_raised` is true, the course ids on the request, and that nobody was enrolled and nothing was spent.

## Approval gates

| Act | Who |
|---|---|
| Employee approval | The employee named on the directory row |
| Manager approval | The manager named on that row |
| Stale pins or an unreadable budget | The manager, with the boolean on the approval object |
| Enrol, book, or spend | Not this agent |
