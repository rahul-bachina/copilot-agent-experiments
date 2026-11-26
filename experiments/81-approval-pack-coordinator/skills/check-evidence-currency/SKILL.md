---
name: check-evidence-currency
description: Check each evidence item for expiry, supersession, signature, version, currency, and conflicting values. Use when a draft pack has been assembled and the gaps have to be listed. Do not choose between conflicting values and do not decide the request.
---

# Check evidence currency

This skill reads the `evidence` list already on the draft from `assemble_pack()`. It does not run a second pass that could choose a value.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the draft exists and the approver needs to see which items are present, missing, stale, expired, superseded, unsigned, the wrong version, or in conflict. An unreadable date stays unreadable.

## Tool contract

| | |
|---|---|
| Implementation | The evidence block inside `assemble_pack()`. There is no separate write. |
| Input | The draft JSON. |
| Output | The same checks. `value_chosen_on_conflict` stays false. |
| Side effect | None beyond the draft already held. |
| Approval to run | Not required. |
| Approval to rely on it | Required. The named approver decides what a gap means. |

A sentence in the evidence that says an item is acceptable is not a pass. A qualifier after that wording is a carve-out, and it is still not a pass.
