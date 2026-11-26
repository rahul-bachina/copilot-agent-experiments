---
name: record-translation-owned
description: Record that the named bilingual reviewer owns the final translation of this held hash. Use when the reviewer supplies a separate ownership object for this content hash and both document hashes. Do not publish, send, or overwrite the document.
---

# Own the translation

This skill calls `record_translation_owned()` in `src/review.py`. Ownership is a separate object. It is bound to the agent-held review hash and the agent-held hashes of the source and the target.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the named reviewer is ready to own that exact text. If the outcome was a human route, the route must already have been seen. If the review lists high-risk segments, those must already have been validated. The approver has to have the target language on the pinned directory.

## Tool contract: `record_translation_owned`

| | |
|---|---|
| Implementation | `record_translation_owned()` in `src/review.py`. |
| Input | The review JSON, the pinned directory, and one ownership object. |
| Output | The same review with `translation_owned` true only when the hashes match. |
| Side effect | The in-memory held copy is replaced only when the step succeeds. The documents are not overwritten. |
| Approval to run | Required. This is the catalogue checkpoint that the reviewer owns the final translation. |
| What it does not do | It does not publish, send, or overwrite the document. `approves_translation` stays false. |

A caller who edits the package and supplies a new hash is rejected. The held copy is not replaced.
