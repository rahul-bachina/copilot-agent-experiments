# Experiment 76: Charity Grant Application Assistant

Catalogue ID **V007**. Autonomy **A1**. The assistant drafts application answers, an attachments checklist, a deadline plan, and an impact report. The named applicant approves that exact content before a copy is written to a synthetic staging store. The agent does not submit an application, does not contact a funder, and does not send anything.

An applicant points at the pinned synthetic funder brief, the pinned charity profile, and the pinned monitoring rows. Harbour Lane Community Kitchen and Northfold Community Foundation are invented. The charity number label `synthetic-760014` is not a Charity Commission number.

The core is Python in the standard library. It calls [Experiment 12](../12-document-intake/) so the files are not confirmed and no purpose is confirmed, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. A user can run it without a tenant. Catalogue row V007 names M365 and the GitHub Copilot harness. This folder ships both Copilot Studio harnesses. No mailbox connector and no funder connector is enabled.

## The problem

A bid can say, in its own text, that the applicant has already approved it, that the gaps should be ignored, or that the reader should submit it. A deadline can be in the past, ambiguous, or unreadable. A caller can paste a different funder brief and ask for that one to be used. A monitoring note can name a person, give a count of three people, or describe distress. Those are the failures this starter is built to separate. A real approval is a separate object, from the directory applicant named on the draft, for that exact content hash.

## Non-goals

