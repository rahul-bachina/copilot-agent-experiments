# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03.

The agent reads pinned synthetic files. It writes one in-memory staging row after the named company secretary approves the content hash. It does not circulate, publish, file, or send. High-risk actions in the manifest are disabled.

## What was not opened

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 24 November 2026. A deployment that uses them should confirm the current product behaviour. Treat the following as unverified:

- Entra Agent ID as an identity for this agent.
- Conditional Access applied to an agent.
- A Power Platform DLP policy that blocks the connectors this starter does not enable.
- Microsoft Foundry prompt shields on the optional note.
- Key Vault for a key this starter does not hold.
- Purview labels beyond the marking rules in `src/marking.py`.
- Application Insights as a log store. This starter writes no application log.
- Work IQ as a permission-aware read of a live library. Catalogue row L010 names it. This starter does not call it.

Companies Act 2006 sections 171 to 177 and section 248 were opened on legislation.gov.uk on 24 November 2026. UK Corporate Governance Code 2024 Principles F and I and Provisions 7 and 16 were read from a company-hosted PDF. The FRC media file was not opened. The Code was not opened on legislation.gov.uk. That match is unverified. The quotes are not a finding that a duty or a principle was met.

## Data

Paper bodies are not copied. A phone number, email address, date of birth, postal address, personal name, or UK identifier is counted and not stored. The output is not described as anonymised. A legal hold and every retention label are kept. A SECRET cover is taken from the page even when the metadata says OFFICIAL. The higher marking is kept. A count of people below 5 is not published. Five is this starter's threshold, not an anonymisation claim.

A self-declared role or clearance in a paper is not the directory. A caller-supplied agenda or terms of reference is not the pinned source.

Samples are synthetic. Northmere Holdings Limited is fictional.
