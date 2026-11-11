# Microsoft Foundry

The catalogue names Microsoft Fabric and Dynamics 365. A later deployment might add a short narrative around the JSON this core already produced. That narrative is optional. The counts, the quotes, the limitations, the stale flags, and the empty approval stay in `src/evidence.py`.

No Foundry resource is created in this folder. No model is called. `model_called` is false.

If a narrative is added later:

- Run it in UK South or UK West. This repository cannot enforce the region. Whether those regions are available for a given model was not checked on 11 November 2026.
- Pass the JSON, not the raw complaint or survey text.
- Do not train on customer text.
- Turn on prompt shields if a model sees untrusted text. The product page was not opened on 11 November 2026. The portal label and the filter behaviour are unverified here. A filter is not a substitute for having no publish tool and no contact tool.
- The analyst still confirms the sample frame and the limitations. The model does not.

The groundedness evaluator was not opened for this experiment. This folder does not call it.

A live Microsoft Foundry run has not been done. `eval/smoke_report.json` is a deterministic smoke test of the Python.
