# Experiment 75: Benefits Information Assistant

Catalogue ID **V009**. Autonomy **A0**. The assistant answers a general question about what a benefit is, how to apply, what evidence is usually needed, and where to get independent advice. It quotes a pinned synthetic page, the publisher, and the last-reviewed date. It does not decide eligibility, estimate an entitlement, calculate an award, complete or submit a claim, or send. A human adviser route is always offered. The named resident approves the exact summary before a copy is written to a synthetic staging store.

Northmarsh Borough Council is fictional. The same invented council is used by [Experiment 13](../13-council-contact-front-door/). The pages are not GOV.UK pages and they are not Department for Work and Pensions pages. No figure in the fixtures is a current rate or threshold.

## Problem

A resident can ask a general question and receive an answer that sounds like a decision. "Will I get it?" and "How much will I get?" are decisions about that person. A pasted rate, a stale page, or a sentence that says the summary is already approved must not become the answer. Distress, debt, eviction, domestic abuse, and safeguarding need a person, including when the resident paraphrases.

## Who it helps

A resident who wants the published description, the application route, the usual evidence, or where to ask for independent advice. A benefits adviser who receives a summary only after the resident has approved that exact text. The organisation gets a refusal, a citation, and an urgent route that does not decide the claim.

## What it does

It reads the pinned pages and the synthetic directory. It quotes a page only when the date the question is about is before that page's review-due date. On the review-due date the page is stale. That is a starter rule, not a statute. It cites the URL, the publisher, and the last-reviewed date.

It calls [Experiment 13](../13-council-contact-front-door/) so the contact route is recorded. The front-door reply is not the benefits answer. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) to count UK identifiers. The redacted text is not copied, and the output is not described as anonymised. Phone numbers, email addresses, dates of birth, postal addresses, personal names, amounts, and national insurance numbers are masked in the summary.

UK GDPR Article 22, Articles 22A to 22D, Data (Use and Access) Act 2025 sections 80 and 142, S.I. 2026/82 regulation 2(j), and Equality Act 2010 sections 20 and 149 are quoted from the pages opened on 24 November 2026. The quotes are context. They are not a finding that a duty was met. Regulation 5 of S.I. 2026/82 was not quoted.

## Non-goals

- Deciding whether a person will get a benefit, including a paraphrase of "will I get it".
- Estimating an entitlement or calculating an award, including "how much will I get".
- Completing, filling in, or submitting a claim.
- Sending anything, including the summary.
- Treating a caller-supplied page, rule, or rate as the pinned knowledge base.
- Treating an approval sentence inside the question as the approval step.
- Answering from a page that is past its review date.
- Publishing a count of people, or replacing a missing count with zero.
- Deciding that Equality Act 2010 section 20 or section 149 has been met.

## How to run

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -q
python eval/evaluate.py
python src/assistant.py --request examples/sample_request.json --as-of 2026-11-24
```

`eval/smoke_report.json` is a deterministic smoke test of 20 synthetic cases. It is not a model score. Paraphrase recall and page-support precision are not added to that total.

## Layout

```
experiments/75-benefits-information-assistant/
├── README.md
├── agent-manifest.yaml      permissions, copied to permissions.yaml
├── permissions.yaml
├── requirements.txt
├── fixtures/                pinned pages and the synthetic directory
├── examples/sample_request.json
├── src/                     deterministic core
├── tests/
├── eval/                    smoke test, not a model evaluation
├── schema/                  least-privilege tool contracts
├── skills/                  Microsoft Copilot harness layout
├── copilot-studio/          standard-harness topic guide
└── docs/
```

## Honest limitations

Phrase matching is not a decision that a person qualifies. The paraphrase set is a fixture, not a live recall rate. A sentence that uses none of the stems is not flagged. Masking counts identifiers and does not claim the text is anonymised. The pages, the directory, and the amounts are synthetic. Article 6 and Article 9 were not opened. No GOV.UK benefit page was quoted. The harness overview was opened on 24 November 2026 and states no price. Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. No tenant is configured.

## Status

Available. The Python core runs locally. The Copilot Studio topics and the skills are build guides, not an imported solution.

## Licence

MIT. See the repository [LICENSE](../../LICENSE).

## Permissions

[docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
