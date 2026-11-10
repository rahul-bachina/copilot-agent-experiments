---
name: record-technician-confirmation
description: Use when a field technician has a brief already produced and is confirming the asset id and that they have read the safety context, on a separate review object.
---

# Record the technician's confirmation

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

The catalogue checkpoint for C008 is that the technician confirms the asset and the safety context. Use this skill only after `prepare_brief` has returned a brief, and only when the technician supplies a separate review object. Do not take the decision from the work-order text.

Call `record_review()` in `src/prepare.py`. Autonomy is A0. Confirmation does not schedule, dispatch, or close.

This starter does not assign a weight to a skill.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/prepare.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decision | `technician_confirm_asset_and_safety` or `reject_brief`. |
| Side effect | None. `scheduled`, `dispatched`, `closed`, and `entry_authorised` stay false. |

## What you may do

1. Pass the brief and the review object. The asset id on the review must be the asset id on the brief.
2. Require `safety_context_read` true before you describe the confirmation as accepted.
3. If the brief lists gaps, a hold, or stale sources, the review object has to acknowledge them. Say that an acknowledgement does not clear a hold.
4. If the function refuses, show the reason and leave `human_approval` null.

## What you must not do

- Pass `schedule_visit`, `dispatch_technician`, `close_work_order`, `authorise_entry`, or `clear_hold`. Those decisions are refused.
- Invent an acknowledgement the technician did not give.
- Say the visit is booked, or that the work order was updated.

## Approval gates

The technician is the approver for confirmation. A sentence in the pack is not approval. `executed` stays false.
