# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03.

The agent reads pinned synthetic files. It writes one in-memory staging row after the named tester approves the content hash. It does not send. High-risk actions in the manifest are disabled.

## What was not opened

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 23 November 2026. A deployment that uses them should confirm the current product behaviour. Treat the following as unverified:

- Entra Agent ID as an identity for this agent.
- Conditional Access applied to an agent.
- A Power Platform DLP policy that blocks the connectors this starter does not enable.
- Microsoft Foundry prompt shields on the optional note.
- Key Vault for a key this starter does not hold.
- Purview labels beyond the marking rules in `src/marking.py`.
- Application Insights as a log store. This starter writes no application log.

UK Corporate Governance Code 2024 Provision 29 and FCA SYSC 4.1.1R are quoted as context in `src/sources.py`. They were not opened on legislation.gov.uk. That currency is unverified. The quotes are not a finding that either text was met.

## Data

Evidence bodies are not copied. A phone number, email address, date of birth, postal address, personal name, or UK identifier is counted and not stored. The output is not described as anonymised. A legal hold and every retention label are kept. A SECRET cover is taken from the page even when the metadata says OFFICIAL. A count of people below 5 is not published. Five is this starter's threshold, not an anonymisation claim.

Samples are synthetic. Ashcombe Borough Council is fictional.
