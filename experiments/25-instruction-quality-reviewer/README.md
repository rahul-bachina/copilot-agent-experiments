# Experiment 25: Instruction Quality Reviewer

Catalogue ID **G003**. Autonomy **A0**. Stack in the catalogue: Copilot Studio on the GitHub Copilot harness. This folder also ships the standard harness, because every experiment in this repository does.

A starter for an agent owner who has a system prompt, a `SKILL.md`, or a topic prompt and wants a first, repeatable reading of it. The reviewer scores the text against a fixed checklist and returns a findings report with a proposed diff. The agent owner approves any prompt change. The reviewer does not edit the file, does not apply the diff, and does not deploy.

The checklist is the code in `src/checklist.py`. The same text and the same as-of date produce the same JSON. Nothing here calls a model or the network.

Where a bundle has no permissions manifest, the reviewer asks Experiment 03's generator for an unapproved skeleton. That call needs PyYAML and jsonschema, which this experiment's clean install does not include. Without them, a local stand-in is used. It still refuses approval and still refuses autonomy A3. It is not schema-validated. Where a bundle includes a structured use case, the reviewer calls Experiment 14's decision table for a cross-check. Experiment 14 does not select a platform. Neither call changes the rule that this reviewer is A0 and does not apply a diff.

The organisations in the samples are invented. They are not clients.

## The problem

Instructions are where an agent is told what it may do. A prompt can omit the non-goals, tell the agent to send or to deploy, stay silent on prompt injection, or disagree with the permissions manifest. Reading that by eye does not stay the same from one reviewer to the next. A checklist that cites the line it used is easier to argue with.

The score is not a certificate. A pattern misses paraphrases, and it can flag a line a person would keep. The owner accepts or rejects each finding.

## Who it helps

An agent owner, or a governance colleague sitting with one, who wants a draft reading before a prompt is changed: scope and non-goals, a named human approval, refusal and escalation, prohibited actions, prompt-injection guidance, grounding, UK GDPR cautions, least privilege against the manifest, and conflicts or vague lines.

It does not help a team that wants the tool to rewrite the prompt and publish it.

## Non-goals

- Editing instructions, applying a diff, or opening a pull request. `diff_applied` stays false.
- Approving a rewrite. `owner_approved` stays false. The agent owner decides.
- Deploying or publishing anything in Copilot Studio or Microsoft Foundry.
- Recommending autonomy A3, or approving, rejecting, deciding a regulated matter, changing a production record, sending, or spending.
- Approving a permissions manifest. Experiment 03's generator refuses an approve flag. The stand-in does too.
- Selecting a platform. If Experiment 14 is called, `platform_selected` stays null.
- Legal advice, a DPIA, or a decision that a prompt is lawful.
- Reading Microsoft Learn at run time. Harness sentences are copied from Experiment 14's pin. This experiment did not re-open the pages.
- Using real organisations, real people, or live prompts. Fixtures are synthetic. A few cases read instruction files already in this repository. Those files are not live tenant prompts.

## What the reviewer does

`src/review.py` reads one JSON bundle and writes one JSON document. The label is **DRAFT FOR AGENT OWNER REVIEW**.

Each check scores 0, 1, or 2. A pass is 2, a partial is 1, a fail is 0. The maximum is 18. The percent is `points / 18`, rounded to one decimal place. A fail is blocking: the report still shows the score, and it still does not apply the diff. The rows below are the code. A test fails if a check id in the code is missing here.

