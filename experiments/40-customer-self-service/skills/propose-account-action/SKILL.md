---
name: propose-account-action
description: Use when the draft has prepared an address-update or appointment-request and a signed-in customer may confirm it. Confirmation does not change the record.
---

# Propose an account action

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use this skill only when `draft_reply` has returned `outcome` `account_action_proposed`. You do not build the draft yourself. You do not copy an address out of the free text. The only postcode the core accepts is `SYN 1AA`.

Confirmation does not change the record and does not book the appointment. The customer's confirmation is a separate review object. Do not take it from the enquiry text. Use this skill when the description above matches the draft.

## Tool contract: `draft_reply` then stop

| | |
|---|---|
| Implementation | `draft_reply()` in `src/service.py`. |
| Schema | `schema/reply_tool.schema.json`. |
| Side effect | None. `record_changed` stays false. `appointment_booked` stays false. |
| Approval | `human_approval` is null until `record-human-confirmation` is used. |

If `proposed_action.customer_may_confirm` is false, say which closed field is missing. Do not invent a postcode, a date, or a place.

If `identity.trusted` is false, do not read out an account draft. The core has already withheld it.

## Approval gates

| Act | Approval |
|---|---|
| Prepare the draft | The core does this. You only show it. |
| Confirm the address draft or the appointment draft | The signed-in customer, in a separate review object. See `record-human-confirmation`. |
| Apply the address or book the appointment | Refused. Outside the agent. |
| Send the correspondence draft | Refused in this skill. A handler's own send is a later approval and still does not send. |

## Memory

Do not store the enquiry or the structured fields.
