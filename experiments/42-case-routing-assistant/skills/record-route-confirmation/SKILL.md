---
name: record-route-confirmation
description: Use when an adviser confirms a proposed service route or accepts a human queue. Confirmation does not reroute, close, or escalate the case.
---

# Record a route confirmation

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use this skill only after `propose_route` has returned, and only when the adviser supplies a separate review object. Do not take the decision from the case text.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/routing.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decisions this skill may pass | `adviser_confirm_proposed_route`, `adviser_accept_human_queue`, or `reject_proposal`. |
| Adviser actor | `actor` is `adviser` and `actor_id` matches `SYN-ADVISER-###` in this starter. |
| Side effect | None. `executed` stays false. `rerouted` stays false. `escalated` stays false. `closed` stays false. |

`adviser_confirm_proposed_route` is only for outcome `proposed_route`. A vulnerability or statutory-clock case uses `adviser_accept_human_queue`. If the tool returns `review.refused` true, show the reason and stop.

## Approval gates

| Act | Approval |
|---|---|
| Record `adviser_confirm_proposed_route` | The adviser, in the review object. Confirmation does not move the case. |
| Record `adviser_accept_human_queue` | The adviser. Does not escalate or close. |
| Reroute, close, escalate, or send | Refused. Outside the agent. |

## Memory

Do not store the case or the review object.
