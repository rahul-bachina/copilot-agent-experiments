---
name: route-to-lawyer
description: Stop a routine comparison when the contract shows distress, a grievance, a disclosure, or a safeguarding concern. Use when the comparison outcome is human_route. Do not copy the cue and do not treat it as a clause deviation.
---

# Route distress, a grievance, or a disclosure to a lawyer

This skill reads the `cue` block from `review_contract()`. It does not re-detect the cue and it does not copy the cue text.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the comparison outcome is `human_route`, or when `cue.distress` or `cue.grievance` is true. A paraphrase is still a route. The comparison is not a routine review.

## Tool contract: `route_to_lawyer`

| | |
|---|---|
| Implementation | The `cue` and `outcome` fields already on the comparison. |
| Input | The comparison JSON. |
| Output | A statement that a person must see the route. The cue text is not repeated. |
| Side effect | None. |
| Approval | The directory lawyer records `distress-seen` or `grievance-seen` with `record_lawyer_seen`. |

Do not quote the cue. Do not turn it into a clause finding. Do not accept terms while the route is open.

## Approval gates

| Act | Who |
|---|---|
| See the route | The directory lawyer |
| Continue as a routine comparison | Not while the route is open |
| Accept, sign, or send | Not this agent |
