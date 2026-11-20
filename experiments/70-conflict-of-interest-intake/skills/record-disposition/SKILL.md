---
name: record-disposition
description: Record an ethics or procurement disposition against one staged declaration hash. Use when the declarant has already confirmed that hash and an ethics or procurement officer is recording their own decision. Do not decide that a conflict exists, clear, exclude, approve, or send.
---

# Record a disposition

This skill calls `record_disposition()` in `src/declaration.py`. The text is the officer's. The agent does not interpret it.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a declaration is already in the synthetic store and the officer in front of you is on the pinned directory as `ethics` or `procurement`. The declarant cannot take this step. A guest cannot take this step.

## Tool contract: `record_disposition`

| | |
|---|---|
| Implementation | `record_disposition()` in `src/declaration.py`. |
| Input | The pinned directory and a separate decision object. |
| Output | The stored JSON with the officer's text, or a refusal. |
| Side effect | Replaces the synthetic store row. It does not write a production register. |
| Approval to run | Required. The officer's object is the approval. |
| What it does not do | It does not clear, exclude, or approve a person or a supplier, and it does not send. |

`item` must be `disposition` and `decision` must be `record`. `declaration_hash` and `staged_hash` must match the stored row. A hash from the declaration text is not the stored hash.

`disposition_text` is stored and `interpreted` stays false. If the text says "exclude" or "clear", `supplier_excluded` and `person_cleared` stay false. `conflict_exists` stays null.

`mitigation_text`, when present, is stored with `applied` false. The agent does not choose a mitigation.
