---
name: route-a-person
description: Route a reasonable-adjustment, accessibility, distress, or wellbeing signal to a named person. Use when the draft outcome is a human route rather than a routine plan. Do not decide an adjustment and do not enrol.
---

# Route a person

Harness: Copilot Studio **Microsoft Copilot harness**, packaged here in the layout the common brief calls the GitHub Copilot harness. On 17 November 2026 the harness overview did not use the words "GitHub Copilot harness".

This skill reads the outcome `draft_plan()` already set. For an adjustment route it may call `record_adjustment_review()` after a named person has seen the plan. It does not decide that a step is reasonable.

The `name` and `description` above are the skill fields. Generative orchestration, where the tenant uses it, selects a skill from that description. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the statement names a person for wellbeing, distress, a reasonable adjustment, or an accessibility need. Do not use it to turn that signal into a routine enrolment.

## Tool contract: `record_adjustment_review`

| | |
|---|---|
| Implementation | `record_adjustment_review()` in `src/plan.py`. |
| Input | The plan JSON and a review object: `plan_id`, `reviewer_ref`, `seen` true, and `item` `adjustment-review`. |
| Output | The JSON the function returns. |
| Side effect | Marks the review as seen. `adjustment_decided` stays false. An enrolment request still needs both plan approvals. |
| Approval to run | The reviewer has to be the directory manager or a people partner. |

A wellbeing outcome is not cleared by this tool. Do not pass the cue text back to the employee.

Do not decide an adjustment. Do not enrol. Do not spend. Equality Act 2010 sections 20 and 21 were read. The duty is not marked as met.

## What to show

1. The named route. Do not repeat the cue.
2. For an adjustment route, that `adjustment_decided` and `equality_duty_met` are false.
3. That a seen-step is not an enrolment.

## Approval gates

| Act | Who |
|---|---|
| See the adjustment or accessibility route | Line manager or people partner |
| Take a distress or wellbeing case | Line manager and the organisation's wellbeing route. Not cleared by an approval object |
| Decide that an adjustment is reasonable | Not this agent |
