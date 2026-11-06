# Architecture

Catalogue ID B009. Autonomy A1. The credit officer owns the recommendation and every approval. The sample never decides credit.

The diagram is [architecture_diagram.png](architecture_diagram.png). Alt text: a flowchart from the credit officer, through either Copilot Studio harness, into Python that copies cited lines, and back to the credit officer, the MLRO, and the data protection officer, with no core banking post and no SAR.

## What runs

```
Credit officer supplies one synthetic pack and an as-of date
        |
        v
Either Copilot Studio harness (standard, or GitHub Copilot harness)
        |
        v
draft_memo() in src/draft.py
        |
        +-- Experiment 12 inventories the files. No purpose is requested.
        +-- Current paragraphs in the closed section list are copied.
        +-- Experiment 29 checks that a number or an ISO date is in the span.
        +-- Experiment 36 classifies listed fields, if a comparisons object exists.
        |
        v
JSON draft. credit_decision, recommendation, and limit_set stay null.
        |
        v
Credit officer reviews every cited fact before any use. That step is outside the agent.
MLRO decides any SAR. Data protection officer confirms a lawful basis before live processing.
```

`foundry_called` and `fabric_called` stay false. A Foundry product page and a Fabric product page were not opened.

## Human approval points

The agent does not mark any of these done. `agent_marked_any_approval_done` stays false. `draft_approved_for_use` stays false.

1. The credit officer reviews every cited fact against the document, page, paragraph, and line.
2. The credit officer owns the recommendation and any approval or decline, outside the agent.
3. Any limit is set outside the agent.
4. The MLRO decides any SAR.
5. Customer or bureau contact is outside the agent.
6. A core banking or CRM post is outside the agent.
7. The data protection officer confirms a lawful basis, and any Article 9 condition, before live processing.
8. The credit officer re-opens a stale pin before relying on the legal note.

`record_credit_officer_review` is not an agent tool. The command line does not expose it. A recorded reading sets `reading_acknowledged` and leaves `draft_approved_for_use` false.

## What does not run

No model. No network. No Microsoft Foundry call. No Fabric write. No customer or bureau contact. No core banking or CRM post. No SAR. No A3 path.
