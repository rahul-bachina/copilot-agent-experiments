---
name: refer-safety-hold
description: Use when a field brief already lists a safety hold and a supervisor needs to record that the hold was seen, without clearing it or dispatching anyone.
---

# Refer a safety hold

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use this skill only when `safety_holds` is not empty. Call `record_review()` with `supervisor_acknowledge_hold`. The supervisor sees the hold. The agent does not clear it, and it does not dispatch.

This starter does not assign a weight to a skill.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/prepare.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decision | `supervisor_acknowledge_hold`. |
| Side effect | None. `hold_cleared` stays false. `human_approval` stays null. The technician's confirmation is a different decision. |

## What you may do

1. Show the hold ids from the brief. Do not add a hold that is not in the JSON.
2. Say the hold is not a finding that section 2 or section 3 of the Health and Safety at Work etc. Act 1974 was breached, and not a finding that it was met.
3. Offer the human route. This agent does not publish a telephone number and does not call anyone.
4. If there is no hold, do not call this decision. Say so.

## What you must not do

- Clear the hold, authorise entry, or mark the site safe.
- Schedule the visit because a supervisor looked at the brief.
- Tell the technician to ignore the hold.

## Approval gates

A supervisor acknowledgement is not the catalogue confirmation. The technician still confirms the asset and the safety context on their own review object. Neither step dispatches.