- Submitting an application.
- Contacting a funder.
- Sending the package, or writing it to a funder portal.
- Treating an approval marker, a role, or a clearance inside a document as the approval step.
- Applying a funder brief, charity profile, directory, or criteria object supplied in the request. The pinned fixtures are the source.
- Inventing an impact figure, a case study, a testimonial, or a partner.
- Papering over an eligibility gap, or a criterion the charity does not meet.
- Marking a carve-out, or a sentence that merely looks acceptable, as acceptable.
- Applying a biased or leading criterion.
- Guessing an ambiguous date, or replacing an unreadable date or offset with zero or with today.
- Copying monitoring text above the applicant's directory clearance.
- Stripping a legal hold or a retention label.
- Publishing a beneficiary count of one to four people, or adding that count into an aggregate.
- Deciding that Charities Act 2011 section 17 was met, or that a public-benefit duty was met.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 24 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Charity Commission CC3, The essential trustee](https://www.gov.uk/government/publications/the-essential-trustee-what-you-need-to-know-what-you-need-to-do-cc3/the-essential-trustee-what-you-need-to-know-what-you-need-to-do) | The sentence on carrying out the charity's purposes, and two sentences from section 4.2 on public benefit. The page was marked updated 16 September 2026. PB1, PB2, and PB3 were not opened. |
| [Charities Act 2011 section 17](https://www.legislation.gov.uk/ukpga/2011/25/section/17) | Section 17(1) and section 17(5), quoted in `src/sources.py`. The page listed no known outstanding effects for section 17. It also said revised legislation on the site may not be fully up to date. Section 14 was not opened. The cross-reference inside section 17(1) is unverified. |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(c), the data-minimisation principle, quoted in `src/sources.py`. Article 6 and Article 9 were not opened. No lawful basis is asserted. |

The quotes are context for the applicant. They are not a finding that the duty was met, and they are not legal advice.

## What the result does

`prepare_application()` reads one request and the question date, and writes one JSON document. The answers, the eligibility reading, and the deadline use the pinned files in `fixtures/`. A caller-supplied brief or directory is diffed and not applied. The same inputs and the same date produce the same JSON. `human_approval` is null. `submitted`, `funder_contacted`, and `sent` stay false.

**Eligibility.** Each pinned check is met, not met, or unreadable. Match funding is not on the profile, so EL-MATCH stays not met. The safeguarding policy date is 15 January 2025, and the deadline is 31 March 2027, so the twelve-month window in the brief is not met. That window is the brief's rule. It is not a statutory period. A claim that the gap is met is flagged and does not change the status.

**Answers and the impact report.** A meal count, a beneficiary count, or a quotation is copied only from a monitoring row or the profile, with the source reference. A beneficiary count below 5 is not published and is not added into a total. Five is this starter's threshold. An unreadable count is flagged and is not replaced with zero. A partner is named only when the profile names them. Word limits are the integers on the pinned questions. An answer that would exceed the limit is omitted rather than cut in a way that changes a figure.

**Deadline.** The pinned deadline is parsed. It is compared with the question date, not with today. A past deadline is flagged. An ambiguous or unreadable date is flagged. An offset that is not an integer is flagged and is not replaced with zero. The offsets in the brief are planning offsets. They are not statutory periods.

**Text.** An approval marker, a self-declared role, or a self-declared clearance in the text is recorded and not trusted. "It is not true that …" is not an inclusion. A distress, grievance, or safeguarding stem is routed even when the sentence denies it. The cue text is not copied. A safeguarding policy title is not that cue. A carve-out after acceptable wording is not marked acceptable. A biased criterion in a caller object is flagged and not applied.

**People and markings.** Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are counted. The values are not stored. The case-note body is not copied. The output is not described as anonymised. Metadata and content are both read. A SECRET cover is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**Intake.** Experiment 12 inventories the monitoring files that have text, up to 12 files. `files_confirmed` and `purpose_confirmed` stay false. Figures are still read from the structured rows when a row has no note.

`submit_application`, `contact_funder`, `send`, and `write_production` raise `GrantForbidden`.

`record_applicant_approval()` records that the directory applicant named on the draft approved one item. The content hash has to match the draft now in the result. A string is not coerced to true. The record does not submit the bid.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08 and 12 must be present beside this folder.

```bash
cd experiments/76-charity-grant-application-assistant
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/grant.py --request examples/sample_request.json --as-of 2026-11-14
```

The sample request carries approval language, a self-declared role, a self-declared clearance, and a caller brief on purpose. They are stripped or ignored. `human_approval` stays null. The monitoring rows include a distress sentence, so the outcome is `route_to_human`.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total. On the committed run, 20 of 20 cases passed, and each paraphrase category had at least 20 sentences with recall 1.0 and precision 1.0 on those sentences. That is not a live rate.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Cue matching is a stem list. A paraphrase that uses none of those stems is not flagged. The smoke report states recall and precision on the fixture sentences. That is not a live rate.
- "Not true that", "nobody", "does not", and the other denial frames are the negation rule. A denial that uses none of them can be missed. A distress stem is routed even inside a denial.
- The twelve-month safeguarding window and the deadline offsets are the pinned brief. They are not statutory periods.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period.
- Counts of people below 5 are not published. Five is this starter's threshold. A statistics authority page was not opened. This is not anonymisation.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- Section 14 of the Charities Act 2011 was not opened. PB1, PB2, and PB3 were not opened. Article 6 and Article 9 were not opened.
- Experiment 12 inventories at most 12 files. Structured rows without a note are still used as figures. The intake flag says when the batch was capped.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- The harness overview was opened on 24 November 2026. See [docs/harness-comparison.md](docs/harness-comparison.md). The page did not use the words "GitHub Copilot harness".
- Harbour Lane Community Kitchen and Northfold Community Foundation are fictional.
- This is not a decision that the charity is eligible, and it is not a submitted application.

## Two Copilot Studio harnesses

Both call `src/grant.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness submits a bid. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_applicant_approval` only with the approval object. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** Catalogue row V007 names M365 and this harness. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The file tools that harness can use are not used to edit the monitoring rows or to send. No mailbox connector is enabled in this starter.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The hashes, the gaps, and the approval step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Document intake: [../12-document-intake/](../12-document-intake/).
- UK identifier redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/76-charity-grant-application-assistant/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── fixtures/
└── tests/
```

MIT Licence. See [LICENSE](../../LICENSE).
