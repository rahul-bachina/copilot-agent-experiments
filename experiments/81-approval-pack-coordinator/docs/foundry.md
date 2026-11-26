# Microsoft Foundry

Say Microsoft Foundry. The retired product name is not used.

Foundry is optional. If a team wants a short prose note beside the JSON, a Foundry model may paraphrase fields that are already on the draft: the outcome, the missing list, the stale list, and the named approver references. It must not choose an approver, choose between conflicting values, or set `human_approval`.

The Python core does not call a model. `model_called` is not a field because no model path exists in `assemble_pack`. The hash, the flags, and the decision stay in `src/coordinator.py`.

Prompt shields, Key Vault, and a UK region for a deployment were not opened on 26 November 2026. Treat that product behaviour as unverified. This repository does not deploy a Foundry resource.

A note that disagrees with the JSON is a defect in the note. The approver relies on the JSON and the held hash, not on the prose.
