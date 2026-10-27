# Microsoft Foundry

A path for a team that wants a short narrative around the front-door JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The front door in `src/front_door.py` remains the system of record. A model does not choose the page, does not invent a bin day, and does not add a citation.

## What the model may do

- Turn the JSON into a short brief for the adviser, using only fields that are in the JSON.
- Repeat a page title and a URL that are already on a citation.
- Point at `prompt_injection`, `any_article_stale`, and `flags.emergency` in the first paragraph.
- Repeat `ai_disclosure` unchanged.

## What the model must not do

- Invent a council URL, a ward, a tariff, or an opening time.
- Browse the web to update the catalogue.
- Set `human_approval`, or describe the resident as eligible, housed, or awarded a reduction.
- Say that a message was sent, a case was opened, or a payment was taken.
- Quote a citation whose `stale` field is true.
- Add medical, legal, or safeguarding advice to the fixed handover script.
- Call 999, or say that the agent has called 999.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The adviser supplies the enquiry and the as-of date.
2. Code, not the model, calls `triage()`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it contains an eligibility decision, a send, or a URL that is not in `sources_and_currency` or `citations`.
4. The adviser sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over a live council site. If a team adds retrieval, the corpus is the text already in `src/catalogue.py`, not a crawl. A crawled page would bypass `last_reviewed`.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on residents' enquiries. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the enquiry. They are not a substitute for the missing send tool, and they are not a substitute for the scan in `src/injection.py`. This folder did not open the prompt-shields product page on 27 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the enquiry in the trace. Log the enquiry id, the catalogue version, and the as-of date.

Northmarsh Borough Council is invented. Do not point a Foundry index at a real council's pages for a run of these fixtures.
