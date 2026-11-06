---
name: explain-comparison-row
description: Use when a wording specialist asks for one comparison row to be restated with its clause citations and any not stated cell.
---

# Explain one comparison row

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You restate one row from the draft. You copy the cited text. You do not paraphrase it into a coverage opinion. You do not say which meaning is more favourable to the consumer. Section 69 of the Consumer Rights Act 2015 was read and is not applied by this skill. Autonomy A3 is never a recommendation.

This skill does not list trigger phrases and does not assign routing weights. The generative-orchestration guidance opened on 6 November 2026 says names carry more weight than descriptions. Whether that planner selects this harness was not stated on the harness overview.

## What you may do

1. Name the row id, the topic, and the subject key the caller supplied. The subject was not inferred from the prose.
2. For each stated quote, give the wording id, the clause reference, the document, the page, the paragraph, the line range, the verdict, and `other_failures`.
3. For a cell whose status is `not_stated`, say `not stated` and that nothing was inferred. For `not_quoted`, say the wording's documents were not used, which is not a finding that the topic is absent.
4. If `basis_of_contract_words` is true, say those words appear in the cited span. `basis_clause_of_no_effect` stays null.
5. Do not draft replacement wording.

## Approval gates

Explaining a row is not validation. The wording specialist validates the interpretation outside this skill. You do not contact a broker and you do not write a policy administration system.

## Memory

Do not store the row or the clause text. Do not use memory for this explanation.

## Stop

When the row has been restated, stop.
