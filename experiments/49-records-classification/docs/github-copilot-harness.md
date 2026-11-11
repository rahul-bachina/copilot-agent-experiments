# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness. It is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 11 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

The skills in `skills/` tell the agent when to call the Python core. They do not tell it to delete, dispose, move, or downgrade a record. This starter does not assign a weight to a skill.

## Skills

| Skill | Use when |
|---|---|
| `propose-records-classification` | A records manager has one synthetic document and no draft yet |
| `confirm-records-classification` | A draft exists and the manager is confirming or changing every field |
| `queue-sensitive-record` | The draft is already on the human queue |
| `apply-confirmed-labels` | Every field is already confirmed and the manager asks for the stub receipt |

## Tools

The contracts are in `schema/`. `classify_tool.schema.json` has no approval field and no dispose field. `confirmation_tool.schema.json` allows confirm, change, or reject. It does not allow dispose, delete, move, or downgrade. `label_tool.schema.json` takes a confirmed draft and describes a stub that does not call Microsoft Purview.

## What was not verified

Skill upload, memory, and file creation were not exercised in a tenant. The overview says this harness can create and edit Word, Excel, PowerPoint, and PDF files. This experiment does not use that feature. Billing is Copilot Credits, on the overview's own words. The billing page was not opened. No price is stated here.