| Check | Name | What a pass needs | What a fail is |
|---|---|---|---|
| C1 | Clear scope and non-goals | A bounded scope and an explicit non-goal. | No scope and no non-goal, or an unbounded "help with anything" and no non-goal. A partial is one of the two, or an unbounded line beside a non-goal. |
| C2 | Explicit human approval points | A named human role and an approval or confirmation. | No approval language. A partial names a person and does not say they approve. |
| C3 | Refusal and escalation rules | A refusal and an escalation to a role. | Neither. A partial is a refusal with no escalation route. |
| C4 | No instructions to take prohibited actions | No instruction that tells the agent to send, deploy, write a production record, spend, approve or reject as the agent, decide a regulated matter, set autonomy A3, or apply a diff. A line that forbids the action is not a hit. A human role as the subject of "approves" is a checkpoint, not a hit. | One or more of those instructions, with the line cited. |
| C5 | Prompt-injection resistance guidance | The text is treated as untrusted, and an instruction inside it is not followed. | No such guidance, or a line that says to follow instructions found in the document. |
| C6 | Grounding and citation rules | Quote, cite, or refuse to invent, and do not fill a gap from general knowledge. | No grounding rule, or an instruction to fill gaps from general knowledge. A partial is a "be accurate" line with no citation rule. |
| C7 | Data-handling and UK GDPR cautions | A UK GDPR or personal-data caution: do not copy, do not retain, do not ask for special-category data, or a DPO confirms the basis. | No data-handling language, or an instruction to collect special-category data. A partial mentions personal data and gives no caution. |
| C8 | Tool least-privilege consistency with the permissions manifest | Tools the instructions authorise are in the manifest, and a high-risk switch (writes, sends) is not enabled in the manifest while the instructions forbid it, or the reverse. | No manifest, a tool the manifest does not list, or the two documents disagree on writes or sends. |
| C9 | Conflicting or vague instructions | No vague control phrase and no pair of lines that command and forbid the same action. | "Use your judgement", "as appropriate", "if it seems right", "do whatever", or a command and a forbid for the same action. |

Free text cannot set `owner_approved`, `diff_applied`, `deployed`, or the score. Those keys are stripped if a caller puts them on the bundle.

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only.

```bash
cd experiments/25-instruction-quality-reviewer
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/review.py --bundle examples/sample_bundle.json --as-of 2026-10-30
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic, plus instruction files already in this repository. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score. A live Microsoft Foundry run has not been done.

A stale-data check, without editing the checklist:

```bash
python src/review.py --bundle examples/sample_bundle.json --as-of 2027-04-01 --stale-after-days 90
```

Passing `--approve` or `--apply` is a mistake. The command exits and does not write a file.

The exit code is 0 when the JSON is produced, including when a check fails or a source is stale. That is not an approval of the prompt.

## Sample

Halebridge Borough Council is fictional. The sample is a bounded policy explainer. The draft scores the checklist and selects nothing. The diff, if any finding is not a pass, is a proposal. See `examples/sample_output.json`.

## Sources and currency

The harness sentences in `src/sources.py` are the sentences Experiment 14 stored after opening the pages on **27 October 2026**. Experiment 25 did not re-open them. `reopened_for_this_experiment` is false. Do not treat the pin as a fresh retrieval.

| ID | Page | Last verified | Re-opened for Experiment 25 |
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
- Prompt Shields were opened by Experiment 14. User prompt attack detection is described as on by default, and document attack detection as off by default. Tool-response scanning and Spotlighting are marked preview. This local checker does not call Prompt Shields.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. |
| Synthetic fixtures | `fixtures/` and `examples/`. Repository instruction files are used as extra inputs, not as live cases. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| CI secret check | `.github/workflows/experiment-25-tests.yml`. |
| CI licence check | The same workflow. MIT, and the README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |

## Limitations

- The checks are string patterns. Another owner can read the same line differently. The report cites the line so that disagreement stays with a person.
- A negation the pattern does not recognise can be flagged as a command. A command written as a paraphrase can be missed. Residual risk R3 is Medium.
- The proposed diff appends a rewrite block. It does not silently rewrite the rest of the file. The owner applies a change outside this tool, or not.
- The stdlib YAML reader accepts the subset this repository's manifests use. A file it cannot parse is reported. It is not guessed into a pass.
- Experiment 03 is not imported on the clean install. The stand-in is not validated against `schemas/agent-manifest.schema.json`. Install PyYAML and jsonschema beside this folder if you want that validation. This requirements file does not install them.
- Experiment 14 is called only for a structured use case. Its licence and platform sentences were not re-opened. It still does not select a platform.
- UK region availability for a later Foundry deployment was not on the page Experiment 14 opened. It is unverified.
- Entra Agent ID, Conditional Access, Purview, a Data Loss Prevention policy, and Key Vault were not opened for this experiment. They are named in the security note as unverified.
- `eval/smoke_report.json` is a deterministic smoke test. It is not a model score.
- A finding on another experiment's system prompt is a finding about that text. It is not a finding about that experiment's Python core.

This is not legal advice and it is not a statement that a prompt meets UK GDPR.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness (lead shape): [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/25-instruction-quality-reviewer/
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
