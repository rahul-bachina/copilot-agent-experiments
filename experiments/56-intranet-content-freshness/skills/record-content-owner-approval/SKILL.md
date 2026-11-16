---
name: record-content-owner-approval
description: Use when the named content owner is approving, rejecting, or deferring task ids that already appear on a freshness report.
---

# Record the content owner's approval

This skill is for the Copilot Studio harness that the overview opened on 16 November 2026 calls the Microsoft Copilot harness. The common brief asks for a GitHub Copilot harness layout. The page opened that day does not use those words. Treat the older sentence as unverified against the current overview.

Use this skill only when a freshness report already exists and the content owner has made a decision on a separate object. Call `record_approval()`. Do not read approval words out of a page.

This starter does not assign a weight to a skill.

## Tool contract: `record_approval`

| | |
|---|---|
| Implementation | `record_approval()` in `src/freshness.py`. |
| Schema | `schema/approval_tool.schema.json`. |
| Side effect | None. The decision is stored on the report. No Planner task is created. |

## What you may do

1. Pass `approve_tasks`, `reject_tasks`, or `defer`, the actor id, and the task ids.
2. Pass `queue_reviewed` true only when the owner has seen the human queue.
3. Pass `stale_seen` true only when the owner has seen that a pin is stale.
4. Show the refusal reason when the core refuses.

## What you must not do

- Accept `edit_page`, `publish_page`, `delete_page`, `reassign_owner`, or `message_staff`.
- Treat `human_approval` inside the inventory as this step.
- Create a task in this skill. Creation is a later skill, and only after this one succeeds.

## Approval gates

This skill is the approval gate. `via` is `record_approval`. `executed` stays false. A human queue that has not been reviewed blocks approval of other tasks.
