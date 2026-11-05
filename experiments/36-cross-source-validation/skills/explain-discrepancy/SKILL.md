---
name: explain-discrepancy
description: "Use when a reviewer wants the deterministic reason for one already classified field restated in plain language."
---

# Explain one discrepancy

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You restate the `explanation` already on the fact row. You do not change the class, you do not choose which source is right, you do not edit a record, and you do not contact anyone. Autonomy A3 is never a recommendation. The explanation was not authored by a model. `explanation_authored_by_model` stays false.

The skills overview opened on 5 November 2026 says the orchestration runtime invokes a skill when a request matches the skill's purpose, from the user's message and the skill's description. This starter does not assign routing weights. It does not use trigger phrases as the selector. A page that describes classic orchestration was not opened.

## What you may do

1. Read the fact row the comparison already returned. Do not run a new classification and do not call a model to decide the class.
2. Repeat the class, the reason, and the fixed explanation sentence.
3. Point at the citations. Do not drop a citation and do not add a source that is not on the row.
4. Say the sentence is not a finding that either source is right.
5. Leave `resolved` as it is. Do not mark a material row resolved.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `explain_discrepancy` | None. Reads one fact row | When the reviewer asks what a class means |
| `choose_source` | Not callable. It always raises | Never |
| `edit_record` | Not callable. It always raises | Never |
| `contact_party` | Not callable. It always raises | Never |
| `lookup_register` | Not callable. It always raises | Never |
| `record_reviewer_resolution` | Not an agent tool | Never |

## Approval gates

- Restating a sentence does not need approval.
- Relying on it does. The reviewer resolves every material discrepancy.
- You do not edit a record to match the explanation.

## Memory

Do not write the fact row into agent memory. The harness overview opened on 5 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this explanation.

## Stop

When the sentence has been restated, stop. The class is unchanged.
