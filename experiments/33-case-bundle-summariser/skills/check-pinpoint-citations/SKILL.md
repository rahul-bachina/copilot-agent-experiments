---
name: check-pinpoint-citations
description: "Use when a decision-maker has proposed sentences and wants each one checked against the cited page, paragraph, and line."
---

# Check pinpoint citations

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `check_pinpoint_citations`, which runs `summarise()` with `proposed_sentences`. You do not rewrite a sentence so that it passes. You do not recommend an outcome, and you do not make a disclosure decision. Autonomy A3 is never a recommendation.

Generative orchestration on this harness selects from the skill description. This starter does not assign routing weights and does not use classic-orchestration trigger phrases.

## What you may do

1. Pass the synthetic bundle, the as-of date, and the proposed sentences. Each sentence needs a document id, a page, a paragraph, and a line range. Do not pass a prohibited flag.
2. Show the label `DRAFT FOR THE DECISION-MAKER. NOT A DECISION.`
3. Show one row per proposed sentence: the verdict, `other_failures`, and whether the span resolved. Say that `other_failures` are not added to `failure_count`.
4. Say `shown_source` is `proposed`. The extractive sentences are still returned and are not collapsed into `sentence_count`.
5. Say `checker_passed` means no shown sentence failed. It is not an acceptance and it is not a case outcome.
6. If a sentence is `span_does_not_support`, `citation_missing`, `prohibited_action`, or `stale_or_superseded`, leave it failed. Do not offer a replacement outcome.
7. Leave `summary_accepted_as_reading_aid` false. Do not call `record_sentence_review`. It is not an agent tool.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `check_pinpoint_citations` | None. Reads the bundle and the proposed sentences | When a draft needs a pinpoint check |
| `recommend_outcome` | Not callable. It always raises | Never |
| `decide_disclosure` | Not callable. It always raises | Never |
| `find_credibility` | Not callable. It always raises | Never |
| `accept_summary` | Not callable. It always raises | Never |
| `record_sentence_review` | Not an agent tool | Never |

## Approval gates

- Checking a sentence does not need approval.
- Relying on a passed sentence does. The decision-maker reviews every cited sentence.
- A disclosure decision stays with that person. You do not make one.

## Memory

Do not write proposed sentences or citations into agent memory. The harness overview opened on 4 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this check.

## Stop

When the verdicts are shown, stop. Nothing has been accepted, disclosed, or decided.
