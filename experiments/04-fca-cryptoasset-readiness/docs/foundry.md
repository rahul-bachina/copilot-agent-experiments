# Microsoft Foundry

A path for a team that wants a short narrative around the register. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The checker in `src/gap_register.py` remains the system of record. A model does not calculate currency, does not choose rule stage, and does not add a citation.

## What the model may do

- Turn the JSON into a short brief for the Compliance Officer or MLRO, using only fields that are in the JSON.
- Repeat `page_says` and the source URL from the row.
- Point at `prompt_injection` and `any_source_stale` in the first paragraph.

## What the model must not do

- Invent an FCA URL, a Handbook paragraph, or a source id.
- Browse the web to update the catalogue.
- State a readiness finding, or give regulatory or legal advice.
- Accept a gap, or change `accepted_as_gap`.
- Treat `consultation` or `planned_consultation` as a final rule.
- Submit, send, file, or write a production record.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The reviewer supplies the pack and the as-of date.
2. Code, not the model, calls `build_register`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion schema rejects a response that contains a readiness finding or a URL that is not in `sources_and_currency`.
4. The reviewer sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over the live FCA site. If a team adds retrieval, the corpus is the text already pinned in `src/sources.py`, not a crawl. A crawled page would bypass the last-verified date.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on the firm's policies. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the pack. They are not a substitute for the missing submit tool, and they are not a substitute for the injection scan in `src/injection.py`. This folder did not re-open the prompt-shields product page on 24 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the pack in the trace. Log the document ids, the catalogue version, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
