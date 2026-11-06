---
name: check-memo-citations
description: Use when a credit officer wants one proposed memo sentence checked against a document, page, paragraph, and line.
---

# Check a memo citation

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `check_memo_citations`, which runs `draft_memo()` with the proposed facts the credit officer typed. You do not rewrite the sentence to make it pass. A paraphrase fails. Autonomy A3 is never a recommendation.

The generative-orchestration guidance opened on 6 November 2026 says names carry more weight than descriptions, and that a topic can be invoked by its described purpose and also by trigger phrases. This skill does not list trigger phrases and does not assign routing weights.

## What you may do

1. Pass the synthetic pack, the as-of date, and the proposed fact with its document id, page, paragraph, and line range.
2. Show the one verdict and `other_failures`. Do not add `other_failures` to `failure_count`.
3. If the verdict is not `supported`, say the sentence is not in the cited lines. Do not supply a replacement figure.
4. State `credit_decision` and `limit_set` are null. `sar_filed` is false.

## Approval gates

The credit officer reviews the verdict before any use. You do not approve the sentence as a credit fact, and you do not call `record_credit_officer_review`.

## Memory

Do not store the pack or the proposed sentence. The harness overview says this harness supports memory. Do not use it here.

## Stop

When the verdict is shown, stop.
