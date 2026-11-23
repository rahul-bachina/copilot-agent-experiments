---
name: record-advice-seen
description: Record that the directory records owner or legal owner has seen one advice hash. Use when that person has the hash in front of them and the acknowledgements are boolean true. Do not treat the step as authority to delete, dispose, transfer, relabel, archive, or send.
---

# Record that the advice was seen

This skill calls `record_advice_seen()` in `src/advice.py`. The only accepted item is `retention-advice-seen` and the only accepted decision is `seen`.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the directory records owner for that series, or a directory legal owner, is looking at this advice hash. `pins_seen` must be the boolean true. A string is not enough. If the result lists `schedule_seen`, `sources_seen`, or `route_seen`, those must be the boolean true as well.

A guest, a member of staff, or a records owner for a different series cannot complete this step. An approver id typed into the note is not the directory.

## Tool contract: `record_advice_seen`

| | |
|---|---|
| Implementation | `record_advice_seen()` in `src/advice.py`. |
| Input | The advice JSON, the pinned directory, and a separate seen object bound to the advice hash. |
| Output | The same advice with `human_approval.effect` set to `seen_only`, or a blocked reason and a null approval. |
| Side effect | An in-memory acknowledgement. `records_changed` stays false. |
| Approval | This is the approval step. It does not authorise disposal. |

If the advice hash does not match the advice now in front of the owner, stop. Tampered text after the hash was taken is rejected.

## Do not decide

Do not delete, move, relabel, archive, transfer, dispose, or send. Do not lift a legal hold. Do not accept a disposal decision on this object.
