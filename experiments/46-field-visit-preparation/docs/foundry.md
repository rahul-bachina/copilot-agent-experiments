# Microsoft Foundry

The catalogue names Dynamics 365 and Microsoft 365. A later deployment might add a short narrative around the JSON this core already produced. That narrative is optional. The holds, the gaps, the stale flags, and the empty approval stay in `src/prepare.py`.

No Foundry resource is created in this folder. No model is called. `model_called` is false.

If a narrative is added later:

- Run it in UK South or UK West. This repository cannot enforce the region.
- Pass the JSON, not the work-order narrative and not a door code.
- Do not train on work orders.
- Turn on prompt shields if a model sees untrusted text. The product page was not opened on 10 November 2026. The portal label and the filter behaviour are unverified here. A filter is not a substitute for having no dispatch tool.
- The technician still confirms the asset and the safety context. The model does not.

The groundedness evaluator and Document Intelligence were not opened for this experiment. Experiment 12 does not call Document Intelligence. This folder does not either.

A live Microsoft Foundry run has not been done. `eval/smoke_report.json` is a deterministic smoke test of the Python.
