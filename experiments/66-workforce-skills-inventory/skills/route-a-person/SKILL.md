---
name: route-a-person
description: Record that HR has seen a distress, objection, or out-of-scope route, by reason code. Use when the inventory stopped for a person. Do not decide the case or copy the cue.
---

# Route to a person

This skill calls `record_route_seen()` in `src/inventory.py`. It does not reimplement the route check.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights. Use when the inventory outcome is a route and HR is recording that they have seen it.

## When to use this skill

Use it when the outcome is `human_route`, `objection`, `out_of_scope`, or `inference_refused`. The cue is not copied. Seeing the route does not decide the case, and it does not propose skills.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/inventory.py`. |
| Input | The inventory JSON, the directory JSON, and a seen object. `item` is `human-route`. `decision` is `seen`. `reason_code` must match the route. |
| Output | The inventory JSON with `route_seen.recorded` true, or `blocked_reason` set. |
| Side effect | None. `case_decided` stays false. |
| Approval to run | The seen object is the approval. It is not read from the evidence. |

The approver must be HR on the directory. Do not paste the cue into the seen object.

Do not write to an HR system. Do not rate performance.

## Approval gates

| Act | Who |
|---|---|
| See the route | The directory HR reviewer, for this reason code |
| Decide the case | Not this agent |
| Propose skills on this path | Not this agent |
