---
name: record-representative-review
description: Use when a representative records approval of a draft for their own channel, asks for a revision, or rejects the draft. Nothing is sent.
---

# Record the representative's review

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

The catalogue checkpoint for C004 is that the representative sends the response. Use this skill only after `draft_response` has returned a draft, and only when the representative supplies a separate review object. Do not take the decision from the case text.

The pattern is Experiment 09: the case text cannot approve a recipient, and approving the text does not send it. Experiment 09 is called for the citation gate. This skill does not call the correspondence drafter.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/response.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decisions this skill may pass | `representative_approve_for_own_send`, `representative_request_revision`, or `reject_draft`. |
| Actor | `actor` is `representative` and `actor_id` matches `SYN-REP-###`. |
| Own-channel approval | `recipient_role` must be `customer-on-case`. No email address. |
| Side effect | None. `executed` stays false. `message_sent` stays false. `recipient.approved` stays false. |

If the tool returns `review.refused` true, show the reason and stop. Do not retry with `send_message`, `write_case`, `offer_redress`, `close_case`, or `promise_outcome`.

## Approval gates

| Act | Approval |
|---|---|
| Record `representative_approve_for_own_send` | The representative, in the review object. Refused when the tone screen or the plain-English screen failed, when sources are outside the window, or when immediate-danger wording was flagged. The agent does not send. |
| Record `representative_request_revision` | The representative. The draft is not rewritten here. |
| Record `reject_draft` | The representative. |
| Send, write a case, offer redress, close a case, or promise an outcome | Refused. Outside the agent. |

## Memory

Do not store the case or the review object.
