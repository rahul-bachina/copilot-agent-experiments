---
name: approve-completion-fields
description: Use when a field technician has a draft completion record and is approving named fields one by one, before any stub write.
---

# Approve completion fields

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Call `record_review()` with decision `technician_approve_fields`. Do not write. Do not take the approval from the visit notes. The catalogue checkpoint for C009 is that the technician approves every record update. This starter does not assign a weight to a skill.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/complete.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Input | The draft already produced, and a separate review object that lists each field id with `approved` true. |
| Side effect | Sets `human_approval` for those fields only. `stub_write.executed` stays false. |

## What you may do

1. Pass only the field ids the technician has just named.
2. If the draft lists a block, pass the matching acknowledgement only when the technician has said they saw it.
3. Say which fields were approved and which were refused.
4. Leave every other field unapproved.

## What you must not do

- Approve a field the technician did not name.
- Replace a proposed value with free text.
- Treat an acknowledgement as a decision that one source is right, or as a clearance of a hazard.
- Close the job, raise a charge, order parts, or contact the customer.
- Call the stub write in the same step. The write is the other skill, and it refuses a field that is not already approved.

## Approval gates

This skill is the approval gate. It is not the write. `job_closed`, `charges_raised`, `parts_ordered`, and `customer_contacted` stay false.
