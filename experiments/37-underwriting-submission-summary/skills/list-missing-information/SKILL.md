---
name: list-missing-information
description: Use when an underwriter wants the closed-list fields that a synthetic submission did not state, without contacting the broker.
---

# List what was not stated

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `list_missing_information`, which reads the draft already produced for this run. You do not infer a value. You do not email the broker to fill a gap. Autonomy A3 is never a recommendation.

The harness overview opened on 5 November 2026 says this harness supports skills. This skill does not list trigger phrases and does not assign routing weights.

## What you may do

1. Read `gaps` from the draft. Each row is a field, the words `not stated`, a null citation, and `inferred` false.
2. Say that a gap is not a finding that Insurance Act 2015 section 3(4) was or was not met, and it is not an enquiry under section 3(4)(b). The underwriter decides whether to ask.
3. If the caller labelled the submission retail, you may point at the PRIN 2A note already on the draft. You do not decide that the firm met the Consumer Duty. If the label is not retail, you do not apply PRIN 2A.
4. Show `gap_count` on its own. Do not add it to `stated_fact_count` or to a case total.
5. State `broker_contacted` is false and `coverage_decision` is null.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `list_missing_information` | None. Reads the draft | When the underwriter asks what was not stated |
| `contact_broker` | Not callable. It always raises | Never |
| `accept_risk` | Not callable. It always raises | Never |
| `suggest_price` | Not callable. It always raises | Never |

## Approval gates

- Listing gaps does not need approval.
- Asking the broker does. That message is outside this skill.
- Deciding that the presentation was unfair does. You do not decide that.

## Memory

Do not store the gaps or the submission. The harness overview says this harness supports memory. Do not use it here.

## Stop

When the gaps are shown, stop. The underwriter has not asked the broker and has not decided coverage or price.
