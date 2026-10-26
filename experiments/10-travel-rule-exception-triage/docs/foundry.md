# Microsoft Foundry

A path for a team that wants a short narrative around the triage JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The checklist in `src/triage.py` remains the system of record. A model does not decide which field is missing, does not apply the £800 limb, and does not add a citation.

## What the model may do

- Turn the JSON into a short brief for the analyst, using only fields that are in the JSON.
- Repeat a provision and a URL that are already on the result.
- Point at `prompt_injection`, `any_source_stale`, and `sunrise.relied_on` in the first paragraph.

## What the model must not do

- Invent a legislation.gov.uk URL, a JMLSG paragraph, or a threshold.
- Browse the web to update the catalogue.
- Set `analyst_decision`, or describe the transfer as held, returned, or released.
- Treat the FCA statement as a waiver of regulation 64D.
- Use 1,000 euros as the operative threshold.
- Draft or file a suspicious activity report.
- Contact a counterparty, or tell the analyst that the agent has done so.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The analyst supplies the record and the as-of date.
2. Code, not the model, calls `triage()`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it contains a decision, a release, or a URL that is not in `sources_and_currency`.
4. The analyst sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over the live FCA site or legislation.gov.uk. If a team adds retrieval, the corpus is the text already pinned in `src/sources.py`, not a crawl. A crawled page would bypass the last-verified date.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on the firm's transfers. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the record. They are not a substitute for the missing release tool, and they are not a substitute for the scan in `src/injection.py`. This folder did not re-open the prompt-shields product page on 26 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the transfer in the trace. Log the transfer id, the catalogue version, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
