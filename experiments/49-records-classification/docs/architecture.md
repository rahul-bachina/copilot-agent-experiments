# Architecture

The records manager supplies one synthetic document and an as-of date. Either Copilot Studio harness calls `src/classify.py`. The core calls Experiment 12, Experiment 08, and Experiment 19 in process. It does not call a model and it does not call the network.

The draft has five proposals: file plan, retention entry, disposal action, Government Security Classifications marking, and personal-data indicators. Each has evidence and a confidence level. `human_approval` is null.

The records manager confirms or changes every field on a separate review object. Queued items have to be marked reviewed. The label stub runs only after that confirmation. The stub does not call Microsoft Purview. Delete, dispose, move, and downgrade are not tools of the agent.

## What a tenant would add, and what this starter does not

| Piece | In a tenant | In this starter |
|---|---|---|
| File plan | The organisation's own business classification scheme | A fictional Merrowfield scheme, labelled as configuration |
| Retention | Purview retention labels, or the organisation's schedule | A suggested synthetic label name. Not created in Purview |
| Sensitivity | Purview sensitivity labels | A suggested marking. Not applied |
| Disposition | A person reviews before deletion, if the tenant configures that | Not started. `disposed` stays false |
| Identity | Entra, if the organisation uses it | Not registered. Product behaviour unverified |

## Diagram

The picture is `architecture_diagram.png`, drawn by `generate_diagram.py`. Regenerate it with that script if the boxes change. Matplotlib is used only for the picture. It is not a runtime dependency.
