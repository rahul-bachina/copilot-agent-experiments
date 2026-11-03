# Experiment 30: Agent Regression Test Generator

Catalogue ID **G008**. Autonomy **A1**. Stack in the catalogue: Microsoft Foundry plus GitHub. This folder also ships both Copilot Studio harnesses, because every experiment in this repository does.

A starter for a maintainer who has an agent's permissions manifest, its `SKILL.md` files, its tool contract, and a set of observed failures or change notes. The generator drafts regression cases: inputs, expected behaviours, prohibited-action checks, and one prompt-injection variant per observation. The cases are files under `proposed-changes/` and the text of a pull request. The maintainer approves the tests and any pull request. The generator does not merge, does not push to any branch, and does not edit the agent under test.

The rules are the code in `src/rules.py` and `src/cases.py`. The same bundle and the same as-of date produce the same JSON. Nothing here calls a model, Git, or the network. A local call to Experiment 03, when a skeleton was requested and no manifest was supplied, is an in-process call. It is not a network call. Without PyYAML and jsonschema the call becomes a local stand-in. The stand-in still refuses approval and still refuses autonomy A3.

Halebridge Borough Council, named in the sample, is fictional. It is not a client. The housing-repairs agent in the sample is not an agent in this repository.

## The problem

A failure that was seen once, or a change note that says a description moved, is easy to lose. The next person writes a different test, or writes the same test again, or writes a test that no longer points at the failure. A generator that fingerprints each case, skips one that already exists, and stores the observation id and the requirement id on the case keeps that link. It still does not decide that the test is good enough to merge.

The draft is not a certificate. A pattern misses a paraphrase. A maintainer reads the case before it becomes a test the organisation runs.

## Who it helps

A maintainer, or an agent owner sitting with one, who wants a first set of regression files before anyone edits the agent or opens a pull request.

It does not help a team that wants the tool to merge, to push to a protected branch, or to change the agent under test.

## Non-goals

- Merging a pull request. `merged` stays false.
- Pushing to any branch, including a protected branch (`main`, `master`, `production`, `release`). `pushed` and `protected_branch_targeted` stay false.
- Editing the agent under test. `agent_under_test_edited` stays false. An output directory that resolves inside that agent's path is refused.
- Opening a pull request. `pr_opened` stays false. The markdown is content only.
- Approving the generated tests. `maintainer_approved` and `tests_applied` stay false. The maintainer decides.
- Calling Microsoft Foundry, uploading a dataset, or reporting a pass rate. `foundry_evaluation_called` stays false. No threshold is set.
- Recommending autonomy A3, approving a permissions manifest, or deploying an agent.
- Scoring trigger phrases, or assigning a routing weight. See rule R7.
- Fetching a URL supplied in the bundle. `network_called` stays false.
- Using real organisations, real people, or live failures. Fixtures are synthetic.

## What the generator does

`src/generate.py` reads one JSON bundle and writes one JSON document. The label is **DRAFT FOR MAINTAINER REVIEW**.

The rows below are the code. A test fails if a rule id in `src/rules.py` is missing here.

| Rule | What it drafts |
|---|---|
| R1 | One expected-behaviour case when an observation has an input and an expected behaviour. |
| R2 | One prompt-injection variant of that observation. The variant appends the labelled marker `SYN-MARKER-OVERRIDE`. The marker is not a procedure for attacking a live system. |
| R3 | One prohibited-action case when the observation names an action, or when the expected behaviour forbids approve, reject, close, write, update, delete, send, spend, pay, decide, merge, push, or edit. |
| R4 | One prohibited-action case for a callable tool operation whose effect is send, delete, or write and which has no structured human-approval flag. A read operation does not draft a case. |
| R5 | One prohibited-action case for each high-risk flag on a supplied manifest. A disabled flag stays disabled. An enabled flag is not performed. If the supplied level is A3, one further case says not to operate at A3. `a3_recommended` stays false. |
| R6 | A case whose fingerprint matches an existing test, or an earlier case in the same draft, is skipped. The row keeps its trace and names `duplicate_of`. No second file is written. |
| R7 | A change note marked trigger-phrase only, with no description change, drafts nothing. This generator does not assign a routing weight to a trigger phrase. |
| R8 | `foundry-queries.jsonl` has one line for each drafted case and no line for a skipped duplicate. The line is a JSON object with a `query` field, which is the shape on the evaluate-agent page opened on 3 November 2026. The file is not uploaded. |

The fingerprint is the first 16 hex characters of a SHA-256 over the kind, the input, and the expected behaviour, after stripping the ends and collapsing internal whitespace. Case is kept. Two cases that differ only by a line break in the same place are the same case.

Counts are three numbers. `drafted` plus `skipped_duplicate` equals `considered`. `observations_not_drafted` is not added to `considered`. A Foundry query line is not a second copy of a drafted case.

The sample bundle drafts 16 cases, skips 1 duplicate of `EXIST-001`, and leaves 1 observation undrafted because it is a trigger phrase only. Those figures are the deterministic draft for `examples/sample_bundle.json` on as-of date 2026-11-03. They are not a model score.

On the standard harness, generative orchestration selects a topic from the description of its purpose. Classic orchestration selects a topic by matching a user query with trigger phrases. That comparison is the table on "Orchestrate agent behavior with generative AI", opened on 3 November 2026. The page says it describes the standard harness. This generator does not implement either selector. Whether the GitHub Copilot harness uses the same rule was not on that page. That point is unverified.

Free text cannot set `maintainer_approved`, `merged`, `pushed`, `pr_opened`, `tests_applied`, `foundry_evaluation_called`, or the case list. Those keys are stripped if a caller puts them on the bundle. A sentence that forbids the action is not recorded as an instruction.

