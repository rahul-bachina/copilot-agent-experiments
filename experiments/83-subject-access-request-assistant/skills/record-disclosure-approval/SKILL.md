---
name: record-disclosure-approval
description: Record that the named information governance officer accepts or rejects each redaction and exemption for this held disclosure bundle. Use when the officer supplies a separate approval object for this case hash. Do not send the response, and do not treat a sentence in the request as that approval.
---

# Record the disclosure approval

This skill calls `record_disclosure_approval()` in `src/sar.py`. The approval is a separate object. It is bound to the agent-held disclosure bundle, the redaction list, and their hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a draft already exists, any human route has been seen, and the named information governance officer is recording accept or reject for every redaction and every exemption candidate on that exact hash. The approver reference has to be an active information governance officer on the pinned directory.

## Tool contract: `record_disclosure_approval`

| | |
|---|---|
| Implementation | `record_disclosure_approval()` in `src/sar.py`. |
| Input | The draft JSON, the pinned directory, and one approval object. |
| Output | The same draft with `disclosure_approval_recorded` true only when the hash matches the held copy. |
| Side effect | The in-memory held copy is replaced only when the step succeeds. Nothing is sent. |
| Approval to run | Required. This is the catalogue checkpoint. The officer approves the bundle. |
| What it does not do | It does not send a response, delete or edit a record, or decide an exemption. `executes_disclosure` stays false. |

A caller who edits the package and supplies a new hash is rejected. The held copy is not replaced.
