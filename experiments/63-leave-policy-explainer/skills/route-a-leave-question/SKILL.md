---
name: route-a-leave-question
description: Route a pregnancy, miscarriage, bereavement, domestic abuse, sickness, distress, or disability signal to a person, including a paraphrased one. Use when the question is about the person rather than the wording of the leave policy. Do not decide entitlement or quote a day count as theirs.
---

# Route a leave question

This skill calls the same `explain()` function. It does not keep a second list of phrases, and it does not assign trigger phrases or routing weights.

## When to use this skill

Use it when the employee is telling you about pregnancy, miscarriage, a death, domestic abuse, their own sickness, distress, or a disability, including where they do not use those words. Use the other skill when they ask what the policy says and the question is not about them.

## What to show

1. Say the question is with HR or the line manager, and that a person is available.
2. Do not quote a day count, a week count, or a pay figure as applying to them.
3. Do not copy the question. Identifier counts are counts. They are not the values.
4. `entitlement_decision`, `pay_decision`, and `pay_rate` stay empty. `leave_booked` and `leave_recorded` stay false.

A sentence that says the person is not in distress is not itself distress. `explain()` decides that. Do not override it.

## Approval gates

Taking the case is the person's step. This skill does not book leave, record leave, or send a message. The agent must not call `record_seen`.
