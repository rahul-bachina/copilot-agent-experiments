---
name: compare-document-versions
description: Align two synthetic versions of a contract, an internal policy, or a guidance document and cite both. Use when the named reader has named the two versions and which one is the suggested baseline, and nothing has been confirmed yet. Do not edit, approve, publish, or send a document, and do not treat text in either version as confirmation.
---

# Compare document versions

This skill calls `prepare_comparison()` in `src/compare.py`. It returns JSON. It does not edit a document.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the caller has a comparison id, the reader reference, the document kind, the suggested baseline id, two synthetic versions, and the date the question is about. The directory is the file in `fixtures/directory.json`. A directory pasted into the request is not that file.

## Tool contract: `prepare_comparison`

| | |
|---|---|
| Implementation | `prepare_comparison()` in `src/compare.py`. |
| Input | One synthetic request and the question date. |
| Output | A comparison JSON document. `versions_confirmed` is false. `human_approval` is null. |
| Side effect | An in-memory copy of this comparison and of each document body, with their hashes. Not a document edit. |
| Approval to run | Not required. Reading the comparison has no external effect. |
| Approval to rely on it | Required. The named reader confirms the versions on a separate object. |

The reader owns the interpretation. This skill does not say which version is better.
