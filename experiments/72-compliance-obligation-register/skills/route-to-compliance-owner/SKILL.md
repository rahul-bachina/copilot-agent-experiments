---
name: route-to-compliance-owner
description: Record that the compliance owner has seen a human route. Use when the note shows distress, a grievance, a disclosure, or a safeguarding concern, including a paraphrase. Do not copy the cue and do not stage the proposal.
---

# Route to the compliance owner

This skill calls `record_route_seen()` in `src/register.py`. It does not copy the cue into the record.

The `name` and `description` above are the skill fields. Generative orchestration, where the tenant uses it, selects a skill from that description. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when `propose_register()` returns `outcome` `route_to_human`. That includes distress, a grievance, a disclosure, or a safeguarding concern, including when the wording is paraphrased. Do not continue the routine proposal.

## Tool contract: `route_to_compliance_owner`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/register.py`. |
| Input | The route result and a separate seen object. `decision` is `seen`. `item` is `route-seen`. |
| Output | A seen record. `staged` stays false. |
| Side effect | None. Nothing is written to the staging register. |
| Approval to run | Required. The named compliance owner, for this route hash. |

`route_hash` must match the proposal. A hash from another note is rejected. `pins_seen` must be the boolean true.

Do not copy the cue. Do not decide what the person needs. Do not stage the changes that were not produced. Do not send.
