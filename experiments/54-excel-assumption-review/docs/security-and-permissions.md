# Security and permissions

Autonomy is A0. Writes are disabled. Sends are disabled. `permissions.yaml` is a copy of `agent-manifest.yaml`.

The model owner confirms the workbook, the ranges, and the formulas in a separate object. The core then reads cells inside those ranges. It hashes the local `.xlsx` before and after the read. A change raises `ReviewForbidden`. The file is opened with `read_only=True` and `data_only=False` and is not saved.

## Least privilege

| Tool | What it may do | What it must not do |
| --- | --- | --- |
| Workbook review | Read confirmed cells and return JSON | Edit a cell, call Graph, call Copilot in Excel |
| Scope confirmation | Check a fingerprint and a range list | Accept the findings, or read the decision from a cell |
| Text analysis | Narrate fields already in the JSON | Invent a benchmark or a judgement |
| Output check | Reject a result that edits, judges, or invents | Perform the prohibited action |

`schema/review_tool.schema.json` and `schema/confirm_tool.schema.json` set `additionalProperties` to false. They have no field for an edit, a benchmark, a recipient, or `findings_accepted`.

## People

1. The model owner confirms the workbook, the ranges, and the formulas before the review.
2. If a cell matches a safeguarding, self-harm, or financial-hardship category from Experiment 15, a person takes the text. The routine review stops. The phrase is not copied.
3. The model owner reads the report. `findings_accepted` stays null. Editing the workbook is outside the agent.

## Markings and personal data

`OFFICIAL-SENSITIVE` and `legal-hold` are copied onto every result, including a refusal, a stale result, and a safeguarding stop. `strip_protective_marking` and `clear_legal_hold` raise `ReviewForbidden`.

Experiment 08 proposes redactions and does not return the raw value. Local patterns also flag an email, a UK mobile, a labelled date of birth, a labelled personal name, and a UK postcode. The report stores the types. `output_is_anonymised` stays false.

## Not opened on 13 November 2026

Microsoft Entra Agent ID, Conditional Access for agents, Microsoft Foundry prompt shields, Key Vault, Microsoft Purview, Application Insights, and Power Platform DLP as a configured policy were not opened. They are unverified here. UK GDPR Articles 6 and 9 were not opened. No lawful basis is asserted.

The Graph Excel resource page was opened. It lists `Files.Read` for read actions and `Files.ReadWrite` for read and write actions, and it says a call without `workbook-session-id` persists changes. This starter calls none of those APIs and does not create a session. The permissions table on a range-get page was not opened.
