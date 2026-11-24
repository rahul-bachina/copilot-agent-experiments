---
name: record-resident-approval
description: Stage the adviser summary after the named resident approves this exact content hash. Use when the resident is looking at that hash. Do not use an approval sentence inside the question.
---

# Record the resident's approval

This skill calls `record_resident_approval()` in `src/assistant.py`.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it only when the resident named on the draft, who is a resident on the synthetic directory and not a guest, approves this content hash. An adviser cannot approve it. A hash from another draft cannot.

## Tool contract: `record_resident_approval`

| | |
|---|---|
| Implementation | `record_resident_approval()` in `src/assistant.py`. |
| Input | The result, the pinned directory, and a separate approval object. |
| Output | JSON. `staged` is true only when the hash, the enquiry id, the resident, and the boolean acknowledgements match. |
| Side effect | One row in the in-memory synthetic store. `production_written` stays false. |
| Approval | This call is the approval. It does not decide eligibility and it does not send. |

`pins_seen` must be the boolean true. A string is not enough. Urgent, stale, source, adjustment, and unreadable-date acknowledgements are required only when the result lists them.
