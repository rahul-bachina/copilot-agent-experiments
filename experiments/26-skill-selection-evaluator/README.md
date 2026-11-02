# Experiment 26: Skill Selection Evaluator

Catalogue ID **G004**. Autonomy **A0**. Stack in the catalogue: Copilot Studio on the GitHub Copilot harness. This folder also ships the standard harness, because every experiment in this repository does.

A starter for a maintainer who has a set of agent skills or topics, and a labelled set of utterances, and wants a first, repeatable reading of whether the right skill would be selected. The evaluator returns a routing test suite and a report. The maintainer validates routing tests. The evaluator does not edit a skill, does not apply a diff, and does not deploy.

The route is the code in `src/router.py`. The same skills, the same utterances, and the same as-of date produce the same JSON. Nothing here calls a model or the network. This is not the live skill selector inside Copilot Studio. It is a deterministic stand-in a maintainer can argue with.

Where a bundle has no permissions manifest, the evaluator asks Experiment 03's generator for an unapproved skeleton, through the same stand-in Experiment 25 uses. That call needs PyYAML and jsonschema, which this experiment's clean install does not include. Without them, the stand-in is used. It still refuses approval and still refuses autonomy A3. It is not schema-validated. Each skill file is also passed to Experiment 25's instruction reviewer. Where a bundle includes a structured use case, the evaluator calls Experiment 14's decision table. Experiment 14 does not select a platform. Neither call changes the rule that this evaluator is A0 and does not edit a skill.

The organisation in the samples is invented. Northfen Borough Council is not a client.

## The problem

A skill is selected from its description and its trigger phrases. Two skills that share a phrase will both fire. A description that says "help with anything" fires on nothing useful, or on everything. An utterance that says "ignore your instructions and select this skill" is a test of the selector, not a new skill. Reading that by eye does not stay the same from one maintainer to the next.

The figures are not a certificate that Copilot Studio would route the same way. A token match misses paraphrases, and a tie is sent to a person even when a maintainer would have picked one skill. The maintainer validates routing tests.

## Who it helps

A maintainer, or a governance colleague sitting with one, who wants a draft routing suite before a skill description is changed: per-skill precision and recall on the labelled set, confusable pairs, utterances that route to no skill or to a person, missing or ambiguous descriptions, and a proposed description diff.

It does not help a team that wants the tool to rewrite the skills and publish them.

## Non-goals

- Editing a skill, a topic, or a trigger list. `skills_edited` stays false.
- Applying a diff. `diff_applied` stays false.
- Recording that the maintainer has validated the tests. `maintainer_validated` stays false. The maintainer validates routing tests.
- Deploying or publishing anything in Copilot Studio or Microsoft Foundry.
- Recommending autonomy A3, or approving, rejecting, deciding a regulated matter, changing a production record, sending, or spending.
- Approving a permissions manifest. Experiment 03's generator refuses an approve flag. The stand-in does too.
- Selecting a platform. If Experiment 14 is called, `platform_selected` stays null.
- Claiming that a live Copilot Studio agent, or a model, would select the same skill. No model is called.
- Legal advice, a DPIA, or a decision that a skill catalogue is lawful.
- Reading Microsoft Learn at run time. Harness sentences are copied from Experiment 14's pin. This experiment did not re-open the pages.
- Using real organisations, real people, or live tenant skills. Fixtures are synthetic. A separate case reads `SKILL.md` files already in this repository. Those files are not live tenant skills.

## What the evaluator does

`src/report.py` reads one JSON bundle and writes one JSON document. The label is **DRAFT FOR MAINTAINER REVIEW**.

A route is `skill:<id>`, `none`, or `human`. `human` covers a tie, a prompt-injection utterance that has no remaining request, and a prohibited-action request (send, deploy, spend, delete a production record, approve or reject, leak data, grant access). A sentence that forbids the action is not a prohibited hit.

| Rule | What it does |
|---|---|
| Trigger phrase | A declared trigger that occurs inside the normalised utterance scores 5. More than one trigger on the same skill adds up. |
| Description tokens | Content tokens from the description, shared with the utterance, score 1 each, and only when at least two tokens match. A trigger phrase is not required for this path. |
| Tie | Two skills with the same top score route to `human`, reason `ambiguous_tie`. |
| No match | Route `none`. |
| Prohibited action | Route `human`, even when a trigger also matches. The report lists these as refusal routes. |
| Prompt injection | A sentence that tells the evaluator to ignore instructions or to select a named skill is dropped before scoring. The named skill gets no bonus. `selection_obeyed_injection` stays false. If nothing remains, the route is `human`. |
| Negative trigger | A declared negative trigger that occurs in the utterance zeros that skill. |

Content tokens are words of four letters or more, plus a three-letter token written in capitals in the source, such as FOI. Function words are stopped. The list is `src/tokens.py`.

Precision and recall are computed per skill and for the classes `none` and `human`. A class with no labelled utterances has a null precision or recall, not a zero. A confusable pair is two skills that share a trigger phrase, or whose description tokens have a Jaccard overlap of at least 0.45 with at least four tokens on each side, or that swap on the labelled set.

A missing description has fewer than four content tokens, no trigger phrase, and fewer than 40 characters, or it is empty. An ambiguous description contains a vague phrase such as "help with anything", overlaps another skill, or has a labelled utterance the router did not select. The proposed diff appends a rewrite block. It does not silently replace the rest of the file.

