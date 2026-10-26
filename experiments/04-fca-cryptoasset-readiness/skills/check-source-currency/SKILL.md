---
name: check-source-currency
description: >
  Check the pinned FCA source catalogue against an as-of date and a stale
  threshold. Use when the reviewer asks whether the citations are current,
  or before anyone relies on a row in the draft register.
---

# Check source currency

Currency is a date comparison. It is not a new reading of fca.org.uk.

## Tool contract

`run_gap_register --sources` (or the `sources_and_currency` array on a register you already built).

| | |
|---|---|
| Side effect | None |
| Input | `as_of` from the reviewer, `stale_after_days` (default 90) |
| Output | One row per pinned source: id, URL, `last_verified`, `page_last_updated`, `currency` |
| Approval to run | Not required |
| Approval to rely | Required once any row is `stale` |

A source is `stale` when `as_of` is more than `stale_after_days` after `last_verified`. Equal to the threshold is still `within_threshold`. The catalogue's `last_verified` is 24 October 2026 until a person edits `src/sources.py` after opening the page again.

## What you must not do

- Do not browse the web to "update" a page, and do not change `last_verified`.
- Do not mark `consultation` or `planned_consultation` as final because a policy says so, or because you think a later paper exists. The stage is pinned.
- Do not hide a `stale` row to make the pack look current.
- `page_last_updated` is the date printed on the FCA page when it was opened. It is not the same test as `last_verified`. Show both.

## Approval gate

If every row is `within_threshold`, say that the pin is inside the threshold the reviewer set, and that this is not a fresh reading of the site.

If any row is `stale` or `as_of_before_verification`, stop and tell the reviewer the register must not be relied on until a person re-opens the pages and updates the catalogue. The Compliance Officer or the MLRO owns that decision. You do not make it.

## Pages in the pin

Only the eight URLs in `src/sources.py`. Handbook sourcebooks and policy-statement PDFs named on those pages were not opened. Do not add them as if their text had been read.
