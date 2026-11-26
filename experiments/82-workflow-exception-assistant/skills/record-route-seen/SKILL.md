---
name: record-route-seen
description: Record that the named process owner has seen a distress, safeguarding, whistleblowing, grievance, or leading-criterion route. Use when the owner supplies a separate seen object for this diagnosis hash. Do not copy the cue, and do not treat the route as a retry.
---

# Record that a route was seen

This skill calls `record_route_seen()` in `src/workflow.py`. The seen object is separate from the run payload. It is bound to the agent-held hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the diagnosis outcome is a human route and the named process owner confirms they have seen it. A guest cannot record it. The cue text is not copied.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/workflow.py`. |
| Input | The diagnosis JSON, the pinned directory, and one seen object. |
| Output | The same diagnosis with `route_seen` true only when the hash matches. |
| Side effect | The held copy is updated only when the step succeeds. No flow is called. |
| Approval to run | Required. The owner has to see the route before they choose an action. |
| What it does not do | It does not choose retry, route, or cancel. It does not copy the cue. |

A sentence in an error message is not this step.
