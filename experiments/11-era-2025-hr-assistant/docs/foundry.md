# Microsoft Foundry

A path for a team that wants a short narrative around the review JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The checklist in `src/review.py` remains the system of record. A model does not decide which section is in force, does not decide that the employer complied, and does not add a citation.

## What the model may do

- Turn the JSON into a short brief for the HR lead, using only fields that are in the JSON.
- Repeat a provision and a URL that are already on the result.
- Point at `prompt_injection`, `any_source_stale`, and `policy_currency.policy_evidence_stale` in the first paragraph.

## What the model must not do

- Invent a legislation.gov.uk URL, an Acas step, or a commencement date.
- Browse the web to update the catalogue.
- Set `hr_decision`, `compliance_conclusion`, or `disciplinary_decision`.
- Say the employer took all reasonable steps, or that a missing prompt is a breach.
- Treat Acas examples as regulations under Equality Act 2010 section 40B.
- Count a tribunal time limit, or apply the six-month qualifying period to a person.
- Draft a warning, a suspension, or a dismissal.
- Contact a worker or Acas, or tell the HR lead that the agent has done so.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The HR lead supplies the pack and the as-of date.
2. Code, not the model, calls `review()`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it contains a compliance conclusion, a disciplinary outcome, or a URL that is not in `sources_and_currency`.
4. The HR lead sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over the live Acas site, GOV.UK, or legislation.gov.uk. If a team adds retrieval, the corpus is the text already pinned in `src/sources.py`, not a crawl. A crawled page would bypass the last-verified date.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on the employer's reports. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the pack. They are not a substitute for the missing decision tool, and they are not a substitute for the scan in `src/injection.py`. This folder did not re-open the prompt-shields product page on 27 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the incident narrative in the trace. Log the pack reference, the catalogue version, and the as-of date.
