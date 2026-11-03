# Experiment 29: Groundedness Evaluation Agent

Catalogue ID **G007**. Autonomy **A0**. Stack in the catalogue: Microsoft Foundry. This folder also ships both Copilot Studio harnesses, because every experiment in this repository does.

A starter for an evaluation owner who has an agent's answers, the passages that agent was shown, and any citations, and wants a first, repeatable reading of whether each claim stays inside those passages. The checker returns a groundedness report. The evaluation owner approves thresholds and any pass or fail release. The checker does not record either decision.

The checks are the code in `src/score.py`. The same bundle and the same as-of date produce the same JSON. Nothing here calls a model or the network. This is not the Microsoft Foundry groundedness evaluator. That option is described from the page opened on 3 November 2026, and `foundry_evaluator_called` stays false.

Experiment 03 keeps a narrower G007 check inside the assurance pack: copied inventory text, and a draft 180-day review. This folder is the standalone claim checker. It does not clear that pack. Where a bundle asks for a permissions manifest and none was supplied, the checker asks Experiment 03's generator for an unapproved skeleton, through the same stand-in Experiments 26 to 28 use. That call needs PyYAML and jsonschema, which this experiment's clean install does not include. Without them, the stand-in is used. It still refuses approval and still refuses autonomy A3. It is not schema-validated until those packages are present.

The organisations in the samples are invented. Northfen Borough Council, Fenwick Mutual, and Rivertrust NHS Trust are not clients. The sentences in the passages are not quotations from a statute, a regulator, or a real policy.

## The problem

An answer can look fluent and still add a number, a date, or a sentence that was not in the passage the agent was shown. A citation can name a source that was not shown, or quote words that are not in it. A passage can be older than the window the evaluation owner is willing to trust. Reading that by eye does not stay the same from one reviewer to the next.

The figures are not a certificate that a live model is grounded, and they are not the 1 to 5 score described on the Microsoft Foundry page. A word match misses a true paraphrase, and a shared word can hide a different meaning. The evaluation owner approves the thresholds and decides any release.

## Who it helps

An evaluation owner, or a colleague sitting with one, who wants a draft before anyone treats an agent's answers as ready to show to staff or to a customer: per-claim verdicts, a separate stale-source flag, and a calculation against draft thresholds.

It does not help a team that wants the tool to approve the thresholds, to mark a release, or to call Foundry and treat that call as the decision.

## Non-goals

- Approving thresholds. `threshold_approved_by_evaluation_owner` stays false. The 180-day window and a supported rate of 1.0 are drafts.
- Recording a pass or a fail release. `release_decision` stays null. `pass_fail_released` stays false. `draft_bar_met` is a calculation, and `draft_bar_is_not_a_release` stays true.
- Calling the Microsoft Foundry groundedness evaluator or Groundedness Pro. `foundry_evaluator_called` stays false.
- Mapping this checker's rate onto Foundry's 1 to 5 scale. The page's default pass threshold of 3 is recorded as their figure. It is not applied here.
- Recommending autonomy A3, or approving, rejecting, deciding a regulated matter, changing a production record, sending, or spending.
- Approving a permissions manifest. Experiment 03's generator refuses an approve flag. The stand-in does too.
- Scoring live customer, citizen, patient, or staff text. A bundle that is not marked synthetic is refused.
- Legal advice, a clinical opinion, or a statement that a cited statute says what a synthetic passage says.
- Reading Microsoft Learn at run time. The sentences are the ones stored after the pages were opened on 3 November 2026.

## What the checker does

`src/report.py` reads one JSON bundle and writes one JSON document. The label is **DRAFT FOR EVALUATION OWNER**.

Each answer is split into claims on a full stop, a question mark, or an exclamation mark. A claim keeps the citations on the answer unless the bundle already lists claims. One claim receives one verdict. Later failures on the same claim are listed in `other_failures` and are not added to the totals. A stale cited passage sets `stale_source` on the claim. That count is `stale_claim_count`. It is not a verdict and it is not added to `verdict_total`.

| Check, in verdict order | Verdict |
|---|---|
| No citation | `citation_missing` |
| A citation names a passage that was not shown | `source_not_shown` |
| A quote is empty or is not in the cited passage, after whitespace and case are folded | `quote_not_in_source` |
| A digit in the claim is not a standalone number in the cited passage | `number_mismatch` |
| A date in the claim is not the same written form in the cited passage | `date_mismatch` |
| A content word of four letters or more, not in the stop list, is not in the cited passage | `unsupported` |
| None of those | `supported` |

`draft_bar_met` is true only when there is at least one claim, the supported rate is at least the draft `min_supported_rate`, the non-supported count is within `max_non_supported_claims`, and `stale_claim_count` is within `max_stale_claims`. The defaults are 1.0, 0, 0, and 180 days. A caller may pass other draft numbers. They are still not approved.

`do_not_rely` is true when a pinned Microsoft page is older than the pin window, default 90 days, or when any passage in the bundle is stale against the draft day window. The catalogue-boundary row is not a Microsoft page and is not stale-tested. The draft is still produced.

Free text cannot set `threshold_approved_by_evaluation_owner`, `release_decision`, `pass_fail_released`, `groundedness_clearance`, or the verdicts. Those keys are stripped if a caller puts them on the bundle. A sentence that already refuses the action is not treated as an instruction.

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only.

