---
name: refer-rule-change
description: Use when a queue owner is asked to approve a material change to a routing rule. The record does not edit the rule file.
---

# Refer a rule change

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

A material change to a routing rule needs the queue owner. Catalogue checkpoint for C003. Use this skill only when the proposal already contains `rule_change`, and only with a separate review object.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/routing.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decision this skill may pass | `queue_owner_approve_rule_change` or `reject_proposal`. |
| Owner actor | `actor` is `queue_owner` and `actor_id` matches `SYN-OWNER-###` in this starter. |
| Rule id | Must match `rule_change.rule_id`. |
| Side effect | None. `rules_changed` stays false. `rules_file_changed` stays false. |

If `rule_change.status` is `refused_protected_characteristic`, do not ask the owner to approve it. A protected characteristic is not a feature of a rule. Show the refusal and stop.

## Approval gates

| Act | Approval |
|---|---|
| Record `queue_owner_approve_rule_change` | The queue owner, in the review object. The rule file is not edited. |
| Apply the new rule to the current case | Refused. The proposal was built without it. |
| Approve a characteristic as a feature | Refused. |

## Memory

Do not store the proposed rule as if it were already in `src/rules.py`.
