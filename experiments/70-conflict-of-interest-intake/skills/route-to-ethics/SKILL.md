---
name: route-to-ethics
description: Show a human route for distress, a disclosure, a grievance, or special-category detail in a declaration. Use when draft_declaration returns human_route, including when the wording is paraphrased. Do not copy the cue, do not process it as a routine interest, and do not decide, clear, exclude, approve, or send.
---

# Route to a person

This skill calls `record_route_seen()` in `src/declaration.py` only after an ethics or procurement officer has seen the route. It does not stage the declaration.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the outcome is `human_route`. That includes distress, a wish to die, a safeguarding worry, whistleblowing, a grievance, harassment, or special-category detail such as a political opinion, health, religion, a trade union, ethnicity, or sex life. A paraphrase still uses this skill. A family label on an ordinary draft does not, by itself, use this skill. Family detail is minimised on the draft.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/declaration.py`. |
| Input | The draft, the pinned directory, and a separate seen object. |
| Output | The draft with `route_seen` set, or a refusal. |
| Side effect | None. `staged` stays false. |
| Approval to run | Required for the seen record. Showing the route code does not need a tool call. |

`reason_code` must match the draft. `declaration_hash` must match. The approver must be `ethics` or `procurement` on the pinned directory.

Do not copy the cue sentence. Do not decide that a conflict exists. Do not clear or exclude anyone. Do not send the declaration to the supplier or to a mailbox.
