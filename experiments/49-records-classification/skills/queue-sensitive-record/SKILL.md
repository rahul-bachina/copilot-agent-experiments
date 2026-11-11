---
name: queue-sensitive-record
description: Use when a classification draft is already on the human queue because of personal data, a possible OFFICIAL-SENSITIVE marking, a legal hold, low confidence, or an existing higher marking.
---

# Queue a sensitive record

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use this skill only when `human_queue.required` is true. Show the queue reasons from the JSON. Do not clear the queue yourself. The records manager marks `queue_reviewed` on the confirmation object.

This starter does not assign a weight to a skill.

## Tool contract: `record_confirmation`

| | |
|---|---|
| Implementation | `record_confirmation()` in `src/classify.py`. |
| Schema | `schema/confirmation_tool.schema.json`. |
| Required extra | `queue_reviewed` true, and every classification field. |
| Side effect | None. A legal hold stays a hold. `disposed` stays false. |

## What you may do

1. List the queue reasons that are already on the draft.
2. Say a personal-data indicator is not a finding that Article 5(1)(e) was met, and not a finding that it was breached.
3. Say a legal hold means the proposed disposal action is not to dispose. The agent does not dispose.
4. Offer the human route. This agent does not publish a telephone number.

## What you must not do

- Remove OFFICIAL-SENSITIVE, SECRET, or TOP SECRET to make the queue shorter.
- Tell the records manager the queue can be skipped.
- Copy an identifier value.

## Approval gates

A queue review is part of the records manager's confirmation. It does not delete the record and it does not apply a tenant label.
