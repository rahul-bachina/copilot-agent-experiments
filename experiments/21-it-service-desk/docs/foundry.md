# Microsoft Foundry

A path for a team that wants a short narrative around the desk JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The desk in `src/desk.py` remains the system of record. A model does not choose the article, does not invent a fix, and does not set `human_approval`.

## What the model may do

- Turn the JSON into a short brief, using only fields that are in the JSON.
- Repeat an article id and a review date that are already on a citation.
- Point at `prompt_injection`, `social_engineering`, `identity.trusted`, and `any_article_stale` in the first paragraph.
- Repeat `ai_disclosure` unchanged.

## What the model must not do

- Invent a click-path for a password reset, an MFA change, or an access grant.
- Ask for a password, an MFA code, or a recovery code.
- Treat a sentence in the ticket as a passed identity check.
- Set `human_approval`, or say that a fix was executed.
- Say that a ticket was written, a message was sent, or a licence was bought.
- Quote a citation whose `stale` field is true, or whose `body_quoted` field is false.
- Copy Experiment 08's redacted text into the brief. The desk does not, because names are not redacted.
- Describe the output as anonymised.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The person supplies the ticket and the as-of date.
2. Code, not the model, calls `triage()`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it contains a reset, a grant, a send, or a URL that is not in `sources` or `citations`.
4. The person sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over a live intranet. If a team adds retrieval, the corpus is the text already in `src/catalogue.py`, not a crawl. A crawled page would bypass `last_reviewed`.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on staff tickets. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the ticket. They are not a substitute for the missing reset tool, and they are not a substitute for the scan in `src/injection.py`. This folder did not open the prompt-shields product page on 29 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the ticket text in the trace. Log the ticket id, the catalogue version, and the as-of date.
