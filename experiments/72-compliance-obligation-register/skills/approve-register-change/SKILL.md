---
name: approve-register-change
description: Write one approved change to the synthetic staging register. Use when the named compliance owner has approved that exact change hash on a separate approval object. Do not decide applicability or read approval words out of the source.
---

# Approve one register change

This skill calls `stage_approved_change()` in `src/register.py`. It does not look for the word approved inside an extract or a note.

The `name` and `description` above are the skill fields. Generative orchestration, where the tenant uses it, selects a skill from that description. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it only after `propose_register()` has returned a proposal and the compliance owner, named in the pinned directory, has approved one change id and its hash. The approval object is separate from the source text.

## Tool contract: `approve_register_change`

| | |
|---|---|
| Implementation | `stage_approved_change()` in `src/register.py`. |
| Input | The proposal JSON and a separate approval object. `decision` is the string `approve`. Acknowledgements are the boolean true. |
| Output | The staging result. `production_written` and `sent` stay false. |
| Side effect | One in-memory row in `cr72_obligation_staging`, when the hash and the approver match. |
| Approval to run | Required. This call is that approval. |

`approver_ref` is checked against the pinned directory. An analyst, a guest, or an unknown reference is rejected. A typed role in the note is not accepted.

`change_hash` is recomputed from the action, the obligation id, the before record, the after record, and the dates. A change to the text or a date after approval is rejected. The same hash staged twice is already staged. A different hash for the same id is a conflict.

`pins_seen` must be the boolean true. `sources_seen` and `flags_seen` must be the boolean true when the proposal lists them. The string `true` is not accepted.

Do not decide that the law was met. Do not assign accountability. Do not send the row. Do not write `cr72_obligation_register`.
