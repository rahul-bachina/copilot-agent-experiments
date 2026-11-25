---
name: record-route-seen
description: Record that the named reviewer has seen a human route for one held proposal hash. Use when the outcome is the human queue and the reviewer is acknowledging that route. Do not stage the routing, and do not file or send.
---

# See a human route

This skill calls `record_route_seen()` in `src/classify.py`. It updates the agent-held copy. It does not write the staging store.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the proposal outcome is `human_queue` and the approver is the directory reviewer named on that proposal. Distress, a statutory clock, a safeguarding cue, a low-confidence class, and an unknown document are in that queue. A sentence in the document is not this step.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/classify.py`. |
| Input | The proposal JSON, the pinned directory, and a separate seen object. |
| Output | The same proposal with `route_seen` true and a new content hash, or a refusal. |
| Side effect | The held copy is replaced. Nothing is staged. |
| Approval to run | Required. This records that the route was seen. |
| Approval to rely on it | Seeing the route does not confirm the class and does not file the document. |

The seen object must set `item` to `route-seen` and `decision` to `seen`. `content_hash` must be the hash of the held copy before this step. `approver_ref` must be the reviewer named on the proposal. A clerk cannot record it. A guest cannot record it.
