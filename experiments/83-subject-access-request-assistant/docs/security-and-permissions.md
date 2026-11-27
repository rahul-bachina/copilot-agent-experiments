# Security and permissions

`agent-manifest.yaml` and `permissions.yaml` are the same bytes. They validate against `schemas/agent-manifest.schema.json`. Autonomy is A1. Writes are off. Sends are off.

## What the agent may read

- One synthetic request and its synthetic records export.
- The pinned directory in `fixtures/directory.json`.
- The pinned systems list in `fixtures/systems.json`.
- A separate route-seen object or disclosure-approval object.
- Experiment 08 `propose()`, with `reversible` false. Matched values are not stored.
- Experiment 12 `intake()`, as an inventory draft. `files_confirmed` stays false. The file content is not copied back into the result.

## What it must not do

- Send a response, delete a record, edit a record, or decide an exemption. Those functions raise `SarForbidden`.
- Trust an approval marker, a role, a clearance, or a directory that arrived inside the request or a record.
- Drop a protective marking, a legal hold, or a retention label. A SECRET cover is read from the content. A compound label takes the higher marking. OFFICIAL-SENSITIVE is not read as OFFICIAL.
- Treat a count of one to four third parties as a published number, a percentage, or a difference. The threshold of 5 is a starter rule, not anonymisation.
- Coerce an unreadable date, an ambiguous date, or a malformed amount such as `£1,25.00`.
- Select one reading of the one-month period. `deadline_decided` stays false.

## Approval binding

`record_disclosure_approval` stores the approved projection and its hash in the process. A caller who edits the package and computes a new hash is rejected with `caller_rehash_rejected` or `content_tampered`. The held hash does not change. Tests cover at least eight kinds of edit: unredacting, adding a document, dropping a redaction, changing the requester, changing the illustrated date, applying an exemption, flipping the legal hold, changing the marking, and others.

The approver reference is checked against the pinned directory. The role has to be an active information governance officer. A guest, an external solicitor, and an inactive officer cannot approve. A string such as `"true"` is not an acknowledgement.

## Product controls not opened

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 27 November 2026. Treat that product behaviour as unverified.
