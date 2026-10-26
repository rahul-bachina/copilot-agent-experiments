# Microsoft Foundry

A path for a team that wants a short spoken answer beside the JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

`src/answer.py` and `src/review.py` remain the system of record. A model does not choose a clause, a review date, a refusal, or a side of a conflict.

## What the model may do

- Read the JSON aloud, using only fields that are in the JSON.
- Repeat `quote`, `policy_id`, `version`, `clause_id`, and `review_due` from a citation.
- Say "I don't know" when that is the `outcome`, and read the signpost when the outcome is `refused_clinical`.

## What the model must not do

- Invent a policy id, a version, a clause, or a review date.
- Paraphrase a clause into a new rule.
- Fill a gap when `outcome` is `i_dont_know`.
- Read a `quote` that is null. A stale withholding has no quote on purpose.
- Choose between the sources on a `conflict`.
- Set `approved_by_policy_owner`, `published`, or `accepted_by_policy_owner`.
- Answer a clinical question from any other corpus.
- Search the web, or search a SharePoint library that still contains drafts.

## Suggested shape

One orchestration, not a free chat over the intranet.

1. The caller supplies the question and the as-of date, or the owner asks for a review.
2. Code, not the model, calls `answer_question` or `review_register`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion schema rejects a policy id that is not in the JSON, and rejects a clinical recommendation.
4. The person sees the JSON and, beside it, the short reading. The reading is still not an approval.

There is no retrieval over the live intranet. If a team adds retrieval, the corpus is the approved export, already filtered by `staff_visible` and the review date. A crawl of the library would bypass the policy owner.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not trained on the organisation's policies or on staff questions. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the question. They are not a substitute for the missing publish tool, and they are not a substitute for the quarantine in `src/corpus.py`. This folder did not re-open the prompt-shields product page on 24 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the question or the clause text in the trace. Log the outcome, the policy ids, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic register. It is not a Foundry score. A live Foundry run has not been done.
