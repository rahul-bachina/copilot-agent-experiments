---
name: record-interpretation-seen
description: Record that the named reader owns the interpretation of this comparison hash. Use when the versions have already been confirmed and the reader acknowledges that the reading is theirs. Do not give legal advice, and do not approve or publish the document.
---

# Record that the reader owns the interpretation

This skill calls `record_interpretation_seen()` in `src/compare.py`. It runs only after `confirm_versions()` has succeeded for this hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the named reader, having confirmed the versions, records that they own the interpretation. The acknowledgement is a separate object bound to the current comparison hash.

## Tool contract: `record_interpretation_seen`

| | |
|---|---|
| Implementation | `record_interpretation_seen()` in `src/compare.py`. |
| Input | The confirmed comparison, the pinned directory, and one acknowledgement. |
| Output | `interpretation_acknowledged` true only for that hash. `legal_advice` stays false. |
| Side effect | The in-memory held copy is updated only when the step succeeds. Nothing is published. |
| Approval to run | Required. The reader is acknowledging their own reading. |
| What it does not do | It does not decide which version is better, and it does not approve the document. |
