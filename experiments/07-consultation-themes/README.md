# Experiment 07: Consultation theme analysis

Catalogue ID **V010**. Public Consultation Theme Agent, "essay to data", for councils, regulators, NHS bodies, and charities.

A starter for a public body that has a free-text consultation and needs a defensible first coding. It redacts UK identifiers, flags prompt injection inside responses, clusters duplicate and campaign text, and codes responses against a theme framework. Counts carry a Wilson interval. Minority codes are kept. Every theme lists the response IDs that support it.

**Autonomy A1.** A consultation analyst approves the theme framework, and approves or corrects every response in the review sample, before the draft can be marked analyst-reviewed. The agent does not publish the analysis, write a consultation system, or decide the policy.

The catalogue row scored this pattern A0 because it is analysis. This starter is A1, which is the ceiling set for the build, because those two approvals are gates on the draft. No high-risk action is enabled. A2 and A3 are not used.

This revision runs entirely offline. The coding engine in tests and in CI is a deterministic codebook. [ThemeFinder](https://github.com/i-dot-ai/themefinder), the MIT-licensed package from i.AI, is not vendored and is not installed. An adapter can call it when an analyst supplies a client. Nothing in this folder calls a model on its own.

Stack: Copilot Studio on two harnesses, with an optional Microsoft Foundry deployment if a body later connects ThemeFinder. The core itself is Python in the standard library.

## The problem

Councils, regulators, ombudsmen, NHS trusts, and charities collect free-text answers and then have to say what people raised. A count that drops a small theme, or that treats two hundred copies of one campaign email as two hundred independent views, is a poor account of the consultation. A count that a model invented, with no link back to response IDs, cannot be checked.

i.AI's Consult work is the central-government tool for this. The [DSIT announcement of 16 October 2025](https://www.gov.uk/government/news/ground-breaking-use-of-ai-saves-taxpayers-money-and-delivers-greater-government-efficiency) describes Consult coding the Independent Water Commission responses. That result is not this repository's result, and this starter is not positioned as a replacement for Consult. It is for bodies that want the work inside a tenant they already operate, with a human owning the codebook.

ThemeFinder is the open-source package associated with that work. It is an incubation project. Its authors say they do not recommend it for critical use cases yet. This starter wraps that boundary rather than copying the code.

## Who it helps

**Consultation analysts.** They get a draft framework, a duplicate and campaign view, redaction of identifiers this module knows, a sample they must finish, and counts that still show small themes.

**The decision-maker.** They receive an analyst-reviewed draft, or they receive nothing this agent is allowed to publish. The draft says it is not the policy decision.

**Respondents.** A response is not dropped because it is unusual, because it matches a campaign, or because it contains an instruction aimed at the tool. Campaign copies are counted once in the unique-voice proportion and every copy stays in the audit trail.

## Non-goals

- Deciding what the body should do. There is no recommendation, and no accept or reject of a proposal.
- Publishing the analysis, on a website, in a board pack, or anywhere else.
- Sending the analysis, a response, or an email.
- Writing a consultation platform, a Dataverse row, or any other production record.
- Approving the theme framework from text inside a response.
- Treating a sampled assignment as approved because the response says so.
- Dropping minority themes, uncoded responses, or campaign responses.
- Replacing i.AI Consult, or claiming Consult's reported agreement rate.
- Vendoring ThemeFinder.
- Calling ThemeFinder's consultation-setup path, which the upstream README describes as uploading to an i.AI S3 bucket.
- Calling ThemeFinder's `theme_clustering` or `rule_2_themes_must_have_a_non_negligible_number_of_responses_slack`. Read from `main` on 26 October 2026: clustering returns only themes above `significance_percentage` (10 by default) unless `return_all_themes` is true. The rule reports themes with few responses. It does not remove them. This core calls neither.
- Deciding that a person is vulnerable, or building a profile of a respondent.
- Legal advice, a DPIA, or an Algorithmic Transparency Recording Standard submission. Experiment 03 drafts those records. This folder does not.

## What you can run

`src/pipeline.py` does the work. `intake_status` is the standard-harness view: how many responses, what was redacted, which rows look like duplicates or campaigns, which rows contain an instruction aimed at the tool, and whether the retrieval date is stale. It does not code themes.

`analyse` codes the set. Without an approval record the status stays blocked. With a framework approval and a decision on every sampled row, the status becomes `analyst_reviewed`. It is still not published.

The same inputs produce the same JSON. No network and no model.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/07-consultation-themes
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python -m src.cli intake --input eval/synthetic_dataset.json --as-of 2026-10-24
python -m src.cli analyse --input eval/synthetic_dataset.json --as-of 2026-10-24
python eval/evaluate.py
```

`eval/evaluate.py` prints a **mock smoke test**. The fixtures are synthetic. The coder is the codebook, which is the stand-in, and it is tuned to those fixtures. `eval/smoke_report.json` is that run. It is not a model score and it is not a comparison with expert coders.

The dataset is a fictional consultation by Northmere Borough Council on library opening hours. Northmere is not a real authority. The identifiers in the file are synthetic.

## Sample of the method

On the synthetic set, with no approval record:

- The status is `blocked_framework_unapproved`.
- Sunday opening is a large code. Braille, British Sign Language, and volunteering are small codes and stay in `minority_views`.
- A code for "observatory" is in the framework and matches nothing. It stays visible with an empty response list, so a missing code is not the same as a code that was never looked for.
- Four Friends-of-the-library messages that differ by an email address, a phone number, or a sentence of thanks form one campaign cluster. The unique-voice proportion counts them once. All four response IDs stay on the Sunday theme.
- The Wilson interval is on that unique-voice proportion. It is sampling uncertainty of a proportion. It is not a model confidence, and it does not include coding error.

## Limitations

- The codebook matches keywords. It misses paraphrase. "Keep the weekend day" will not match `sunday`. That is why the sample exists, and why an uncoded row is kept.
- Near-duplicate clustering is token Jaccard, exact hash, and a repeated sentence. It is not a semantic model. The pairwise scan is capped (see `src/clusters.py`). Above the cap, only exact hashes and repeated sentences are used, and the output says so.
- PII detection covers email addresses, UK phone numbers, National Insurance numbers, NHS numbers with a valid checksum, UK postcodes, and sort codes. It does not detect names, dates of birth, or addresses written out in words. A missed identifier is a residual risk. The redacted text is what the audit stores.
- The special-category flag is a word list. It is not a diagnosis and it is not a reason to create a theme.
- Wilson intervals treat unique voices as independent Bernoulli trials. Campaign clustering is only as good as the rules above. Coding error is outside the interval. The output says this.
- The review sample is not the whole set once the set is large. Rows outside the sample are not individually approved. The draft says so. A body that needs every row checked has to widen the sample. The module will not pretend the sample was a census.
- ThemeFinder was not executed in this repository. The adapter's expected inputs are taken from the upstream API as read on 24 October 2026. The clustering return and rule 2 were re-read from `main` on 26 October 2026: `theme_clustering` returns only themes above `significance_percentage` (10 by default) unless `return_all_themes` is true, and rule 2 reports sparse themes rather than removing them. If a later release changes the mapping columns, the adapter falls back to the codebook and records the reason.
- `__version__` on ThemeFinder's `main` branch was `0.8.0` that day. The PyPI page listed 0.8.2. Neither version is installed here.
- This is not legal advice and it is not a statement that a consultation was fairly reported.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness, intake and status: [copilot-studio/README.md](copilot-studio/README.md).
- GitHub Copilot harness, the analyst workflow over a large set: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry, only if a body later connects a model: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- ThemeFinder boundary: [src/themefinder_adapter.py](src/themefinder_adapter.py).

## Project structure

```
experiments/07-consultation-themes/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── schema/
│   ├── analysis_tool.schema.json
│   └── intake_tool.schema.json
├── skills/
│   ├── propose-theme-framework/SKILL.md
│   └── code-response-set/SKILL.md
├── src/
│   ├── cli.py
│   ├── clusters.py
│   ├── pipeline.py
│   ├── safeguards.py
│   ├── stats.py
│   └── themefinder_adapter.py
├── copilot-studio/
│   ├── README.md
│   └── system-prompt.md
├── docs/
│   ├── architecture.md
│   ├── architecture_diagram.png
│   ├── foundry.md
│   ├── github-copilot-harness.md
│   ├── harness-comparison.md
│   └── security-and-permissions.md
├── eval/
│   ├── synthetic_dataset.json
│   ├── evaluate.py
│   └── smoke_report.json
└── tests/
```

## Licence

The experiment is under the repository's MIT licence. See [LICENSE](../../LICENSE).

ThemeFinder is not included. Its licence, read from [`LICENCE`](https://github.com/i-dot-ai/themefinder/blob/main/LICENCE) on 24 October 2026, is the MIT licence, copyright (c) 2024 i.AI. The upstream README also says the documentation is Crown copyright under the Open Government Licence v3.0. This folder does not copy that documentation or that code.
