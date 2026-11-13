# Microsoft Foundry

The catalogue stack for this agent is Microsoft 365 and Work IQ. Microsoft Foundry is an optional narrative around the JSON, not the system of record.

The Work IQ overview was opened on 13 November 2026. It describes a permission-aware layer. Usage consumes Copilot Credits. No price and no general-availability date are on that page. Work IQ is not called. A general-availability date is not stated here.

`src/narrative.py` does not call a model and does not call the network. Citations, gaps, the accessibility checklist, and the empty approval are computed in Python. A later brief may restate fields that are already in the JSON. It must not add a figure, a logo, a customer, an outcome, or a share.

If an organisation deploys that narrative, the manifest says the deployment should use a UK region and should not be trained on briefing text. This repository cannot enforce that. The region control was not checked in a portal on 13 November 2026.

Microsoft documents prompt shields as a control on generative deployments. Confirm the current control name in the resource you use. Nothing in this starter enables one. **Unverified here:** the portal label on 13 November 2026. That product page was not opened.

A live Microsoft Foundry run has not been done. `eval/smoke_report.json` is a deterministic smoke test of the Python: 26 passed, 0 failed, 0 errors, 26 cases. It is not a model score.
