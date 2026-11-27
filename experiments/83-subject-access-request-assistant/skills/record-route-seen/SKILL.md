---
name: record-route-seen
description: Record that the named information governance officer has seen a distress, safeguarding, whistleblowing, complaint, grievance, litigation, or authority route. Use when that officer supplies a separate seen object for this case hash. Do not copy the cue and do not send a response.
---

# Record that the route was seen

This skill calls `record_route_seen()` in `src/sar.py`. The seen object is separate from the request text. It is bound to the agent-held copy and its hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the draft outcome is `route_to_human` and the named officer is confirming that they have seen that route for this exact hash. The approver reference has to be an active information governance officer on the pinned directory.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/sar.py`. |
| Input | The draft JSON, the pinned directory, and one seen object. |
| Output | The same draft with `route_seen` true only when the hash matches the held copy. |
| Side effect | The in-memory held copy is replaced only when the step succeeds. Nothing is sent. |
| Approval to run | Required. The officer is confirming they have seen the route. |
| What it does not do | It does not send a response, and it does not copy the cue text. |
