---
name: route-to-secretary
description: Record that the named company secretary has seen a distress, grievance, or safeguarding route. Use when assemble_pack returns route_to_human and that secretary is acknowledging the route for that exact hash. Do not stage the pack and do not copy the cue text.
---

# See a human route

This skill calls `record_route_seen()` in `src/pack.py`. It does not write the staging store.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the outcome is `route_to_human` and the company secretary named on the draft is recording that they have seen the route. A distress sentence is not a routine paper. The cue text is not copied into the record.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/pack.py`. |
| Input | The draft JSON, the pinned directory, and a separate seen object. |
| Output | The same draft with `route_seen` true, or a refusal. |
| Side effect | None. Nothing is staged. |
| Approval to run | Required. This is the secretary seeing the route. |
| Approval to rely on it | The pack still needs `record_secretary_approval` on the hash this step returns. |

The seen object must set `item` to `route-seen` and `decision` to `seen`. `content_hash` must be the hash of this draft. A sponsor, a director, or a guest cannot see the route for the secretary.
