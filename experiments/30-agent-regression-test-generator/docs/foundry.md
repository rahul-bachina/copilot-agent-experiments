# Microsoft Foundry

This generator does not create a Microsoft Foundry agent, a project, a dataset upload, or an evaluation run. No Foundry resource was created while this folder was written. A live Foundry run has not been done. `foundry_evaluation_called` stays false. No threshold is set. No pass rate is reported.

The catalogue row for G008 names Microsoft Foundry. The option below is a description of pages opened on 3 November 2026, plus a local file a maintainer could later adapt. It is not a run.

## Pages opened

| Page | What it said on 3 November 2026 | Used here |
|---|---|---|
| [Evaluate your AI agents](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent) | An agent-targeted evaluation sends each dataset query to a Foundry agent or a hosted agent. Each JSONL line is an object with a `query` field. A rubric evaluator is the recommended primary measure, with built-in evaluators layered on. The page gives an 85 percent task-adherence passing rate as an example of a threshold a team might set. Rubric generation, synthetic and trace-based dataset creation, and risk and safety evaluators have regional restrictions. The region list is on another page. | The queries file uses that `query` shape. The 85 percent figure is not a result and is not a threshold of this generator. The region page was not opened. UK region availability is unverified. |
| [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators) | Items marked preview are in preview and are not recommended for production workloads. Task Completion, Customer Satisfaction, Task Adherence, and Intent Resolution are marked preview. Task Navigation Efficiency, Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output Utilization, and Tool Call Success are not marked preview in that table. Output Quality and Tool Use Quality are marked preview. Quality Grader is described as deprecated and no longer runnable. | None of these evaluators are called. |
| [Quickstart: Evaluate your hosted agent](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent) | The Azure Developer CLI evaluation experience is currently in preview. Evaluation runs against a deployed, invokable hosted agent. The example `eval.yaml` points `dataset.local_uri` at a JSONL file and lists built-in evaluators. The page says the Foundry User role was previously named Azure AI User. | This generator does not deploy an agent and does not run that command. |

The evaluate-agent page also says the service returns pass, fail, and errored as separate counts. This starter's own smoke test uses the same idea: `passed`, `failed`, and `errored` are disjoint. That is a property of `eval/evaluate.py`, not a Foundry result.

## What the draft file is

`foundry-queries.jsonl` has one line per drafted case and no line for a skipped duplicate. Each line is `{"query": "..."}` only, because the page's item schema requires `query` and does not list other fields. Traceability stays in `foundry-trace.json`, which maps the line number to the case id, the observation id, and the requirement id. The trace file sets `called` and `uploaded` to false.

A maintainer who later runs an evaluation would still need a deployed agent, a judge deployment where the evaluator requires one, and a decision about region. Those steps are outside this generator. The human approval point is "Run a Microsoft Foundry evaluation against a deployed agent".

## Prompt Shields and other controls

Prompt Shields were not opened for this experiment. The local scan is not a shield result. Entra Agent ID, Conditional Access, Purview, Key Vault, and a Data Loss Prevention policy were not opened. They are unverified. The evaluate-agent page points at trace evaluation using Application Insights. Application Insights was not configured here, and that product page was not opened for this experiment.
