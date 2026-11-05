---
name: check-submission-citations
description: Use when an underwriter wants a proposed fact checked against a document, page, paragraph, and line in one synthetic submission.
---

# Check a pinpoint

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `check_submission_citations`, which runs `summarise()` with the proposed facts the underwriter pasted. You do not rewrite the fact so that it passes. You do not accept or decline a risk. Autonomy A3 is never a recommendation.

The harness overview opened on 5 November 2026 says this harness supports skills. This skill does not list trigger phrases and does not assign routing weights. The generative-orchestration guidance says a described purpose can select a topic, and that names carry more weight than descriptions. Whether that planner selects skills on this harness was not stated on the harness overview.

## What you may do

1. Pass the synthetic submission, the as-of date, and the proposed facts. Each fact needs a field, the text, and a citation with document id, page, paragraph, line start, and line end.
2. Show one verdict per fact. Show `other_failures` as a list. Do not add those later failures to `failure_count`.
3. A number that is not in the cited lines is `number_or_date_mismatch`. A paraphrase is `span_does_not_support`, even when the number matches. Do not treat shared words as support.
4. If the verdict is not `supported`, say the fact is not adopted. Do not replace it with a guess. If the submission has no line, the extract path says `not stated`. This skill does not invent that line.
5. State `coverage_decision`, `price_suggested`, and `terms_suggested` are null. `broker_contacted` is false.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `check_submission_citations` | None. Reads the submission and the proposed facts | When a pasted fact needs a pinpoint check |
| `accept_risk` | Not callable. It always raises | Never |
| `suggest_price` | Not callable. It always raises | Never |
| `contact_broker` | Not callable. It always raises | Never |
| `write_underwriting_system` | Not callable. It always raises | Never |

## Approval gates

- Checking a fact does not need approval.
- Relying on a supported fact does. The underwriter reads the cited lines.
- You do not call `record_underwriter_review`.

## Memory

Do not store the submission or the proposed facts. The harness overview says this harness supports memory. Do not use it here.

## Stop

When the verdicts are shown, stop. A supported fact is still not a decision to write the risk.
