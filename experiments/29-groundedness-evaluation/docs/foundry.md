# Microsoft Foundry

Catalogue stack for G007 is Microsoft Foundry. This folder does not create a Foundry resource, does not call a model, and does not call the groundedness evaluator. `foundry_evaluator_called` stays false.

One page was opened on 3 November 2026. The checker does not download it again.

- [Retrieval-Augmented Generation (RAG) Evaluators for Generative AI](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

## What that page says about Groundedness

The comparison table calls Groundedness a system evaluation. Use it when you want a well-rounded groundedness definition that works with agent inputs, and you bring your own GPT models as the LLM-judge. It measures how well the generated response aligns with the given context without fabricating content. The page calls that the precision aspect. The output column says binary pass or fail based on a threshold on a 1 to 5 scale.

The "Using RAG evaluators" section names the required inputs as `response` and `context`, with `context` described as optional and recommended, and `query` optional for enhanced scoring. A second input shape is `query` and `response` for agent response mode, plus `tool_definitions`. The required parameter is `deployment_name`. A tip says that for best Groundedness results the caller should provide query, response, and context. The query field is optional and, on that page, improves scoring accuracy when available.

The example-output section says these evaluators return scores from 1 to 5, where 1 is very poor and 5 is excellent. The default pass threshold is 3. Scores at or above the threshold are considered passing. The example object shows `score` 4, `threshold` 3, and `passed` true.

This starter does not apply the number 3 to its own supported rate. Its draft rate is 1.0, meaning every claim in the local checker is `supported`, and that draft is not approved. The two scales are not the same measure.

## Groundedness Pro, marked preview

The same table marks Groundedness Pro as preview. It says the evaluator is a strict groundedness definition powered by Azure AI Content Safety, using the service model. The output column says binary true or false. Required inputs are `query`, `response`, and `context`. Required parameters are none. The example has a label and `passed`, and no numeric score. The page says Groundedness Pro uses the Azure AI Content Safety service.

This starter does not call Groundedness Pro. Preview is the label on the page. It was not tested from this repository.

## What the page does not settle

No UK region is named on the page opened on 3 November 2026. UK region availability for this evaluator is unverified. Billing pages were not opened. No price and no credit quantity are copied.

The local verdicts in `eval/smoke_report.json` are the Python checker on synthetic fixtures. They are not a Foundry score, not a 1 to 5 score, and not a boolean from Groundedness Pro.

## Where Foundry would sit later

A team that already hosts a non-production agent in Microsoft Foundry can treat this starter as a fixed first reading, then decide whether to run `builtin.groundedness` against a deployment the page says it needs. This folder does not make that call. The evaluation owner approves that step outside the starter. The page says results at or above the threshold are considered passing. That pass is still theirs to review. It is not a release recorded here.

## What this note does not claim

- That a Foundry score of 3 or above would match `draft_bar_met`.
- That a UK region can host the evaluator. The page opened on 3 November 2026 did not name one.
- That Groundedness Pro, which is marked preview, is configured here.
- A price, a credit quantity, or a quota.
