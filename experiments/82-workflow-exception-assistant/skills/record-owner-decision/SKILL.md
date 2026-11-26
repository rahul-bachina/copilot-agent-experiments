---
name: record-owner-decision
description: Record that the named process owner chooses retry, route, or cancel for this held proposal. Use when the owner supplies a separate decision object for this diagnosis hash. Do not retry, cancel, edit a record, or re-run a flow, and do not treat a sentence in the payload as that decision.
---

# Record the owner's decision

This skill calls `record_owner_decision()` in `src/workflow.py`. The decision is a separate object. It is bound to the agent-held proposal and its hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a diagnosis already exists, any human route has been seen, and the named process owner is choosing retry, route, or cancel for that exact hash. The approver reference has to be the owner or a deputy on the pinned register, and that person has to be an active process owner on the pinned directory.

## Tool contract: `record_owner_decision`

| | |
|---|---|
| Implementation | `record_owner_decision()` in `src/workflow.py`. |
| Input | The diagnosis JSON, the pinned directory, and one decision object. |
| Output | The same diagnosis with `owner_decision_recorded` true only when the hash matches the held copy. |
| Side effect | The in-memory held copy is replaced only when the step succeeds. Nothing is retried or cancelled. |
| Approval to run | Required. This is the catalogue checkpoint. The process owner chooses. |
| What it does not do | It does not retry, cancel, edit a record, or re-run a flow. `executes_action` stays false. |

A caller who edits the package and supplies a new hash is rejected. The held copy is not replaced.
