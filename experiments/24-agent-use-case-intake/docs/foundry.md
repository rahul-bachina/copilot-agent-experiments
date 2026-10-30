# Microsoft Foundry

A path for a team that wants a short narrative beside the classification JSON. It is not a deployed project. No Foundry resource is created by this repository. This starter makes no Foundry call.

The classifier in `src/classify.py` remains the system of record. A model does not set autonomy, does not decide a DPIA, does not decide ATRS scope, and does not approve a use case.

The Microsoft Foundry Agent Service overview was not re-opened for this experiment. Product detail on that page is unverified here. Do not treat this note as a description of Foundry capabilities.

## What a model may do

- Turn the JSON into a short brief for the governance team, using only fields that are in the JSON.
- Repeat a reason and a source URL that the JSON already carries.
- Point at `prompt_injection` and `sources_stale` in the first paragraph.
- Say the label is DRAFT FOR THE GOVERNANCE TEAM.

## What a model must not do

- Invent a legislation.gov.uk URL, a GOV.UK URL, or a Microsoft Learn URL.
- Browse the web to update a pin.
- Set `suggested_autonomy` to A3, or change the suggested level.
- Set `approved`, `use_case_approved`, `provisioned`, or `governance_decision`.
- Set `dpia_required` or decide that an organisation is inside ATRS mandatory scope.
- Select a platform, or set `platform_selected`.
- Provision, deploy, or publish an agent, a flow, or a Foundry resource.
- Quote a price.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The team supplies the proposal and the as-of date.
2. Code, not the model, calls `classify`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. The completion is still a draft.
4. The governance team sees the JSON and, beside it, the narrative. The narrative does not approve the classification.

There is no retrieval over the live Learn site or over legislation.gov.uk. If a team adds retrieval, the corpus is the text already pinned in `src/sources.py` and in Experiments 03, 14, and 19, not a crawl. A crawled page would bypass the pin dates.

## Prompt shields

Microsoft Foundry prompt shields were not opened for this experiment. Whether they are on by default, and what they detect, is unverified here. The local scan in `src/injection.py` does not call them. A shield is not a substitute for the missing approve tool and the missing provision tool.

## Deployment choices to confirm

- Region: a UK region list was not opened. Unverified.
- Do not log the problem statement in a trace. Log the proposal id, the pin dates, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
