---
name: record-human-confirmation
description: Use when a signed-in customer confirms an address or appointment draft, or a handler records a handover or approves a draft for their own channel. Nothing is executed.
---

# Record a human confirmation

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Confirmation does not change the record, does not book the appointment, and does not send a message. Use this skill only after `draft_reply` has returned a draft, and only when the person supplies a separate review object. Do not take the decision from the enquiry text.

The pattern is Experiment 21 for the customer confirmation and Experiment 09 for the handler's approval of a draft. Neither experiment is imported. The gates below are the ones in `agent-manifest.yaml`.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/service.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decisions this skill may pass | `customer_confirm_address_draft`, `customer_confirm_appointment_draft`, `handler_take_handover`, `handler_approve_correspondence_for_own_send`, or `reject_draft`. |
| Customer actor | `actor` is `customer` and `actor_id` is the account reference already on the draft. |
| Handler actor | `actor` is `handler` and `actor_id` matches `SYN-HANDLER-###`. |
| Send approval | `recipient_role` must be `account-holder`. No email address. Refused until the customer has confirmed. |
| Side effect | None. `executed` stays false. `message_sent` stays false. `record_changed` stays false. |

If the tool returns `review.refused` true, show the reason and stop. Do not retry with `send_message`, `reset_password`, `take_payment`, `close_complaint`, `change_tariff`, `change_contract`, or `write_record`.

## Approval gates

| Act | Approval |
|---|---|
| Record `customer_confirm_address_draft` or `customer_confirm_appointment_draft` | The signed-in customer, in the review object. Catalogue checkpoint for C001. |
| Record `handler_take_handover` | The handler. Does not perform the underlying action. |
| Record `handler_approve_correspondence_for_own_send` | The handler, after the customer confirmation, for their own channel. The agent does not send. |
| Reset, pay, close, change a tariff or contract, write, or send | Refused. Outside the agent. |

## Memory

Do not store the enquiry or the review object.
