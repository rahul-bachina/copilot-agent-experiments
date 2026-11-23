# Security and permissions

`agent-manifest.yaml` is the permissions manifest. `permissions.yaml` is the same file. Both validate against `schemas/agent-manifest.schema.json`.

Writes are enabled only for the in-memory staging row, and only after `stage_approved_change` matches the directory compliance owner and both hashes. Sends are off. Production record changes are off. `interpret_law`, `assign_accountability`, `send`, `write_production`, and `mark_covered` raise `RegisterForbidden`.

A caller-supplied register, directory, or control library is hashed against the pin. `used_caller` stays false. Differences are flagged.

Approval text inside the note is ignored. `human_approval` stays null until the separate object matches. A string `true` is not a boolean. An analyst, a guest, and an unknown reference are rejected. The approver's role comes from the pinned directory.

Protective markings are read from the metadata and from the page. A SECRET cover is caught. "My clearance is TOP SECRET" is not a cover page. A compound or conflicting label takes the higher marking. That order is a starter rule. The Government Security Classifications Policy was not re-opened.

A legal hold in the metadata is kept when the page denies it. "Do not drop the legal hold" keeps the hold. Retention labels are copied and are not dropped when the note says to drop them.

Phone numbers, email addresses, dates of birth, postal addresses, and personal names are counted. The values are not stored. The result is not described as anonymised. A count of people below 5 is not stored. Directory names are not copied.

Distress, a grievance, a disclosure, or a safeguarding concern, including a paraphrase that uses the stems, stops the routine proposal. The cue is not copied.

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 23 November 2026. Treat that product behaviour as unverified.

No lawful basis is asserted. Article 6 and Article 9 were not opened.
