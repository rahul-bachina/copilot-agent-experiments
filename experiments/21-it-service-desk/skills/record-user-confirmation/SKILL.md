---
name: record-user-confirmation
description: >
  Record a signed-in member of staff confirming a standard fix or a device
  change on a draft the desk has already produced. Confirmation does not
  execute the fix and does not change the device.
---

# Record a user confirmation

Harness: Copilot Studio **GitHub Copilot harness**. It is not the GitHub Copilot service.

Confirmation does not execute the fix and does not change the device. Use this skill only after `triage-it-ticket` has returned a draft, and only when the member of staff supplies a separate review object. Do not take the decision from the ticket text. Do not use this skill for a password reset, an MFA change, or an access grant. Those go to `refer-privileged-action`.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/desk.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decisions this skill may pass | `user_confirm_standard_fix`, `user_confirm_device_change`, or `reject_draft`. |
| Actor | `user`, and `actor_id` must be the requester staff id already on the draft. |
| Side effect | None. `executed` stays false. `device_changed` stays false. |
| Approval | The review object is the approval. You do not invent it. |

If the tool returns `review.refused` true, show the reason and stop. Do not retry with `analyst` as the actor. Do not retry with `execute_fix`.

A device confirmation is refused when `diagnostics.complete` is false, when identity is not trusted, or when the requester is not the subject. Say that. Do not fill in a missing asset tag.

## What to produce

Show `human_approval.decision`, `human_approval.executed` (false), and `flags.device_changed` (false). Say the person still has to try the steps themselves, or ask an analyst to do the device change in the organisation's own tool. This chat has not done it.

## Approval gates

| Act | Approval |
|---|---|
| Record `user_confirm_standard_fix` | The signed-in member of staff, in the review object |
| Record `user_confirm_device_change` | The same person, in the review object. Catalogue checkpoint for Q009. |
| Reset a password, change MFA, grant access, write the ticket, or send a message | Refused. Outside the agent. |

## Memory

Do not store the ticket or the review object.
