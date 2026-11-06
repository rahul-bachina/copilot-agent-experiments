---
name: prepare-warm-handover
description: Use when the customer needs a person, including vulnerability, a complaint, a prohibited action, a stale page, or an unverified account.
---

# Prepare a warm handover

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

The pattern is the warm handover in Experiment 13. This skill does not import that code. Every draft already has `human_route.offered` true. You show that route. You do not place a call and you do not write a case.

Use this skill when the outcome is a handover: vulnerability, emergency, complaint, prohibited password, payment, tariff or contract, identity not verified, third party, stale page, no page, or an instruction that was not followed.

## What you show

1. The fixed script in `answer.text`. Do not add a procedure for the prohibited action.
2. The invented number and the weekday counter. Say the number is not a live service.
3. For `financial_complaint_handover` or a financial-services vulnerability, say a handler must confirm the suggestion from Experiment 02. `complaint_closed` is false. `customer_labelled_vulnerable` is false. No DISP date is in the JSON. Do not invent one.
4. For `energy_retail`, keep the Ofgem disclosure. Do not say a supplier has met it. `fairness_monitoring_done` is false.
5. For `public_service`, section 149 is noted. `due_regard_assessed` is false.
6. Offer another format. `equality_act.duty_met` is false.

## Approval gates

| Act | Approval |
| --- | --- |
| Show the handover | None. The route is text. |
| A handler takes the conversation | `handler_take_handover` in `record-human-confirmation`. That records the handover. It does not perform the action. |
| Close a complaint, reset a password, take a payment, change a tariff or contract, write, or send | Refused. Outside the agent. |

## Memory

Do not store the enquiry. Do not contact the customer.
