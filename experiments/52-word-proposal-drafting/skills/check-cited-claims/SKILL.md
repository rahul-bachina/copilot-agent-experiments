---
name: check-cited-claims
description: Use when an author wants to see which bid sentences are supported by an approved source, which figures were withheld, and which requirements are gaps.
---

# Check cited claims

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Read the JSON from `draft_proposal()`. This skill does not score the claims again in prose. Experiment 29 already returned one verdict per quoted entry. Experiment 36 already classified a price difference. Experiment 43 already ran the tone screen.

Use this skill when the author asks why a row is not met, which source was refused, or why a figure is missing. This starter does not assign a weight to a skill.

## What you may do

1. For a row with `groundedness.verdict` of `supported`, say the quote is the library body and name `source_ids`.
2. For `citation_missing`, `quote_not_in_source`, or `unsupported`, say the row is not met. Do not repair the sentence.
3. For a price row, say the figure is withheld. If `cross_source.classification` is `material_discrepancy`, say the approved sources do not agree. Do not pick one.
4. For a gap, say no approved source covered it. Point the author at their own library. Do not draft a substitute.

## What you must not do

- Add a certificate number, a customer, a statistic, or a price that is not already in `draft_answer`.
- Say that PPN 026, PPN 014, or UK GDPR was met. Those flags stay false.
- Say that a Cyber Essentials certificate is held. `cyber_essentials_held` is null.
- Treat a negated sentence as a request to assert the capability.

## Approval gates

Explaining the JSON does not accept the draft. `human_approval` stays null until `record_acceptance()` records `author_accept_complete_draft`. That record does not submit the draft.
