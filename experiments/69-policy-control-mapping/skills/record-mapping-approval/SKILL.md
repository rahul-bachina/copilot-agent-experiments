---
name: record-mapping-approval
description: Record that a directory control owner approved one mapping, gap, or contradiction, bound to that item's content hash and the proposal hash. Use when the owner has already seen the proposal and is approving one exact item. Do not mark a control as met, close a gap, edit a policy, or write to a GRC system.
---

# Record a mapping approval

This skill calls `record_owner_approval()` in `src/map_controls.py`. It does not decide that a control is met.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the proposal already exists and a directory control owner is approving one item: one mapping, one gap seen, one contradiction seen, or a distress route. The approval object is separate from the policy text.

## Tool contract: `record_mapping_approval`

| | |
|---|---|
| Implementation | `record_owner_approval()` in `src/map_controls.py`. |
| Input | The proposal JSON, the directory JSON, and one approval object. |
| Output | The same proposal with `human_approval` set only when the approver, the item, the content hash, and the proposal hash all match. |
| Side effect | None. `control_met`, `gap_closed`, `policy_edited`, and `grc_written` stay false. |
| Approval to run | The approval object is the approval. A sentence in a policy is not. |

`decision` must be the string `approved`. `pins_seen` must be the boolean true, because the CAF PDF was not opened. A string is not coerced. If the proposal is stale, `stale_seen` must be the boolean true. If the caller library differs from the pinned library, `library_differences_seen` must be the boolean true. If a biased criterion was flagged, `bias_seen` must be the boolean true.

The approver reference is checked against the synthetic directory. The role must be Control owner. A guest cannot approve. A typed id that is not in the directory cannot approve.

If the policy text was changed after the hash was taken, stop. The old approval does not cover the new text.

Do not mark a control as met. Do not close a gap. Do not edit a policy. Do not write to a GRC system.
