# Microsoft Foundry

Optional. No Foundry resource is deployed by this folder. The runnable sample does not call a model. It runs `src/classify.py` on the synthetic fixtures.

A short note may be written from the JSON that `classify_document()` already returned. The note may use only fields that are already in that JSON. It must not choose a class the JSON left unset. It must not say that a statutory clock was met. It must not say that the document was filed.

The content hash, the class, the destination, the suppressed counts, and the approval step stay in the Python core. A note that disagrees with the JSON is not the record.

This starter does not call a model. A live Microsoft Foundry run has not been done. The smoke test in `eval/smoke_report.json` is a deterministic run of the Python core. It is not a model score.

A production deployment that did call Foundry should use UK South or UK West. This repository cannot enforce that region. Prompt shields were not opened on 25 November 2026. Treat that product behaviour as unverified.
