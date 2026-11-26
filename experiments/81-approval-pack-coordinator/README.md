# Experiment 81: Approval Pack Coordinator

Catalogue ID **O007**. Autonomy **A1**. The coordinator assembles a draft approval pack for a synthetic spend request, policy exception, or change request. It names the approvers and the evidence the pinned matrix requires for that type and threshold, checks every evidence item, and writes a cover note. The named approver reviews the complete pack and decides. The agent does not approve, reject, sign, submit, pay, or send.

This is a general approval-routing pack. It is not Experiment 18, which builds an evidence-pack index for an export a person has not approved. It is not Experiment 74, which assembles a board pack for a company secretary. The pack hash is Experiment 74's `digest`. The evidence sha256 comes from Experiment 18's `build_pack`. Neither call decides this request. `paper_hash` is not called, because a board-paper projection would drop the fields this pack has to bind.

Status: **Available** as a local starter. No tenant is configured. No model is called.

## Who it helps

An approvals officer, a finance checker, or a change manager who has to see, in one place, who must decide and which evidence is missing, stale, unsigned, superseded, the wrong version, or in conflict. The officer still decides.

## What it does

Given one synthetic request and the question date, the starter:

1. Reads the pinned matrix, checklist, and directory. A matrix, directory, or delegation in the request is listed and not applied.
2. Selects the band from the type and the threshold. An unreadable amount is not turned into zero. Parts that add up are routed at the total, so a split does not stay under a lower band. A headline that disagrees with the parts is not chosen.
3. Names directory people for each required role. The requester is excluded. A guest, an inactive person, and a person over their delegation limit are excluded.
4. Checks each evidence item for presence, expiry, supersession, signature, version, currency, support, and conflicting values. Conflicting values are both cited. Neither is chosen.
5. Keeps protective markings from the metadata and from the text, taking the higher one, and keeps legal-hold and retention labels.
6. Routes distress, safeguarding, whistleblowing, grievance, and disclosure cues to a person, including a denial. The cue text is not copied.
7. Writes a cover note of what is present, missing, or stale, and what was checked.
8. Holds a copy of that pack and its hash. `record_approver_decision` records the named approver's approve, reject, or return only for that held copy.

## What it does not do

- It does not approve, reject, sign, submit, pay, or send. Those functions raise.
- It does not let the requester approve their own request.
- It does not treat an approval sentence, a role, a guest flag, or a clearance inside the evidence as the directory or the decision.
- It does not follow instructions embedded in the evidence.
- It does not decide that a statutory duty was met.
- It does not search Microsoft 365 or write a finance system.

## UK context

Opened on legislation.gov.uk on 26 November 2026.

Companies Act 2006, section 386(1), at <https://www.legislation.gov.uk/ukpga/2006/46/section/386>:

> Every company must keep adequate accounting records.

Section 386(2) on that page begins "Adequate accounting records means records that are sufficient—" and continues with paragraphs (a), (b), and (c). Paragraph (c) on the page ended with an F1 omission marker. The omitted words are not quoted here. The page said the section is up to date with all changes known to be in force on or before 25 November 2026.

The Accounts and Audit Regulations 2015 (S.I. 2015/234), regulation 3, at <https://www.legislation.gov.uk/uksi/2015/234/regulation/3>, headed "Responsibility for internal control". The page showed the extent as E+W:

> A relevant authority must ensure that it has a sound system of internal control which—
>
> (a) facilitates the effective exercise of its functions and the achievement of its aims and objectives;
>
> (b) ensures that the financial and operational management of the authority is effective; and
>
> (c) includes effective arrangements for the management of risk.

The words "segregation of duties" were not on either page. That phrase, as a statutory quotation, is **unverified**. The spend bands in `fixtures/approval_matrix.json` are the pinned synthetic matrix. They are not a statutory minimum. Nothing in this starter is a finding that section 386 or regulation 3 was met.

## Honest limitations

- The held copy lives in the process. A restart drops it.
- A distress sentence that uses none of the cue stems is not flagged. The recall figures in `eval/smoke_report.json` are a fixture smoke test, not a live model rate.
- Phone numbers, email addresses, dates of birth, postal addresses, and personal names in an excerpt are masked. The output is not anonymised. Experiment 08 counts UK identifiers and its redacted text is not copied.
- A headcount below 5 is withheld, including a difference or a percentage filed under another name. Five is a starter rule, not a claim of anonymisation.
- The marking order is a starter rule. The Government Security Classifications policy was not opened.
- Entra Agent ID, Conditional Access, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 26 November 2026. Treat that product behaviour as unverified.
- Reedmarsh Internal Services and Northfold Supplies are invented.

## Layout

```
experiments/81-approval-pack-coordinator/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/coordinator.py
├── fixtures/
├── eval/
├── skills/
├── copilot-studio/
└── docs/
```

`permissions.yaml` is the same file as `agent-manifest.yaml`. It validates against `schemas/agent-manifest.schema.json`.

## Run it

From this folder, with Python 3.11:

```bash
python -m pip install -r requirements.txt
python src/coordinator.py --request examples/sample_request.json --as-of 2026-11-25
python -m pytest tests/ -q
python eval/evaluate.py --output eval/smoke_report.json
```

The sample is a synthetic roof spend of 18400 pounds. `human_approval` is null. The phone number and the email address in the quote are not in the JSON. The caller-supplied matrix is not applied.

The smoke test is deterministic. It is not a model evaluation. Twenty cases are one row each. Paraphrase recall is a separate block and is not added to that total.

## Harnesses

Both Copilot Studio harnesses call this Python core. See [docs/harness-comparison.md](docs/harness-comparison.md), [copilot-studio/README.md](copilot-studio/README.md), and [docs/github-copilot-harness.md](docs/github-copilot-harness.md). The Power Automate note is [copilot-studio/power-automate-flow.md](copilot-studio/power-automate-flow.md). It is guidance. It is not an importable solution. Microsoft Foundry, if used, only turns the JSON into a short note. See [docs/foundry.md](docs/foundry.md).

## Licence

MIT. See the repository `LICENSE`.
