# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness. It is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 12 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

The skills in `skills/` tell the agent when to call the Python core. They do not tell it to delete, unpublish, move, or change permissions. This starter does not assign a weight to a skill.

## Skills

| Skill | Use when |
|---|---|
| `propose-curation-actions` | A site owner has one synthetic snapshot and no draft yet |
| `record-site-owner-approval` | A draft exists and the site owner is approving, rejecting, or deferring named proposal ids |
| `queue-sensitive-page` | The draft already queues a page and that queue has to be reviewed first |
| `apply-approved-curation` | The named proposals are already approved and the site owner asks for the stub receipt |

## Tools

The contracts are in `schema/`. `curate_tool.schema.json` has no approval field and no delete field. `approval_tool.schema.json` allows `approve_actions`, `reject_actions`, or `defer`. It does not allow delete, unpublish, move, or a permission change. `stub_tool.schema.json` takes a confirmed draft and describes a stub that does not call SharePoint or Microsoft Graph.

## What was not verified

Skill upload, memory, and file creation were not exercised in a tenant. The overview says this harness can create and edit Word, Excel, PowerPoint, and PDF files. This experiment does not use that feature. The GitHub Copilot harness knowledge-sources page was not opened. Billing is Copilot Credits, on the overview's own words. The billing page was not opened. No price is stated here.
