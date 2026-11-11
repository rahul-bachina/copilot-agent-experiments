# Architecture

The technician supplies one synthetic completion pack and an as-of date. Either Copilot Studio harness calls `draft_completion` in `src/complete.py`. The same pack and the same date produce the same JSON.

Experiment 46 builds the pre-visit brief when the pack includes a pre-visit pack. A brief the technician already holds is accepted only when its catalogue id is C008, and only the structured ids are kept. Experiment 15 returns indicator categories for the visit text. Experiment 05 illustrates a housing category with officer approval forced off. Instruction clauses are removed. The rest of the sentence stays.

`human_approval` is null. Nothing is written.

The technician then approves named fields on a separate review object. A clash, a safety escalation, a stale pin, or a missing pre-visit context blocks that approval until the review says it was seen. Seeing a hazard does not clear it.

A later review stub-writes only fields that were approved earlier. The stub is the JSON in the reply. `production_system_written` stays false. The job is not closed. No charge is raised. No part is ordered. The customer is not contacted.

## What a tenant would add, and what this starter does not

| Piece | In this folder |
|---|---|
| Python core | `src/complete.py`. No network. |
| Experiment 46 | In-process `prepare_brief` or a supplied brief. |
| Experiment 15 | In-process `scan`. No model is passed. |
| Experiment 05 | In-process `triage`, officer approval forced off. |
| Copilot Studio | Build notes. Not an imported solution. |
| Dynamics 365 | Named in the catalogue. Not connected. |
| Microsoft Foundry | Optional narrative. Not deployed. |

Closing the job, raising a charge, ordering parts, and contacting the customer are a person stepping through the organisation's own process. This starter does not do those things. A production write is disabled in the manifest.

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only by that script.
