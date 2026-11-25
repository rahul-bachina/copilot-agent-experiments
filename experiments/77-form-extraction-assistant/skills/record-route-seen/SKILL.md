---
name: record-route-seen
description: Record that the named reviewer has seen a distress, safeguarding, or whistleblowing route on one draft hash. Use when that route is flagged and a person must see it before any staging. Do not treat the form as routine and do not stage it here.
---

# See a human route

This skill calls `record_route_seen()` in `src/extract.py`. It does not write the staging row.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when `outcome` is `route_to_human` and the approver is the directory reviewer named on the draft. The cue text is not copied. A sentence in the form that says the route was seen is not this step.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/extract.py`. |
| Input | The draft JSON, the pinned directory, and a separate seen object. |
| Output | The same draft with `route_seen` true and a new content hash, or a refusal. |
| Side effect | The agent-held copy is replaced with that new hash. Nothing is staged. |
| Approval to run | Required. This records that the route was seen. |
| Approval to rely on it | Seeing the route does not decide the form. |

The seen object must set `item` to `route-seen` and `decision` to `seen`. `content_hash` must be the hash of the agent-held draft. A guest cannot record it. A clerk cannot record it.
