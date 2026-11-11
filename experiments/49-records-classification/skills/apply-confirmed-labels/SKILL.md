---
name: apply-confirmed-labels
description: Use when the records manager has already confirmed every classification field and asks for the stubbed label receipt, which does not call Purview and does not delete or downgrade the record.
---

# Apply a confirmed label stub

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use this skill only when `flags.classification_confirmed` is already true. Call `apply_confirmed_labels()`. If the stub is refused, say the reason from the JSON and stop.

This starter does not assign a weight to a skill.

## Tool contract: `apply_confirmed_labels`

| | |
|---|---|
| Implementation | `apply_confirmed_labels()` in `src/classify.py`. |
| Schema | `schema/label_tool.schema.json`. |
| Side effect | A stub receipt in the JSON. `purview_called` stays false. `labels_applied_in_tenant` stays false. Nothing is deleted, disposed of, moved, or downgraded. |

## What you may do

1. Show the stub's retention label name and sensitivity label name, and say they were not sent to Microsoft Purview.
2. Say a configured disposal action was named and not executed.
3. If the reason is `downgrade_refused`, `legal_hold_blocks_destroy`, `stale_sources`, or `outside_code_scope`, stop. Do not retry with a lower marking.

## What you must not do

- Call Purview, SharePoint, or an EDRMS.
- Describe the stub as a label that is now on the record.
- Delete or move the record because the stub was recorded.

## Approval gates

The records manager's earlier confirmation is the approval gate. This skill does not add a second, silent approval. The human route remains available. The agent still does not dispose of the record.
