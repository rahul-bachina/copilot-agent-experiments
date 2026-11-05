# Microsoft Foundry

The catalogue names document handling and an LLM-as-a-judge beside this row. This folder does not create a Foundry resource, does not call a model, and does not call an evaluator. `foundry_evaluator_called` stays false. `llm_as_judge` stays false.

One page was opened on 5 November 2026.

- [Retrieval-Augmented Generation (RAG) Evaluators for Generative AI](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

## What that page says

The comparison table calls Groundedness a system evaluation. Use it when you want a well-rounded groundedness definition that works with agent inputs, and you bring your own GPT models as the LLM-judge. It measures how well the generated response aligns with the given context without fabricating content. The page calls that the precision aspect. The output column says binary pass or fail based on a threshold on a 1 to 5 scale.

The page says these evaluators return scores from 1 to 5, where 1 is very poor and 5 is excellent. The default pass threshold is 3. Scores at or above the threshold are considered passing.

Groundedness Pro is marked preview. It uses the Azure AI Content Safety service and returns a boolean. Response Completeness is also marked preview. It measures recall against a ground truth.

This starter does not apply the number 3, and it does not call Groundedness, Groundedness Pro, or Response Completeness. Its draft bar is 1.0 on the local checker: every quoted line supported, every applicable checklist row met, and no unsupported coverage phrase. That draft is not approved. The two scales are not the same measure.

Document Intelligence is a Foundry Tool that could read a scan. It was not called. A file this starter cannot read stays `not_read`, which is a gap, not a clean result. The product page for Document Intelligence was not opened on 5 November 2026. Anything about regions, preview status, or price would be unverified.

## What the page does not settle

No UK region is named on the page opened on 5 November 2026. UK region availability for this evaluator is unverified. Billing pages were not opened. No price and no credit quantity are copied.

The local verdicts in `eval/smoke_report.json` are the Python checker on synthetic fixtures. They are not a Foundry score, not a 1 to 5 score, and not the LLM-as-a-judge in FCA case study K. That case study combined staff checks with an automated assessment. This checker is the deterministic half of that shape. The staff half is the handler.

## Where Foundry would sit later

A team that already hosts a non-production agent in Microsoft Foundry can treat this starter as a fixed first reading, then decide whether to run `builtin.groundedness` against a deployment the page says it needs. This folder does not make that call. The evaluation owner approves that step outside the starter. A pass on the page's scale is still theirs to review. It is not a decline, and it is not a release recorded here.

Prompt Shields were not opened for this experiment. Anything this folder might say about defaults or preview status would be unverified. The local phrase list is not a shield result.

## What this note does not claim

- That a Foundry score of 3 or above would match `below_threshold` being false.
- That a UK region can host the evaluator. The page opened on 5 November 2026 did not name one.
- That Groundedness Pro or Response Completeness, which are marked preview, is configured here.
- A price, a credit quantity, or a quota.
- That this checker is an LLM-as-a-judge.