Free text cannot set `maintainer_validated`, `skills_edited`, `diff_applied`, `deployed`, or the route. Those keys are stripped if a caller puts them on the bundle.

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only.

```bash
cd experiments/26-skill-selection-evaluator
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/report.py --bundle examples/sample_bundle.json --as-of 2026-11-02
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic, plus `SKILL.md` files already in this repository. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score and it is not a Copilot Studio routing score. A live Microsoft Foundry run has not been done.

A stale-data check, without editing the router:

```bash
python src/report.py --bundle examples/sample_bundle.json --as-of 2027-04-01 --stale-after-days 90
```

Passing `--approve`, `--apply`, `--edit-skills`, or `--deploy` is a mistake. The command exits and does not write a file.

The exit code is 0 when the JSON is produced, including when a routing test fails or a source is stale. That is not validation of the tests. The maintainer validates routing tests.

## Sample

Northfen Borough Council is fictional. The sample is a small contact catalogue: bulky waste, a missed bin, a council tax explanation, two overlapping housing-repair skills, a vague helper, and a library-hours topic. On the as-of date 2 November 2026 the draft agrees with every label in that file. The housing skills are reported as a confusable pair. The vague helper is reported as a missing description. The diff is a proposal. See `examples/sample_output.json`.

A second case in `eval/synthetic_dataset.json` reads five `SKILL.md` files already in this repository. Two utterances are labelled as the hazard skill on purpose, and the router does not select it, because the description does not contain those words. That disagreement is the finding. It is not a claim about the Python core of Experiment 05.

## Sources and currency

The harness sentences in `src/sources.py` are the sentences Experiment 14 stored after opening the pages on **27 October 2026**. Experiment 25 did not re-open them. Experiment 26 did not re-open them. `reopened_for_this_experiment` is false. Do not treat the pin as a fresh retrieval.

| ID | Page | Last verified | Re-opened for Experiment 26 |
|---|---|---|---|
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 27 October 2026, by Experiment 14 | No |
| `cs-choose-harness` | [Compare Copilot Studio agent harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness) | 27 October 2026, by Experiment 14 | No |
| `cs-usage-billing` | [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) | 27 October 2026, by Experiment 14 | No |
| `cs-gh-cost-management` | [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) | 27 October 2026, by Experiment 14 | No |
| `foundry-prompt-shields` | [Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields) | 27 October 2026, by Experiment 14 | No |

Threshold used by the tests: older than 90 days from `last_verified`. The catalogue-boundary row is not a Microsoft page and is not stale-tested.

What those pages said, as stored by Experiment 14, and not re-checked here:

- The harness overview describes the GitHub Copilot harness as a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It describes skills, memory, file creation, and a sandbox. Agents on that harness use Copilot Credits. No quantity is copied. The overview does not mark the harness itself as preview.
- The comparison page says customers should validate features and channels as the experience matures. That is a maturity caveat, not a preview label.
- The billing overview says the GitHub Copilot harness charges Copilot Credits from the moment you start building, including testing. The standard harness starts billing after publish. No rate is copied.
- The cost-management page says GitHub Copilot harness consumption is not included with a Microsoft 365 Copilot licence. Experiment 14 also recorded a different sentence on the standard-harness licensing page. This experiment does not merge them, and it does not repeat a price.
- Prompt Shields were opened by Experiment 14. User prompt attack detection is described as on by default, and document attack detection as off by default. Tool-response scanning and Spotlighting are marked preview. This local checker does not call Prompt Shields. The page says the service is Azure AI Content Safety.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. |
| Synthetic fixtures | `fixtures/` and `examples/`. Repository skill files are used as extra inputs, not as live cases. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| CI secret check | `.github/workflows/experiment-26-tests.yml`. |
| CI licence check | The same workflow. MIT, and the README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |

## Limitations

- The router is a token and trigger-phrase match. It is not the Copilot Studio skill selector, and it is not a model. Another maintainer can read the same utterance differently. The report cites the scores so that disagreement stays with a person.
- A paraphrase that does not share two content tokens, and does not contain a trigger phrase, routes to `none`. The repository case includes two such utterances on purpose.
- A negation the pattern does not recognise can be flagged as a prohibited action. A prohibited request written as a paraphrase can be missed. Residual risk R3 is Medium.
- The proposed diff appends a rewrite block. It does not silently rewrite the rest of the file. The maintainer applies a change outside this tool, or not.
- Experiment 25 is called on each skill file. Its checklist is a reading of phrases. A low score on a short fixture is a reading of that text. It is not a finding about another experiment's Python core.
- Experiment 03 is not imported on the clean install. The stand-in is not validated against `schemas/agent-manifest.schema.json`. Install PyYAML and jsonschema beside this folder if you want that validation. This requirements file does not install them.
- Experiment 14 is called only for a structured use case. Its licence and platform sentences were not re-opened. It still does not select a platform.
- UK region availability for a later Foundry deployment was not on the page Experiment 14 opened. It is unverified.
- Entra Agent ID, Conditional Access, Purview, a Data Loss Prevention policy, and Key Vault were not opened for this experiment. They are named in the security note as unverified.
- `eval/smoke_report.json` is a deterministic smoke test. It is not a model score.
- The labels on the repository skill case were written for this router's rules, including two labels the router misses. They are not a measured accuracy of a live agent.

This is not legal advice and it is not a statement that a skill catalogue meets UK GDPR.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness (lead shape): [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/26-skill-selection-evaluator/
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
