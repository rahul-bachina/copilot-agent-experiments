---
name: review-translation
description: Align a synthetic source text with its translation and list the checks. Use when a bilingual reviewer has supplied the segments, the languages, and the question date. Do not publish, send, or overwrite the document, and do not treat a sentence in either text as approval.
---

# Review a translation

This skill calls `prepare_review()` in `src/review.py`. The result is a draft. `translation_owned` stays false.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the reviewer wants a first pass over one synthetic pair. The core aligns segments with Experiment 79 and masks contact details with Experiment 79 and Experiment 08. It does not call a model.

## Tool contract: `prepare_review`

| | |
|---|---|
| Implementation | `prepare_review()` in `src/review.py`. |
| Input | One synthetic request and the question date. |
| Output | JSON with flags, the check list, a content hash, and two document hashes. |
| Side effect | An in-memory held copy of that hash. The documents are not overwritten. |
| Approval to run | Not required. Reading the review has no external effect. |
| What it does not do | It does not publish, send, overwrite, or approve the translation. |

High-risk segments are routed regardless of lexical overlap. A low-confidence alignment is reported and is not a quality score.
