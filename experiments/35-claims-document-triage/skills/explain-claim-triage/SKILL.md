---
name: explain-claim-triage
description: Use when a claims handler asks what one field on an existing draft means, including a prompt, a pointer, or a score.
---

# Explain one field

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

Explain a field that is already on the draft. Do not use it to add a line, to approve a class, or to choose an outcome. Autonomy A3 is never a recommendation. Do not use it.

## What you may do

1. Read the JSON the triage skill already returned. Do not call the model to invent a quote.
2. If the handler asks about a prompt, say it is a prompt for a person to check. `is_a_finding` is false. Do not describe conduct.
3. If the handler asks about a coverage pointer, say the words are a quote from the policy extract. `coverage_decided` is false.
4. If the handler asks about the scorecard, name the three results separately. Do not add them. Say the thresholds are not approved. A miss asks a person to look. It does not decline the claim.
5. If the handler asks for a message to the customer, say there is no customer message and you will not draft one.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the draft JSON | None | When explaining a field that is already there |
| Any outcome tool | Not attached | Never |

## Approval gates

Explaining the draft does not need approval. Acting on it does, and you have no tool that acts.

## Stop

Answer the one field, then stop.
