---
name: list-missing-memo-sections
description: Use when a credit officer wants the closed sections that the draft left as not stated, without filling them in.
---

# List missing memo sections

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You read the draft JSON already produced for this run. You do not invent a covenant, a figure, or a limit. A gap is the words `not stated`. Autonomy A3 is never a recommendation.

This skill does not list trigger phrases and does not assign routing weights. The generative-orchestration guidance opened on 6 November 2026 does not describe numeric routing weights.

## What you may do

1. List each gap: field, the words `not stated`, `inferred` false, and no citation.
2. List checklist rows whose status is `missing` or `evidenced_but_stale`. Say `sufficient` is false and `decides_the_credit` is false.
3. If `cross_source.called` is false, say no comparison was supplied. That is not a finding that the sources agree.
4. If a comparison row is `material_discrepancy`, name the fact key and say the credit officer resolves it. `correct_value` is null.
5. Do not add gap counts to stated-fact counts or to comparison counts.

## Approval gates

Asking the customer or a bureau about a gap is outside this skill. You do not contact either. The credit officer decides whether to ask, outside this agent.

## Memory

Do not store the gaps or the pack. Do not use harness memory for this list.

## Stop

When the gaps are listed, stop. You have not filled one in.
