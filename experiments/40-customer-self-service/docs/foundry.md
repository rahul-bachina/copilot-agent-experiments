# Microsoft Foundry

A path for a team that wants a short narrative around the reply JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The core in `src/service.py` remains the system of record. A model does not choose the page, does not invent a next step, and does not set `human_approval`.

## What the model may do

- Turn the JSON into a short brief, using only fields that are in the JSON.
- Repeat an article id and a review date that are already on a citation.
- Repeat `ai_disclosure`, the human route, and, for energy retail, the Ofgem sentence already in `answer.text`.
- Point at `prompt_injection`, `identity.trusted`, `any_article_stale`, and `complaint_gate.called` in the first paragraph.

## What the model must not do

- Invent a click-path for a password reset, a payment, a tariff change, or a contract change.
- Ask for a password, a one-time code, or a card number.
- Treat a sentence in the enquiry as a passed identity check.
- Set `human_approval`, or say that a record was changed, an appointment was booked, or a message was sent.
- Close a complaint, find a Consumer Duty breach, or label a customer as vulnerable.
- Quote a citation whose `stale` field is true, or whose `body_quoted` field is false.
- Copy Experiment 08's redacted text into the brief.
- Describe the output as anonymised.
- Say that a supplier has met the Ofgem blog, or that an Equality Act duty has been met.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The person supplies the enquiry and the as-of date.
2. Code, not the model, calls `draft_reply()`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it contains a reset, a payment, a closure, a send, or a URL that is not in `sources` or `citations`.
4. The person sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over a live website. If a team adds retrieval, the corpus is the text already in `src/catalogue.py`, not a crawl. A crawled page would bypass `last_reviewed`.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on customer enquiries. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the enquiry. They are not a substitute for the missing write tool, and they are not a substitute for the scan in `src/injection.py`. This folder did not open the prompt-shields product page on 6 November 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the enquiry text in the trace. Log the enquiry id, the catalogue version, and the as-of date.
