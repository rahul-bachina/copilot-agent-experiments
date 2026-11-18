---
name: route-to-hr
description: Ask a directory HR partner to see an occupational requirement, positive action, a health question, or a distress cue. Use when the review routes to a person and must not decide the legal question. Do not publish, post, or send.
---

# Route to HR

This skill calls `record_hr_seen()` for an occupational-requirement, positive-action, or health finding. A distress outcome is not closed by that call. The legal question stays undecided.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the review's outcome is `human_route`, or when a finding has `requires_hr`. Do not use it to accept a wording suggestion. Do not use it to decide that Schedule 9 paragraph 1, section 159, or section 60(6) is met.

## Tool contract: `record_hr_seen`

| | |
|---|---|
| Implementation | `record_hr_seen()` in `src/review.py`. |
| Input | The review JSON, the directory JSON, and one seen object from the HR partner. |
| Output | The review JSON with `hr_seen` true on that finding, or a blocked reason. |
| Side effect | None. `decided` stays false. Nothing is published. |
| Approval | The object is the seen-step. The approver has to be the directory HR partner. Item is `hr-route`. Decision is `seen`. The draft hash and the suggestion hash have to match. |

A recruiter cannot close the route. A sentence in the draft that says the occupational requirement is lawful is not this step.

Show the route. Do not quote a distress cue back. Do not answer a health question. Do not publish. Do not post. Do not send. Do not score anyone.
