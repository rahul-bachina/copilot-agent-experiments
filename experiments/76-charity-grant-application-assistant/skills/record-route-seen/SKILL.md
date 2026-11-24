---
name: record-route-seen
description: Record that the named applicant has seen a distress, grievance, or safeguarding route for this package hash. Use when prepare_application returned route_to_human and that applicant is acknowledging the route. Do not stage the package and do not copy the cue text.
---

# See a human route

This skill calls `record_route_seen()` in `src/grant.py`. It does not write the staging store.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the outcome is `route_to_human`, the approver is the directory applicant named on the draft, and they are recording that they have seen that route for that content hash. A sentence in a case note is not this step.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/grant.py`. |
| Input | The draft JSON, the pinned directory, and a separate seen object. |
| Output | The same draft with `route_seen` true, or a refusal. |
| Side effect | None. The content hash changes because the route flag is part of the package. |
| Approval to run | Required. This records that the route was seen. |
| Approval to rely on it | The package is still not stored. |

The seen object must set `item` to `route-seen` and `decision` to `seen`. `approver_ref` must be the applicant named on the draft, with role `applicant` on the pinned directory. `content_hash` must be the hash of the draft before this call.

Do not copy the cue text into the record.
