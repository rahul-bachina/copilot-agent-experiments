---
name: stub-write-approved-fields
description: Use when a field technician wants the in-memory stub to record fields they have already approved, and no field that is still unapproved.
---

# Stub-write approved fields

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Call `record_review()` with decision `technician_stub_write`. The review must name each field again with `approved` true. A field that was not approved on an earlier review is refused. The write is the JSON in the reply. It is not a production work order. This starter does not assign a weight to a skill.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/complete.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Input | A draft that already has field approvals, and a review that names the fields to write. |
| Side effect | `stub_write.executed` becomes true only when at least one previously approved field is written. `production_system_written` stays false. `executed` stays false. |

## What you may do

1. Show the field ids that were written and the field ids that were refused.
2. Say the store is `in_memory_stub`.
3. Repeat that the job is not closed.

## What you must not do

- Write a field that was not approved earlier.
- Close the job, raise a charge, order parts, or contact the customer.
- Say that a production system was updated.
- Clear a hazard because the technician acknowledged it.
- Send the regulation 9 written summary. `written_summary_sent` stays false.

## Approval gates

The earlier field approval is required. This skill does not create that approval. A review that tries to close, charge, order, or contact is refused, and nothing is written.
