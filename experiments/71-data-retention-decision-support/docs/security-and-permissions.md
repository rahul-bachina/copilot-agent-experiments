# Security and permissions

Autonomy A0. Reads are the pinned inventory, the pinned schedule, the pinned directory, and one synthetic note. Writes are off. Sends are off.

`advise_retention()` does not delete, move, relabel, archive, transfer, or send. `record_advice_seen()` records an in-memory acknowledgement bound to the advice hash. `records_changed` stays false. `delete_records`, `dispose`, and `send` raise.

The seen step accepts the directory records owner for that series, or a directory legal owner. A guest, a member of staff, or another series' owner is rejected. A role or a clearance typed into the note is ignored. `pins_seen` must be the boolean true. A string is not coerced. Tampered advice after the hash was taken is rejected.

A legal hold and every retention label are kept. Content is not copied. A marking is taken from metadata and from the page, and a compound label takes the higher tier. The caller's clearance comes from the directory.

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 23 November 2026. Treat that product behaviour as unverified.

The manifest is `agent-manifest.yaml`. `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.

Kill switch: turn the Copilot Studio agent off, or revoke a Foundry credential if one was added. Times are the platform's. This starter has not measured them. Contacts on mereford.example.gov.uk are placeholders.
