# Microsoft Foundry

Optional. No Foundry resource is deployed by this folder.

A short note may be written from the JSON that `prepare_comparison()` already returned. The note may use only fields that are already in that JSON. It must not add a quotation, a party, or a case study. It must not say that a change is immaterial. It must not say that the document was approved, edited, published, or sent. It must not give legal advice.

The content hash, the document hashes, the material flags, and the confirmation step stay in the Python core. A note that disagrees with the JSON is not the record.

This starter does not call a model. A live Microsoft Foundry run has not been done. The smoke test in `eval/smoke_report.json` is a deterministic run of the Python core. It is not a model score.

A production deployment that did call Foundry should use UK South or UK West. This repository cannot enforce that region. Prompt shields were not opened on 25 November 2026. Treat that product behaviour as unverified.
