# Experiment 71: Data Retention Decision Support

Catalogue ID **L007**. Autonomy **A0**. The assistant explains which pinned synthetic retention line appears to apply, calculates an indicative review or transfer date from the trigger, and lists the questions the records owner must answer. The records or legal owner makes every retention, disposal, transfer, or hold decision. The agent does not delete, move, relabel, or archive anything, and it does not send.

A records owner names one synthetic series and the date the question is about. The core reads a pinned inventory, a pinned retention schedule, and a pinned directory. Mereford Borough Council and the series titles are invented.

The core is Python in the standard library. It calls [Experiment 01](../01-foi-complaint-triage/) for a keyword class and an urgency level, [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers, and [Experiment 12](../12-document-intake/) so the note is not confirmed and no purpose is confirmed. Those calls do not decide. A user can run it without a tenant. The catalogue row names Microsoft 365 and Copilot Studio first. This folder still ships both Copilot Studio harnesses. The Microsoft Foundry option is a note.

## The problem

A retention schedule and a records inventory can disagree with each other, and with a note pasted into the chat. The note can say the owner has already approved disposal, that a legal hold should be stripped, or that the series contains no personal data, in the same paragraph that names a person. A missing or ambiguous trigger date is not today's date. An open FOI request, a subject access request, litigation, an inquiry, or a legal hold is not a prompt to dispose. Those are the failures this starter is built to separate. A real seen step is a separate object, from the directory records owner or legal owner, for that exact advice hash. Seeing the advice does not authorise disposal.

## Non-goals

- Deciding retention, disposal, transfer, or hold.
- Deleting, moving, relabelling, archiving, or sending a record.
- Suggesting disposal for a legal hold or an open FOI, SAR, litigation, or inquiry.
- Treating approval text inside a title or a note as the seen step.
- Trusting a self-declared role, guest status, or clearance.
- Trusting a schedule, inventory, or directory pasted into the request.
- Coercing an unreadable date or period to today or to zero.
- Marking a carve-out, or a shorter caller period, as safe or acceptable.
- Applying a biased or leading criterion.
- Stripping a legal hold or a retention label.
- Deciding that UK GDPR Article 5(1)(e) was met, that a section 77 offence was committed, or that a Public Records Act duty was met.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 23 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`. The extracts did not show an "up to date on or before" date. Currency is unverified. The section 46 code of practice was not opened. Article 84B was not opened.

| Source | What this starter takes from it |
| --- | --- |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(e), as the page showed it: "kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed; personal data may be stored for longer periods insofar as the personal data will be processed solely for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes in accordance with Article 84B (‘storage limitation’)". The footnote on that page says the words were substituted on 5 February 2026 by the Data (Use and Access) Act 2025, section 87(1)(a). The editorial marker F4 is not part of the quote. Context for the records owner. Not a finding that the principle was met. Article 6 and Article 84B were not opened. |
| [Freedom of Information Act 2000, section 46](https://www.legislation.gov.uk/ukpga/2000/36/section/46) | Section 46(1): "The Secretary of State shall issue, and may from time to time revise, a code of practice providing guidance to relevant authorities as to the practice which it would, in his opinion, be desirable for them to follow in connection with the keeping, management and destruction of their records." The revised text names the Secretary of State. The page said there are currently no known outstanding effects, and also that revised legislation on the site may not be fully up to date. |
| [The National Archives, records management code](https://www.nationalarchives.gov.uk/information-management/manage-information/planning/records-management-code/) | The page says: "Section 46 of the Freedom of Information Act 2000 required the Lord Chancellor to issue a Code of Practice on the management of records." That sentence is from the National Archives page. It is not the code. A GOV.UK publication URL tried on the same date returned 404. The code's paragraphs are unverified. |
| [Freedom of Information Act 2000, section 77](https://www.legislation.gov.uk/ukpga/2000/36/section/77) | Section 77(1) is the offence of altering, defacing, blocking, erasing, destroying, or concealing a record held by the public authority, with the intention of preventing disclosure of information the applicant would have been entitled to. The quote is in `src/sources.py`. This starter does not decide that an offence was committed. The page carried the same currency caveat as section 46. |
| [Public Records Act 1958, section 3](https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/3) | Section 3(4): "Public records selected for permanent preservation under this section shall be transferred not later than 20 years after their creation either to the Public Record Office or to such other place of deposit appointed by the Secretary of State under this Act as the Secretary of State may direct". The proviso and section 3(1) are in `src/sources.py`. The 20 years is a latest transfer point for selected records. It is not a minimum retention period for every record. Section 3(4A) was on the page. Orders under the Constitutional Reform and Governance Act 2010, section 45(2), were not opened. The Act is applied in this starter only where the pinned inventory says the series is a public record selected for permanent preservation. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox. The prose says agents on that harness use Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. No "last updated" line was in the extract. That date is unverified. |

## What the result does

`advise_retention()` reads one request and the question date, compares any caller-supplied schedule, inventory, or directory with the pinned files, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `disposal_suggested`, `deleted`, `moved`, `relabelled`, `archived`, and `sent` stay false. `may_be_relied_on_as_a_disposal_decision` stays false.

**The line.** An active pinned line whose series code matches the pinned inventory is cited, with the reason. A withdrawn line is not cited. Two active lines are both cited and neither date is chosen.

**The date.** The indicative date is the trigger date plus the pinned period. 29 February 2024 plus one year is 28 February 2025. That clamp is a starter rule, not a statute. A numeric date with both numbers from 1 to 12 is ambiguous and is not resolved. An unreadable date is not replaced with today or with zero. The question date is the date the caller names.

**Blockers.** A legal hold, an open FOI, SAR, litigation, or inquiry, a missing or unreadable flag, conflicting lines, distress, or a public record selected for permanent preservation is routed to the records owner. Disposal is not suggested. Personal data raises an Article 5(1)(e) question for the owner. It is not a finding. A denial in the note does not clear a hold or a personal-data flag on the pinned inventory.

**People and markings.** The directory supplies the role and the clearance. "My role is records owner" and "my clearance is TOP SECRET" are ignored. Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. "Do not downgrade SECRET" still counts. A compound label takes the higher marking. A legal hold and every retention label stay on the result. Phone numbers, email addresses, dates of birth, postal addresses, and personal names are counted and not stored.

**Caller sources.** A shorter period, a destroy action, or an unreadable period in a pasted schedule is flagged. The pinned line is used. It is not marked safe. A carve-out after acceptable wording is not marked acceptable. A biased criterion is not applied.

**Seen.** `record_advice_seen()` records that the directory records owner for that series, or a legal owner, has seen that advice hash. A string is not coerced to true. Tampered content is rejected. The acknowledgement does not delete or dispose.

`delete_records`, `move_records`, `relabel_records`, `archive_records`, `transfer_records`, `dispose`, `apply_hold`, `lift_hold`, and `send` raise `RetentionForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 01, 08, and 12 must be present beside this folder.

```bash
cd experiments/71-data-retention-decision-support
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/advice.py --request examples/sample_request.json --as-of 2026-11-20
```

The sample request carries approval language, a one-year caller schedule, a self-declared role, and a self-declared clearance on purpose. They are ignored. `human_approval` stays null. The indicative date is 2030-03-31 from pinned line SCH-FIN-01. Disposal is not suggested.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Cue and support matching is a stem list. A wording that uses none of those stems is not flagged. The smoke report states recall on the fixture sentences. That is not a live rate. Support precision on the negative controls is in the same report.
- "Not" within eight words before a phrase can hide a match. "It is not true that X includes Y" is the case this rule is built for. Markings use a narrower denial so "do not downgrade SECRET" is still SECRET.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened.
- A schedule whose next-review date is the question date is not relied on. That is this starter's rule. It is not a statutory period. Experiment 12's document window is that experiment's rule.
- Adding a year to 29 February lands on 28 February when the target year is not a leap year. A day/month pair that can be read either way is left ambiguous. Those are starter rules.
- The 20 years in Public Records Act 1958 section 3(4) is the latest transfer point in the text that was opened, for records the pinned inventory marks as selected for permanent preservation. Transitional orders were not opened. The proviso was not applied. It is not a finding of breach when the date appears to have passed.
- The small-number threshold is 5. Counts from 1 to 4 are replaced. Zero stays zero. It is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is", a title plus a surname, or "my wife is" plus a name are counted. The values are not stored. A name with none of those patterns is not counted.
- Article 5, sections 46 and 77, and section 3 had no currency stamp in the extract opened on 23 November 2026. Those pins are not confirmed. Article 6, Article 9, and Article 84B were not opened. The section 46 code was not opened.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Mereford Borough Council and the series titles are fictional.
- This is not a retention decision, a disposal authority, or legal advice.

## Statute

The manifest does not assert the controller's lawful basis. Article 5(1)(e), section 46(1), section 77(1), and section 3(4) were read on 23 November 2026 as context for the records owner. `article_5_met`, `offence_found`, and `pra_duty_met` stay null.

A retention label and a legal hold stay on the result. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/advice.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness decides disposal. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_advice_seen` only with the seen object. Microsoft's harness overview, opened 23 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. The catalogue stack is Microsoft 365 and Copilot Studio. This folder does not call Microsoft Graph and does not ship a solution package.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 23 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says it uses Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The catalogue row L007 names Microsoft 365 and Copilot Studio first. The gates are the same.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The hash, the line, and the seen step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- FOI triage signals: [../01-foi-complaint-triage/](../01-foi-complaint-triage/).
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Document intake: [../12-document-intake/](../12-document-intake/).

## Project structure

```
experiments/71-data-retention-decision-support/
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
