# Microsoft Foundry

Optional. No Foundry resource is deployed by this folder. The runnable sample is the Python core, and it runs offline on the synthetic files.

A short note may be written from the JSON that `prepare_review()` already returned. The note may use only fields that are already in that JSON. It must not add a quotation, a statute, or a case study. It must not say that a translation has no issues unless the JSON statement says that and the check list is present. It must not say that the translation was published, sent, overwritten, or approved by the agent. It must not clear a high-risk segment.

The content hash, the document hashes, the flags, and the ownership step stay in the Python core. A note that disagrees with the JSON is not the record.

This starter does not call a model. A live Microsoft Foundry run has not been done. The smoke test in `eval/smoke_report.json` is a deterministic run of the Python core. It is not a model score and it is not a translation-quality score.

A production deployment that did call Foundry should use UK South or UK West. This repository cannot enforce that region. Prompt shields were not opened on 26 November 2026. Treat that product behaviour as unverified.