Where the bundle asks for a permissions-manifest skeleton and does not supply a manifest, the generator asks Experiment 03. `approved` on that skeleton stays false. The skeleton is not written into the agent under test. The clean install does not include PyYAML or jsonschema, so the stand-in is the usual result. It is not schema-validated.

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only.

```bash
cd experiments/30-agent-regression-test-generator
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/generate.py --bundle examples/sample_bundle.json --as-of 2026-11-03
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score. A live Microsoft Foundry run has not been done.

The smoke summary uses three disjoint counts. `passed` plus `failed` plus `errored` equals `total_cases`. A row is not both failed and errored.

A stale-data check, without editing the rules:

```bash
python src/generate.py --bundle examples/sample_bundle.json --as-of 2027-05-03 --stale-after-days 90
```

To write the proposed files somewhere that is not the agent under test:

```bash
python src/generate.py --bundle examples/sample_bundle.json --as-of 2026-11-03 --out-dir /tmp/regression-draft
```

Passing `--merge`, `--push`, `--approve`, `--apply`, or `--open-pr` is a mistake. The command exits and does not write a file.

The exit code is 0 when the JSON is produced, including when a source is stale or a case was skipped as a duplicate. That is not an approval of the tests.

## Sample

Halebridge Borough Council is fictional. The sample agent is a housing-repairs draft with sends and writes disabled, one read operation, and one send operation that has no approval gate. See `examples/sample_output.json`.

## Sources and currency

Pages opened for this experiment on **3 November 2026**. The generator does not download them at run time.

| ID | Page | Last verified |
|---|---|---|
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 3 November 2026 |
| `cs-generative-orchestration` | [Orchestrate agent behavior with generative AI](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions) | 3 November 2026 |
| `foundry-evaluate-agent` | [Evaluate your AI agents](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent) | 3 November 2026 |
| `foundry-agent-evaluators` | [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators) | 3 November 2026 |
| `foundry-hosted-eval-quickstart` | [Quickstart: Evaluate your hosted agent](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent) | 3 November 2026 |

The catalogue-boundary row is not a Microsoft page and is not stale-tested. Billing pages were not opened.

What those pages said on 3 November 2026, in short:

- The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. The harness can take a goal, break it into steps, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run in a sandbox. Agents and workflows on it use Copilot Credits. No quantity is copied. The overview does not mark the harness as preview. The standard harness follows the topics and rules the maker defines.
- The generative-orchestration page says it describes the standard harness. Generative orchestration selects topics based on the description of their purpose. Classic orchestration selects topics based on matching a user query with trigger phrases. The most important factor the page names is the description. This generator does not assign a weight.
- The evaluate-agent page describes an evaluation that sends each dataset query to a Foundry agent or a hosted agent. Each JSONL line has a `query` field. A rubric evaluator is the recommended primary measure, with other evaluators layered on. The page uses an 85 percent task-adherence passing rate as an example of a threshold a team might set. This generator does not set a threshold and does not report that figure as a result. The page says rubric generation and risk and safety evaluators have regional restrictions and points at another page. That page was not opened. UK region availability is unverified.
- The agent-evaluators page says items marked preview are in preview and are not recommended for production workloads. Task Completion, Customer Satisfaction, Task Adherence, and Intent Resolution are marked preview. Task Navigation Efficiency, Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output Utilization, and Tool Call Success are not marked preview in the table on that page. Output Quality and Tool Use Quality are marked preview. Quality Grader is described as deprecated and no longer runnable. This generator runs none of them.
- The hosted-agent quickstart says the Azure Developer CLI evaluation experience is currently in preview. Evaluation runs against a deployed, invokable hosted agent. This generator does not deploy one and does not run that command.

Prompt Shields, Entra Agent ID, Conditional Access, Purview, a Data Loss Prevention policy, and Key Vault were not opened for this experiment. They are named in the security note as unverified.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. |
| Synthetic fixtures | `examples/` and `fixtures/`. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| CI secret check | `.github/workflows/experiment-30-tests.yml`. |
| CI licence check | The same workflow. MIT, and the README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library and, for the manifest reader, Experiment 25's YAML subset reader. |

## Limitations

- The cases are drafts of inputs and expected behaviours. They do not call the agent under test. A maintainer has to wire each case to a runner they own. Residual risk R1 is High until that happens.
- A paraphrase that does not use the verbs in R3 does not become a prohibited-action case. A sentence that forbids one verb covers that verb only.
- The injection variant is one labelled sentence. It is not the attack list on any red-team page, and it is not a bypass guide.
- Dedupe is a fingerprint of kind, input, and expected behaviour. A reworded duplicate is not skipped. A whitespace-only difference is skipped.
- The generator does not read the agent under test from disk. Paths in the bundle are labels. A path that climbs out of a relative folder is refused.
- Experiment 03 is not imported on the clean install. The stand-in is not validated against `schemas/agent-manifest.schema.json`. Install PyYAML and jsonschema beside this folder if you want that validation. This requirements file does not install them.
- The supplied manifest is read for its autonomy level and its high-risk flags. It is not schema-validated by this command. This experiment's own `agent-manifest.yaml` is validated by the repository schema test when jsonschema is installed at the repository root.
- UK region availability for a later Foundry evaluation was not on a page opened for this experiment. It is unverified.
- `eval/smoke_report.json` is a deterministic smoke test. It is not a model score and it is not a Foundry pass rate.
- The 85 percent figure above is an example on Microsoft's page. It is not a result from this repository.

This is not legal advice and it is not a statement that an agent meets a test standard.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/30-agent-regression-test-generator/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── schema/
├── src/
├── skills/
├── copilot-studio/
├── docs/
├── eval/
├── examples/
├── fixtures/
└── tests/
```

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
