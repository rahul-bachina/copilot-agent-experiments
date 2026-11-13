---
name: review-assumptions
description: Use when a confirmed synthetic workbook needs an inventory, formula checks, paired-value comparison, and a computed sensitivity, without editing the file.
---

# Review the assumptions

This skill is the skills layout the catalogue calls the GitHub Copilot harness. The harness overview opened on 13 November 2026 names that layout the Microsoft Copilot harness. That page says the harness can edit Excel. This skill must not.

Call `review_workbook()` in `src/review.py`. Do not reimplement the formula reader. Do not add a number the JSON did not compute. Autonomy is A0. The model owner has already confirmed the scope. This starter does not assign a weight to a skill.

## Tool contract: `review_workbook`

| | |
|---|---|
| Implementation | `review_workbook()` in `src/review.py`. |
| Schema | `schema/review_tool.schema.json` and `schema/confirm_tool.schema.json`. |
| Input | One synthetic pack, one confirmation, and an as-of date. `synthetic` must be true. `model_id` must match `SYN-MDL-` and four digits. |
| Side effect | None. The workbook hash is checked before and after the read. `executed` is false. |

## What you may do

1. Pass the synthetic pack, the confirmation, and the as-of date.
2. Show the label `REVIEW FOR THE MODEL OWNER. THE WORKBOOK WAS NOT CHANGED. NO ASSUMPTION WAS JUDGED.` before any finding.
3. If `outcome` is `safeguarding_for_human`, stop and say a person must take the text. Do not quote the phrase.
4. If `outcome` is `stale_sources`, say the pinned pages are outside the window and do not list findings.
5. List `ranges_inspected`, `inventory`, `hardcoded_literals`, `inconsistent_formulas`, `broken_references`, `circular_references`, `paired_assumptions`, and `questions` exactly as returned.

## What you must not do

- Edit the workbook or say that a cell was written.
- Say an assumption is right, wrong, correct, or incorrect.
- Invent a benchmark or a typical rate.
- Choose which of two paired values is the right one.
- Copy personal data or an instruction sentence out of a cell.
- Remove `OFFICIAL-SENSITIVE` or `legal-hold` from the report.

## Approval gates

Scope confirmation is a separate object. The model owner still has to read the report. This skill does not set `findings_accepted`.
