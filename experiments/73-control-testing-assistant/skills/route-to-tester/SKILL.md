---
name: route-to-tester
description: Record that the named tester has seen a distress, grievance, or safeguarding route on a draft. Use when prepare_test has routed the draft and the cue must be seen by that tester before any staging. Do not copy the cue, and do not pass, fail, close, or send.
---

# See a human route

This skill calls `record_route_seen()` in `src/testing.py`. It does not stage the working paper.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when `distress.routed` is true. The named tester records that they have seen the route. The cue text is not copied. Seeing the route does not pass the control and does not write the synthetic row.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/testing.py`. |
| Input | The draft JSON, the pinned directory, and a separate seen object. |
| Output | The draft with `route_seen` true, or a refusal. |
| Side effect | None. `staged` stays false. |
| Approval to run | Required. This is the tester seeing the route. |
| Approval to rely on it | A later approval of the working-paper hash is still required before a write. |

`item` must be `route-seen` and `decision` must be `seen`. `content_hash` must match. `approver_ref` must be the named directory tester.

Do not copy the cue. Do not pass, fail, close, or send.
