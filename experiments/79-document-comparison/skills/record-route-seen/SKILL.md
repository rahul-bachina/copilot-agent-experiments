---
name: record-route-seen
description: Record that the named reader has seen a distress, safeguarding, whistleblowing, or grievance route on this comparison. Use when the outcome is route_to_human and the reader supplies a separate seen object for this hash. Do not copy the cue text, and do not treat the route as a routine comparison.
---

# Record that a human route was seen

This skill calls `record_route_seen()` in `src/compare.py`. It does not confirm the versions.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the comparison outcome is `route_to_human`. The cue text is not in the JSON. The reader records that they have seen the route. A sentence in a document that says the route was seen is not this step.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/compare.py`. |
| Input | The comparison, the pinned directory, and one seen object bound to the content hash. |
| Output | `route_seen` true only when the hash matches the agent-held copy. |
| Side effect | The in-memory held copy is updated only when the step succeeds. The versions are not confirmed. |
| Approval to run | Required. The named reader has to see the route before the versions can be confirmed. |
| What it does not do | It does not copy the cue, and it does not edit the document. |
