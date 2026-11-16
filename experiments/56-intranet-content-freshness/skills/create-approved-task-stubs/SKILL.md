---
name: create-approved-task-stubs
description: Use when the content owner has already approved named task ids through record_approval and a JSON stub should be recorded without calling Planner.
---

# Record stubs for approved tasks

This skill is for the Copilot Studio harness that the overview opened on 16 November 2026 calls the Microsoft Copilot harness. The common brief asks for a GitHub Copilot harness layout. The page opened that day does not use those words. Treat the older sentence as unverified against the current overview.

Use this skill only after `record_approval()` has set `human_approval.via` to `record_approval` and the decision is `approve_tasks`. Call `create_approved_tasks()`.

This starter does not assign a weight to a skill.

## Tool contract: `create_approved_tasks`

| | |
|---|---|
| Implementation | `create_approved_tasks()` in `src/freshness.py`. |
| Schema | `schema/create_tool.schema.json`. |
| Side effect | A JSON stub in the response. Planner and Power Automate are not called. `executed` stays false. |

## What you may do

1. Show the stub id, the task title, and the content owner id.
2. Say `created_in_planner` is false and `planId` is null.
3. Say the Power Automate approval action was not sent.

## What you must not do

- Call `POST /planner/tasks`.
- Start a Power Automate approval.
- Edit a page, reassign an owner, or message staff.
- Record a stub for a task id the owner did not name.

## Approval gates

This skill does not approve. It refuses a report whose approval did not come from `record_approval`.
