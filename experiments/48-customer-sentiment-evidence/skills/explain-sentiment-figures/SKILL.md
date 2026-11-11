---
name: explain-sentiment-figures
description: Use when an analyst asks what a count, a sample size, a Wilson interval, or a quote in an existing evidence pack refers to, without confirming the pack or publishing it.
---

# Explain the figures

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Read the JSON `prepare_pack` already returned. Do not recompute a proportion in prose and present it as a new figure. If the analyst needs a different as-of date, call `prepare_pack` again. Autonomy is A0. Explaining a figure does not confirm the sample frame and does not publish.

The harness overview opened on 11 November 2026 says this harness supports skills. Use this skill when the description above matches the request. This starter does not assign a weight to a skill.

## Tool contract

| | |
|---|---|
| Implementation | The pack JSON from `src/evidence.py`. |
| Input | A pack already produced. No new customer text. |
| Side effect | None. `ready` is unchanged. `published` stays false. |

## What you may do

1. Point at `distribution.overall.n` and say it is unique voices, not the number of records supplied.
2. Point at `not_counted_as_extra_voices` when a duplicate was dropped from the denominator.
3. Say the Wilson interval comes from Experiment 07 and is not a model confidence score.
4. Point at a quote's `record_id`. Do not invent a second quote.
5. If `number_verified` is false, say so.

## What you must not do

- Add theme `unique_voice_count` values together and call the sum the population.
- Say the interval shows that PRIN 2A.5 or PRIN 2A.6 was met.
- Say a sentiment code is a conclusion about the person behind the record id.
- Mark the pack ready. That is `confirm-sample-frame`.
- Publish or contact anyone.

## Approval gates

This skill does not record `human_approval`. The analyst confirms the sample frame and the limitations only through `record_review`.
