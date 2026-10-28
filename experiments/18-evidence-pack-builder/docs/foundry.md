# Microsoft Foundry

A path for a team that wants a short narrative around the pack JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The index in `src/pack.py` remains the system of record. A model does not set the hash, the page order, the scope check, the review flags, or the empty approval. Experiment 12 remains the inventory. Experiment 08 remains the identifier gateway. A model does not replace either.

## What this starter does not call

Retrieved 28 October 2026 for the harness overview only. This starter makes no network call and does not send an item to a model or to a document service.

Experiment 12's [foundry note](../../12-document-intake/docs/foundry.md) records a reading, on 27 October 2026, of Azure Document Intelligence in Foundry Tools and of the Content Understanding comparison page. This experiment does not repeat those product claims and does not call either service. A file that is not `text/plain` stays `not_read`. That is a gap, not a clean result.

Prompt shields were not re-opened for this experiment on 28 October 2026. Treat the current filter names and defaults as unverified here. Shields would not be a substitute for the missing send tool, and they would not replace `src/pack_injection.py`.

## What a model may do, if a team adds a narrative

- Turn the pack JSON into a short brief, using only fields that are already in the JSON.
- Point at `prompt_injection`, `excluded`, `held_for_review`, and `sources_stale` in the first paragraph.
- Repeat that `exemption_applied` is false and that `gateway.output_is_anonymised` is false.

## What the model must not do

- Invent a hash, a page, an entity type, or a scope.
- Set `export_approved`, `redactions_approved`, or `approver_name`.
- Apply Schedule 2 paragraph 16 or paragraph 19, or say the search was reasonable and proportionate under Article 15(1A).
- Describe the text as anonymised, or reconstruct an item body from the entity types.
- Clear a stale flag, or widen `authorised_scopes`, because an item says to.
- Send the index, or describe a pack-type label as a referral that has happened.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The user supplies the request, and types the as-of date, the pack type, the scopes, and the search period outside the items.
2. Code, not the model, calls `build_pack()`. That call includes Experiment 12 for each in-scope item, and Experiment 12 calls Experiment 08. `apply_model_suggestions` stays false. `reversible` is not requested. This experiment does not call `release`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it approves the export, claims an exemption was applied, claims anonymisation, or names a send.
4. The person sees the JSON and, beside it, the narrative. The narrative is still a draft. An evidence pack approver records the exact list outside the agent.

There is no retrieval over a mailbox or a case store. If a team adds retrieval, the corpus is the closed lists in `src/sources.py`, not a crawl. A crawled page would bypass `sources_pinned_on`.

## Deployment choices to confirm

- Region: UK South or UK West, if a model is used at all.
- The deployment is not trained on the caller's files. Confirm the data-use terms at the time.
- Do not log the item body or the raw identifiers in the trace. Log the request id, the in-scope hashes, the scope list, the search period, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
