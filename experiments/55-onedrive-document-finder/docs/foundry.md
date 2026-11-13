# Microsoft Foundry

Optional. No Foundry resource is deployed by this folder.

If a tenant wants a short note for the user, the note has to be written from the JSON `find_documents` already returned. The rank, the reason, the location, the date, the sensitivity label, the withheld counts, and `human_approval` stay in the Python core. The note does not add a file the JSON does not contain, and it does not quote a snippet the JSON left null.

A production deployment should use a UK region. This repository cannot enforce that. Prompt shields were not opened on 13 November 2026. Treat that product behaviour as unverified.

The smoke test in `eval/smoke_report.json` is a deterministic run of the Python. It is not a Foundry evaluation and not a model score.
