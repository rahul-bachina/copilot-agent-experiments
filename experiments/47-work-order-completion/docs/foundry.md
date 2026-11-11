# Microsoft Foundry

The catalogue names Dynamics 365 and Power Platform. A later deployment might add a short narrative around the JSON this core already produced. That narrative is optional. The field values, the clashes, the stale flags, and the empty approval stay in `src/complete.py`.

No Foundry resource is created in this folder. No model is called. `model_called` is false.

If a narrative is added later:

- Run it in UK South or UK West. This repository cannot enforce the region.
- Pass the JSON, not the visit notes and not a door code.
- Do not train on work orders.
- Turn on prompt shields if a model sees untrusted text. The product page was not opened on 11 November 2026. The portal label and the filter behaviour are unverified here. A filter is not a substitute for having no close tool.
- The technician still approves each field. The model does not.

The groundedness evaluator and Document Intelligence were not opened for this experiment. This folder does not call them.

A live Microsoft Foundry run has not been done. `eval/smoke_report.json` is a deterministic smoke test of the Python.
