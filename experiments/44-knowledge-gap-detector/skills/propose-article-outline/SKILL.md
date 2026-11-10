---
name: propose-article-outline
description: Use when a knowledge manager wants the draft article outline already in a gap review explained, with its evidence links and without publication.
---

# Propose an article outline

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Read `outlines` from the JSON `detect_gaps()` already returned. Do not write a new outline. Do not fill a section with customer text. Autonomy is A0. The knowledge manager confirms gaps. You do not publish.

Use this skill when the description above matches the request. This starter does not assign a weight to a skill.

## Tool contract

| | |
|---|---|
| Implementation | The `outlines` array on the review from `src/gaps.py`. |
| Input | The review JSON for this run. |
| Side effect | None. Each outline has `published` false and `edited` false. |

## What you may do

1. Show `outline_id`, `kind`, `proposed_title`, `sections`, and `evidence_links`.
2. Say the sections are a starter list. The knowledge manager writes the article, outside this agent, if they decide to.
3. If the review outcome is `stale_sources`, say outlines were omitted because the pinned sources are outside the window.

## What you must not do

- Publish the outline or save it as a knowledge article.
- Add a section the JSON does not contain.
- Copy a query into "the question, written by the knowledge manager".
- Choose a winner when the finding kind is `conflict`.

## Approval gates

An outline is not approval to publish. The knowledge manager confirms the gap first, in `record-gap-confirmation`, and still publishes outside this agent. This skill does not publish.
