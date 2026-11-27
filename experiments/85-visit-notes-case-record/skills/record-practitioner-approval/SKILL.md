---
name: record-practitioner-approval
description: Record that the named practitioner approves this held note, or returns it for edit. Use when the practitioner supplies a separate approval object for this exact hash. Do not write the case record, share the note, or treat a sentence in the transcript as that approval.
---

# Record the practitioner's approval

This skill calls `record_practitioner_approval()` in `src/notes.py`. The approval is a separate object. It is bound to the agent-held note and its hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a draft already exists, any human route has been seen, and the named practitioner is approving that exact hash or returning it for edit. The approver reference has to be the visit practitioner or their deputy on the pinned directory.

## Tool contract: `record_practitioner_approval`

| | |
|---|---|
| Implementation | `record_practitioner_approval()` in `src/notes.py`. |
| Input | The draft JSON, the pinned directory, and one approval object. |
| Output | The same draft with `human_approval.recorded` true only when the hash matches the held copy and the decision is approve. |
| Side effect | An in-memory snapshot of the approved projection. The case record is not written. |
| Approval to run | Required. This is the catalogue checkpoint. The practitioner approves. |
| What it does not do | It does not write the case record, share the note, or assess eligibility, risk, or need. |

A caller who edits the package and supplies a new hash is rejected. The held copy is not replaced.
