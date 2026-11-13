---
name: explain-finding
description: Use when a model owner asks what one finding in an already computed workbook review means, using only fields in that JSON.
---

# Explain one finding

This skill is the skills layout the catalogue calls the GitHub Copilot harness. The harness overview opened on 13 November 2026 names that layout the Microsoft Copilot harness. The page says that harness can edit Excel files. This skill does not, and it does not recompute a number the core did not return.

Explain a field that is already in the JSON from `review_workbook()`. If the field is missing, say so. Do not invent a benchmark to fill the gap. Autonomy is A0. This starter does not assign a weight to a skill.

## What you may do

1. Point at the cell, the literal, the two formula shapes, or the absolute change already in the JSON.
2. Say that a 1 percent shock is the method in `sensitivity.method`, and that `benchmark_used` is false.
3. Say that `chosen` is null on a paired row, so neither source was selected.
4. If the owner asks to change a cell, refuse and point at the human route.

## What you must not do

- Add a "should be" figure.
- Say the assumption is material, immaterial, right, or wrong, except to repeat a sentence the JSON already uses that contains a negation.
- Paste text from `Notes` or from an injection pattern. The report stores types and pattern names only.
- Accept the findings on the owner's behalf.

## Approval gates

The model owner reads the explanation and decides what to do with the workbook. `findings_accepted` stays null. Editing the workbook is outside this skill.
