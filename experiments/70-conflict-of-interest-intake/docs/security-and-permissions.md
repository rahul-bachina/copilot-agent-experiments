# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins.

## Identity

The declarant and the officer are references on the synthetic directory. A role or a clearance typed into the declaration is ignored. A directory pasted into the request is compared with the pinned file and is not used.

Entra Agent ID and Conditional Access for agents were not opened on 20 November 2026. Treat that product behaviour as unverified. This starter creates no identity.

## Data

The declaration body is not copied. Phone numbers, email addresses, dates of birth, postal addresses, and personal names are counted by `src/mask.py` and are not stored. Experiment 08 counts UK identifiers. Its redacted text is not copied. The output is not described as anonymised.

A family relationship keeps a label. Article 9(1), opened 20 November 2026, does not list family relationships. Political opinions and the other categories in that paragraph are routed, and the detail is not copied. Article 9(2) is not applied. Article 6 was not opened. No lawful basis is asserted.

A legal hold and every retention label are kept, including on the synthetic row. A SECRET cover is taken from the page even when the metadata says OFFICIAL. The higher label wins. Content above the directory clearance is not copied.

## Tools

`draft_declaration` does not write. `confirm_declaration` writes the in-memory synthetic store when the declarant and the declaration hash match. `record_disposition` stores the officer's words and does not apply them. `record_route_seen` does not stage the declaration.

Sends are off. Production writes are off. `decide_conflict`, `clear_person`, `exclude_supplier`, `approve_person`, `send`, and `write_production` raise.

Power Platform DLP, as a configured policy, was not opened. A flow that added a connector to a mailbox or a live register would need a new manifest first. This folder does not include that connector. Treat a claim about a tenant DLP policy as unverified.

## Pins

Sections 81, 82, and 83 of the Procurement Act 2023, and UK GDPR Articles 5 and 9, were opened on 20 November 2026. The extracts had no "up to date on or before" date. `sources_current` stays false. The declarant sets `pins_seen` to the boolean true before a confirm step. That acknowledgement does not confirm the currency of the text.

## Logging and the switch

This starter writes no application log. Do not put the declaration in a trace. Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.

To stop a local run, do not call `src/declaration.py`. If a team later publishes an agent despite this starter, turn that Copilot Studio agent off and remove any Foundry credential. Contacts in the manifest use `ashcombe.example.gov.uk`. They are placeholders.
