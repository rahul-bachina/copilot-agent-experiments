# Microsoft Foundry

This experiment does not call Microsoft Foundry. The catalogue stack for G010 is Power Platform and Dataverse. The drafts are deterministic so that an ATRS answer, a date threshold, and a lifecycle gate do not come from a model.

A later deployment might use a model to help a person *word* a narrative they will then type into the inventory. That is a different product. If it is added:

- The manifest has to change in the same change. Today, Foundry is not a tool.
- The model must not calculate lifecycle status, choose a lawful basis, or set `approved`.
- Inventory text stays untrusted. [Prompt Shields](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection) in Azure AI Content Safety are the documented control for jailbreak and indirect injection. This repository does not call that API. Whether a given Foundry project has Prompt Shields switched on was **not verified**.
- Inference should be in a UK region. That is a deployment choice. This repository cannot enforce it.
- G007 would still compare the finished ATRS draft with the inventory record. A fluent paragraph that is not in the inventory is an unsupported claim.

No Foundry resource, model deployment, or evaluation project is created here. The smoke test in `eval/smoke_report.json` is not a Foundry evaluation.
