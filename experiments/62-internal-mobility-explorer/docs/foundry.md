# Microsoft Foundry

Optional. No Foundry resource is deployed from this folder. A live model run has not been done. The smoke test in `eval/smoke_report.json` is a deterministic Python run, not a model score.

If a tenant later sends the JSON to Microsoft Foundry for a short note:

- The deployment should be in UK South or UK West. This repository cannot enforce that.
- The note may use only fields already in the JSON.
- It may not add a vacancy, change a closing date, set `hr_seen.recorded`, mark eligibility as decided, or say interest was shared.
- It may not rank or score, and it may not say who should get the job.
- Prompt shields were not opened on 18 November 2026. Treat that product behaviour as unverified.
- A key, if one is used, belongs in Key Vault. There is no key in this folder.

The vacancy list, the eligibility wording, the markings, and the human gates stay in `src/explore.py`.
