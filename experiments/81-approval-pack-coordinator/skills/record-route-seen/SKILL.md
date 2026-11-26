---
name: record-route-seen
description: Record that the named approver has seen a distress, safeguarding, whistleblowing, grievance, or disclosure route. Use when the pack outcome is route_to_human and the route has not been seen. Do not decide the request.
---

# Record that a route was seen

This skill calls `record_route_seen()` in `src/coordinator.py`. It does not approve, reject, sign, submit, or send.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when `outcome` is `route_to_human` and `route_seen` is false. The approver reference must be the person on the pinned directory. A sentence in the evidence is not this step.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/coordinator.py`. |
| Input | The draft, the pinned directory, and a separate seen object bound to the current content hash. |
| Output | A new draft. `route_seen` is true only when the hash matched the held copy. The hash changes because the route flag is inside it. |
| Side effect | Replaces the in-memory held copy with this new version. Nothing is sent. |
| Approval to run | The named approver confirms they have seen the route. |
| Approval to rely on it | A later decision still requires `record_approver_decision`. |

The cue text is not copied. A denial of a distress stem is still a route.