```bash
cd experiments/29-groundedness-evaluation
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/report.py --bundle examples/sample_bundle.json --as-of 2026-11-03
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score and it is not a Foundry score. The summary counts 23 cases once. Claim counts stay on each case and are not added into `total_cases`. On the as-of date 3 November 2026 the agreement with the labelled expectations is 100.0, which means the checker matched its own rules. It is not a measure of a live agent.

A stale-data check, without editing the scorer:

```bash
python src/report.py --bundle examples/sample_bundle.json --as-of 2027-02-15 --stale-after-days 90
```

That date leaves the sample passages inside the draft 180-day window and marks the Microsoft pins stale. `do_not_rely` is true. The three claims stay `supported`. Passing `--approve-thresholds`, `--release`, `--pass`, or `--fail` is a mistake. The command exits and does not write a file.

The exit code is 0 when the JSON is produced, including when `draft_bar_met` is false or a source is stale. That is not approval of the thresholds. The evaluation owner approves thresholds and any release.

## Sample

Northfen Borough Council is fictional. The sample is a housing-repairs leaflet with three answers. Each answer quotes a sentence that is in the leaflet. The leaflet was reviewed on 1 September 2026. On the as-of date 3 November 2026 every claim is `supported`, nothing is stale, and `draft_bar_met` is true. The release is still null. See `examples/sample_output.json`.

Further cases in `eval/synthetic_dataset.json` cover a wrong number, a wrong date, a missing citation, a quote that is not in the passage, a source that was not shown, an extra cost that the leaflet does not state, a 2024 review date, an injected instruction, a refusal sentence, stripped release keys, a fictional Fenwick Mutual complaints note, a fictional Rivertrust NHS Trust corporate leave note that is not clinical, two claims in one answer, a looser unapproved threshold, a non-synthetic refusal, a sector outside the two fixture sectors, an empty answer list, an unapproved manifest skeleton, and a refused request for autonomy A3.

The 8-week sentence in the Fenwick note is text written for this fixture. It is not a citation of the Dispute Resolution sourcebook.

## Sources and currency

| ID | Page | Last verified | Re-opened for Experiment 29 |
|---|---|---|---|
| `foundry-rag-evaluators` | [RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | 3 November 2026 | Yes |
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 3 November 2026 | Yes |
| `catalogue-boundary` | Catalogue row G007 | 3 November 2026 | No. Not a Microsoft page. Not stale-tested. |

What those pages said, as opened on 3 November 2026:

- The RAG evaluators page calls Groundedness a system evaluation. It uses the caller's own GPT model as the judge. It measures how well the generated response aligns with the given context without fabricating content, and it calls that the precision aspect. The output column says pass or fail based on a threshold on a 1 to 5 scale. The example-output section says scores run from 1 to 5, where 1 is very poor and 5 is excellent, and that the default pass threshold is 3. Scores at or above the threshold are considered passing. Required inputs named on the page are `response` and `context`, with `context` described as optional and recommended, and `query` optional. A tip says that for best results the caller provides query, response, and context. The required parameter is `deployment_name`. Groundedness Pro is marked preview. The page says it uses Azure AI Content Safety and returns a boolean rather than that numeric score. Required inputs are query, response, and context. No parameter is required. No UK region is named. UK region availability is unverified.
- The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. The harness can take a goal, break it into steps, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run in a sandbox. Agents on it use Copilot Credits. No quantity is copied. The overview does not mark the harness as preview. The standard harness follows the topics and rules the maker defines. Billing pages linked from the overview were not opened.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. The description is one line and says when to use the skill. |
| Synthetic fixtures | `fixtures/library.json`, `examples/`, and `eval/synthetic_dataset.json`. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`. Experiment 03's generator is called only for an unapproved skeleton. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret check | `.github/workflows/experiment-29-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |

## Limitations

- The checker matches words, digits, quotes, and written dates. It is not an entailment model. A true paraphrase that does not reuse the passage's words is flagged. A shared word can still hide a different meaning. Residual risk R3 is Medium.
- Numbers are digit strings. "twenty-four" is not read as 24. "1" inside "2026" is not treated as the number 1. "1.0" and "1" are different tokens.
- Dates must appear in the same written form. "1 September 2026" does not match "2026-09-01". A full stop ends a claim, so a fixture does not use "e.g." in an answer.
- One verdict is counted. `other_failures` are listed on the claim and are not added to `verdict_total`. `stale_claim_count` is separate. `answer_count` is separate. The smoke summary does not add claim counts into `total_cases`.
- A quote that is not in the passage stops the later number and date checks for that claim. The verdict is `quote_not_in_source`.
- The draft 180-day window is the same draft figure Experiment 03 uses for its narrower G007 check. The evaluation owner has not approved it here either.
- Experiment 03 is not imported on the clean install. The stand-in is not validated against the schema until PyYAML and jsonschema are installed beside this folder. This requirements file does not install them.
- UK region availability for a Foundry evaluation deployment was not on the page opened on 3 November 2026. It is unverified.
- Entra Agent ID, Conditional Access, Purview, a Data Loss Prevention policy, Key Vault, and Application Insights were not opened for this experiment. They are named in the security note as unverified.
- `eval/smoke_report.json` is a deterministic smoke test of 23 synthetic cases. Agreement 100.0 means the checker matched the expectations written for its own rules. It is not a model score.

This is not legal advice and it is not a statement that an agent's answers are fit to release.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/29-groundedness-evaluation/
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
