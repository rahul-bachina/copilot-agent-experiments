# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a tender submission.

## What the core is allowed to do

- Read one synthetic pack and the approved library.
- Quote a library body that passes Experiment 09's citation gate, Experiment 43's tone screen, and Experiment 29's `score_claim`.
- Compare price placeholders with Experiment 36, and withhold the figures.
- Write a local `.docx` from the JSON when the author asks the core to do that.
- Record an acceptance that does not submit the draft.

## What it is not allowed to do

- Submit, send, or upload. `tools.sends` and `tools.writes` are disabled.
- Call Microsoft Graph or the Word JavaScript API. `graph_called` and `word_api_called` stay false.
- Mark a requirement met without a supported citation.
- Copy the requirement text, a certificate number, or a price into the answer.
- Write an assessment summary under section 50.
- Decide that PPN 026, PPN 014, or UK GDPR was met.

## Human approval

Autonomy A1. The author accepts the complete draft before it is used anywhere. That acceptance is `record_acceptance()`. It is refused until every row, gap, and author check has been acknowledged. `used_anywhere` stays false after acceptance. The author uses the file, if they choose to, in their own process.

A person is offered on every result, including a refusal. Unrecognised text goes to the author. It is not marked met and it is not copied.

## Controls named, and what was opened

Opened on 12 November 2026, and described only as far as those pages went:

- Procurement Act 2023 sections 21 and 50.
- PPN 026, its guide, PPN 002, PPN 014, PPN 020, and the NCSC Cyber Essentials overview.
- Copilot Studio harness overview, Word.Body.insertParagraph, and Graph `PUT` content.
- The Office Current Channel note on Agent mode in Word.

These product pages were not opened. Treat the names as unverified here: Microsoft Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Microsoft Purview, and Application Insights. None of those objects is created in this folder.

Work IQ is the catalogue stack beside Microsoft 365. The Work IQ documentation was not opened for this experiment.

## Prompt injection and stale sources

Invitation text is untrusted. A sentence that instructs the agent is not matched. A sentence that negates a claim is not treated as a request to assert it. A prohibited key such as `submitted` or `price` is stripped.

The pinned pages are not refreshed from the web. More than 180 days after 12 November 2026, no library entry is quoted. Equal to 180 days is still inside that window. Experiment 29's own review-stamp window is applied as well. On the library review date, Experiment 09 does not cite the entry.

## Kill switch

Turn the Copilot Studio agent off, remove any Foundry credential used for an optional narrative, or block a later connector for mail, Graph, or a portal with Power Platform DLP. Times in the manifest are the platform's, not a measured drill. The contacts on `northmere.example` are placeholders.
