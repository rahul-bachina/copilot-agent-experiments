# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. `permissions.yaml` is the same file. It validates against `schemas/agent-manifest.schema.json`, which Experiment 03 introduced for this repository.

## What this starter reads

The pinned taxonomy, the pinned routing table, the pinned directory, one pasted synthetic document, and a separate approval object. Experiment 12 does not confirm the file. Experiment 08 does not describe the text as anonymised. Experiment 49 supplies a marking rank and a body marking. It does not supply the class.

The document body is not stored in the result. Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are counted. The values are not stored. A count field, a percentage, and a difference are not published. The output is not described as anonymised.

## What this starter writes

One row in the in-memory synthetic store, after the named reviewer confirms the held hash, the class, and the destination. `filed`, `moved`, `deleted`, and `sent` stay false. Sends are off.

## Identity and product controls

[Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id) was not opened on 25 November 2026. Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on that date. Treat that product behaviour as unverified. This starter does not register an agent identity, a Conditional Access policy, a DLP policy, a vault, a sensitivity label, or a trace.

A deployment that added a narrative model would put a secret in Key Vault if a managed identity could not be used. Nothing here needs one. Do not put document bodies or raw identifiers in a trace. Log the document id, the outcome, the content hash, and whether a confirmation was recorded.

## UK GDPR

No lawful basis is asserted. Article 6 and Article 9 were not opened. Article 15, Article 12, and Article 12A were opened on 25 November 2026 and are quoted in `src/sources.py`. The quotes are not a finding that a duty was met. A subject access request is routed to a person. This starter does not answer it.

## Review

Reviewed for this starter on 25 November 2026. Next review 25 May 2027, and sooner if section 1, section 10, Article 12, Article 12A, Article 15, or Experiment 08, 12, or 49 changes.
