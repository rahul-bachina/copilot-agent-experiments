---
name: record-route-seen
description: Record that the named practitioner has seen a concern or a refused-consent route for this held note. Use when the draft outcome is route_to_practitioner and the practitioner supplies a separate seen object for this hash. Do not assess the concern or write the case record.
---

# Record that the route was seen

This skill calls `record_route_seen()` in `src/notes.py`. The seen object is separate from the transcript.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a draft already exists, the outcome is `route_to_practitioner`, and the named practitioner or their deputy is confirming they have seen that route. The approver reference has to match the pinned directory.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/notes.py`. |
| Input | The draft JSON, the pinned directory, and one seen object. |
| Output | The same draft with `route_seen` true only when the hash matches the held copy. |
| Side effect | The in-memory held copy is replaced with the new hash. Nothing is written to a case record. |
| Approval to run | Required. This records that a person saw the route. It is not an assessment. |
| What it does not do | It does not copy the cue text into the flag, and it does not write or share the note. |

A sentence in the transcript that says the route was already seen is not this step.
