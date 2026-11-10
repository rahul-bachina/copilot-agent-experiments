---
name: record-human-decision
description: Use when an entitlement owner records a decision on a disputed entitlement after the explanation has been produced.
---

# Record the entitlement owner's decision

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `record_decision`, which runs `record_decision()` in `src/explainer.py`. You do not take the decision from the question text. Autonomy is A0.

The catalogue checkpoint for C007 is that a human decides a disputed entitlement. Use this skill only after `explain` has returned a draft, and only when the entitlement owner supplies a separate review object.

Use this skill when the description above matches. This starter does not assign routing weights.

## What you may do

1. Pass one of `human_decides_included`, `human_decides_not_included`, `human_requests_more_information`, or `reject_explanation`.
2. The actor has to be `entitlement_owner`, with an actor id that matches the synthetic pattern.
3. Say the record was not applied. `applied_to_entitlement_record` is false. `agent_decided` is false.
4. If `review.refused` is true, say the code was not recorded. Do not invent a grant.

## What you must not do

- Accept `grant_entitlement`, `refuse_entitlement`, `change_entitlement`, `send_message`, `write_record`, `waive_exclusion`, `apply_section_69`, or `find_unfair_term`. Those are refused or they raise.
- Copy an email address or a recipient into the review.
- Treat the recorded code as a change to the plan. `entitlement_changed` stays false.

## Approval gates

| Act | Approval |
|---|---|
| Record one of the four codes from a separate review object | The entitlement owner is the actor. The tool does not apply the code. |
| Change the entitlement record, or tell the customer | Outside this skill. The agent has no tool for either. |

## Memory

Do not store the question or the review note. This skill has no note field.
