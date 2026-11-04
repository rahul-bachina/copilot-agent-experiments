---
name: read-advice-reports
description: Use when a caseworker has loaded a synthetic advice bundle and wants each report listed before any section is filled.
---

# Read the advice reports

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You list the reports already in the file. You do not decide what the child needs. The caseworker authors the final text. Autonomy A3 is never a recommendation.

## What you may do

1. Read the bundle the caseworker already loaded. Do not fetch a case from a local authority system.
2. If `synthetic` is not true, stop. Do not copy the text.
3. List each `report_id`, the advice type, the author role, and the date. Do not paste a paragraph into a section in this skill.
4. If a field is a name, a date of birth, an address, an NHS number, a UPN, a ULN, or a school name, stop. Do not echo the value.
5. Hand the same file to the assemble-ehcp-draft skill. Do not summarise the child.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the bundle already loaded | None | Once, at the start |
| Web search, including legislation.gov.uk | Forbidden | Do not refresh a citation |
| Decide, send, or edit the final plan | Forbidden | No such tool is attached |

## Memory

The harness overview says this harness supports memory. An administrator control to turn it off was not found on the page opened on 4 November 2026. Do not use it for the advice, the child reference, or the draft.

## Stop

When the report list is shown, stop this skill. The next skill files the paragraphs. It still does not decide.
