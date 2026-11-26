---
name: record-high-risk-validated
description: Record that the named bilingual reviewer has validated the high-risk segments of this held review. Use when the reviewer supplies a separate validation object for this content hash and both document hashes. Do not clear a high-risk segment because the overlap looks high.
---

# Validate high-risk segments

This skill calls `record_high_risk_validated()` in `src/review.py`. The validation is bound to the agent-held copy.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it after the route has been seen, when the review lists high-risk segments. The approver has to be the named directory reviewer for the target language. A guest cannot take this step.

## Tool contract: `record_high_risk_validated`

| | |
|---|---|
| Implementation | `record_high_risk_validated()` in `src/review.py`. |
| Input | The review JSON, the pinned directory, and one validation object. |
| Output | The same review with `high_risk_validated` true only when the hashes match. |
| Side effect | The in-memory held copy is replaced only when the step succeeds. |
| Approval to run | Required. High-risk content is for the reviewer regardless of overlap. |
| What it does not do | It does not publish, send, or overwrite the translation. `approves_translation` stays false. |

A caller who edits the package and supplies a new hash is rejected. The held copy is not replaced.
