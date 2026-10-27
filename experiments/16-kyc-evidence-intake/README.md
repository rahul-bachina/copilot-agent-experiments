# Experiment 16: KYC Evidence Intake Agent

Catalogue ID **B004**. A reviewer of one synthetic customer file against the Money Laundering Regulations 2017. Stack in the catalogue: Copilot Studio, Power Platform, and Azure. Autonomy **A1**.

It builds on [Experiment 12](../12-document-intake/) (O001), purpose `kyc_evidence`. That intake already calls [Experiment 08](../08-uk-pii-redaction-gateway/) (O005), the UK identifier PII gateway. This experiment calls `intake()`. It does not ship a second inventory or a second redactor.

**Status.** Available as a local starter. The checklist runs in Python with no Azure credentials and no network. It is not an importable Copilot Studio solution, and a live model has not been scored.

A KYC reviewer confirms the documents and the purpose. The agent never confirms those steps itself. It never approves, rejects, or onboards a customer. It never assigns a final risk rating. It never files a suspicious activity report. Customer-facing wording is a draft the reviewer might later use. The agent does not send it, and the wording must not hint at suspicion (Proceeds of Crime Act 2002, section 333A).

Samples are synthetic. The firm and the customers are fictional. National Insurance and NHS values are the non-allocatable fixtures documented in Experiment 08.

## The problem

An analyst opening an enhanced due diligence file spends time on a completeness pass: which customer due diligence points under regulation 28 have a document behind them, whether the file itself mentions a regulation 33 trigger, which dates look old, and what to ask the reviewer. A sentence inside a passport scan, or an HTML comment, can also try to mark the customer approved, set a risk rating, or tell the customer that a report has been filed.

This starter is that pass. The decision stays with the reviewer.

## Who it helps

**A KYC reviewer at a fictional payments firm.** They see what the file evidences, what is missing, what is stale on this starter's freshness window, and which questions are still theirs. They confirm the document list and that the purpose is `kyc_evidence`.

**The person who might later write to the customer.** They get a short draft that asks for a missing document type in generic words. It does not say why. Sending it is not a tool of this agent.

**A later reader of the catalogue.** B004 is the specialist row Experiment 12 named and did not call. This folder is that row. It still does not onboard anyone.

It does not help a team that wants the tool to approve a customer, set a risk rating, or file a report.

## Non-goals

- Approving, rejecting, or onboarding a customer.
- Assigning a final risk rating, including high, medium, or low.
- Deciding that regulation 33 applies, that someone is a PEP, or that a country is on the FATF call-for-action list.
- Filing, drafting, or not filing a suspicious activity report. There is no nominated-officer workflow here.
- Sending anything to the customer, the NCA, a supervisor, or anyone else.
- Writing a production record, including Dataverse, SharePoint, or an onboarding system.
- Confirming the documents or the purpose from a sentence inside a file.
- Re-implementing Experiment 12 or Experiment 08.
- Treating the 90-day freshness flag as the regulation 40 record-keeping period.
- Applying JMLSG paragraph numbers. Part I is named below and was not opened.
- Autonomy A3.

## What the review does

`src/review.py` reads one JSON customer file and writes one JSON document. The same file and the same as-of date produce the same JSON. `documents_confirmed` and `purpose_confirmed` are false. `final_risk_rating` is null. `actions_taken` is empty.

**Intake.** The files are passed to Experiment 12 `intake()` with `requested_purpose` `kyc_evidence`. That call hashes each file, suggests a keyword class, previews the O001 checklist, scans for that experiment's injection phrases, flags document dates, and calls Experiment 08. This draft keeps that JSON. It does not copy file bodies out of it, because the intake does not store them either.

**CDD, regulation 28.** The checklist looks for an identity marker and an address marker on a file Experiment 12 actually read, and for a closed list of phrases about the purpose and intended nature of the relationship. Verification under regulation 28(2)(b) and 28(18) is `not_determined`. This starter does not check a reliable source. A phrase being present is not a finding that the duty is met. `sufficient` is false on every row.

**EDD triggers, regulation 33.** Three triggers are read as words in the file, not as a decision:

- Regulation 33(1)(b), as revised: a person established in a **FATF call for action country**. The words "high-risk third country" were substituted on the revised regulation, by SI 2026/621 regulation 19. A file that still uses the old words is reported as containing those words. The FATF list was not downloaded. A country named in the file is quoted for the reviewer and is not classified.
- Regulation 33(1)(d): the file contains a closed PEP phrase. The regulation applies where a relevant person **has determined** that the customer is a PEP, or a family member or known close associate of a PEP. This draft does not make that determination. Regulation 35 was not opened as its own page.
- Regulation 33(1)(f), as revised on 30 June 2026: unusually complex or unusually large given the nature of the transaction, an unusual pattern of transactions, or no apparent economic or legal purpose. Regulation 33(4) tells the relevant person to consider whether the transaction or the relationship appears suspicious. That word stays in the reviewer question. It is not copied into customer-facing text.

Other regulation 33 cases (the firm's own regulation 18 assessment, correspondent relationships, false or stolen identification) are not decided from this file.

**Record-keeping, regulation 40.** The period in regulation 40(3) is five years, beginning on the date the relevant person knows, or has reasonable grounds to believe, that an occasional transaction is complete, or that the business relationship has come to an end. Paragraph (4) says the person is not required to keep the records in paragraph (3)(b)(i) for more than 10 years. This starter quotes that. It does not delete anything. If the file states that a relationship has ended, or that an occasional transaction is complete, and gives a date, the draft adds five years as arithmetic for the reviewer. That date is not an instruction to retain or to delete. The 90-day window is a separate freshness flag. It is not this period.

**Stale.** A document date more than `stale_after_days` before the as-of date is stale. The default is 90 days. A date exactly 90 days earlier is not stale. A future, missing, or unparseable date is not current. The same window applies to the source pin of 27 October 2026. A sentence in the file that says a document is current does not clear the flag.

**Tipping-off.** Customer-facing text is assembled from fixed sentences about document types. It is then checked against a closed lexicon (suspicion, a report, a PEP, a risk rating, and the other words in `src/tipping_off.py`). If any of those words are present, the text is replaced with one generic line and the guard is recorded. Reviewer questions are marked `not_for_the_customer`. They may quote regulation 33(4). They are not the customer note.

**Prompt injection.** File text and a screening note are untrusted. KYC phrases, including hidden in an HTML comment, after a form feed, after blank lines, or split by zero-width characters, are recorded. `followed` is false. Experiment 12 records its own list on the nested intake. Neither list confirms the documents, sets a rating, or sends the customer note.

**Human step, outside `review()`.** `record_reviewer_confirmation` accepts only the role "KYC reviewer", only when the file ids match the draft in order, and only for the purpose `kyc_evidence`. A checksum mismatch blocks it. It still does not approve the customer. `approve_customer`, `reject_customer`, `onboard_customer`, `assign_risk_rating`, `file_sar`, and `send_to_customer` raise `ReviewForbidden`. The skills say the agent must not call the recording function.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 12 and 08 must sit beside this folder, which they do in this repository.

```bash
cd experiments/16-kyc-evidence-intake
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/review.py --input examples/sample_customer_file.json --as-of 2026-10-27
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

The exit code is 0 when a draft is produced, including when files are stale or an injection phrase is present. Those are findings, not an approval. A file that is not marked synthetic is refused.

## Limitations

- **Text only.** Whatever Experiment 12 cannot read, this checklist cannot treat as evidence. `not_read` is a gap. Azure Document Intelligence is not called. See [docs/foundry.md](docs/foundry.md).
- **Keywords and closed phrases miss.** A real passport scan that does not contain the word "passport" is not an identity marker. A PEP described without the listed words is `not_in_file`. That is a gap, not a clean result.
- **The checklist is not sufficiency and not a risk rating.** `final_risk_rating` stays null. `sufficient` stays false.
- **The FATF list is not fetched.** Regulation 33(3)(a) points at a list that has effect from time to time. Naming a country in the file does not put it on that list, and does not take it off.
- **Regulation 35 was not opened.** PEP definitions and the family-member test are not applied from that regulation.
- **JMLSG Guidance, Part I, was not opened.** No part of it is applied. The name is here so a firm knows what was left out.
- **Regulation 40(5) deletion is not performed,** and the exceptions in that paragraph are not decided.
- **The five-year date is arithmetic** on a date the file states. It is not a finding that the relevant person knows the relationship has ended.
- **The 90-day window is not a statutory retention period.**
- **Experiment 08's misses are inherited,** via Experiment 12. Names, email addresses, and telephone numbers are not redacted. This draft does not copy the source text, and it does not claim the text was anonymised.
- **Customer-facing text is a template.** It cannot ask a nuanced question. The guard is a word list. A hint that avoids the list would pass the guard. The reviewer still has to read the note before anyone uses it.
- **A file over 20,000 characters is not scanned** by Experiment 12. An instruction in it is not detected by either phrase list.
- **The smoke test is not a model score.**

This is not legal advice, a DPIA, or a statement that a deployment complies with the Money Laundering Regulations. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `review()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness confirms the documents, approves a customer, or sends the note. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic for a reviewer. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. It is not a customer chat bot. The Customer Conversation harness is the wrong harness for this file, because a customer conversation is where tipping-off risk sits.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the draft explained. It is not the GitHub Copilot service. Skills are in [skills/](skills/). Microsoft's overview, opened 27 October 2026, says agents on that harness use Copilot Credits. Prices were not copied. A last-updated line was not in the text retrieved for this experiment. The overview did not mark the harness itself as preview.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The intake this experiment calls: [../12-document-intake/](../12-document-intake/).
- The gateway that intake calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/16-kyc-evidence-intake/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── kyc_injection.py
│   ├── review.py
│   ├── sources.py
│   └── tipping_off.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 27 October 2026

Legislation is quoted from the pages below. The operative words used in the checklist are in `src/sources.py`.

- [Money Laundering Regulations 2017, regulation 28](https://www.legislation.gov.uk/uksi/2017/692/regulation/28). The page says it is up to date with all changes known to be in force on or before 26 October 2026. There are changes that may be brought into force at a future date. Regulation 28(9) and (9A) are shown as substituted on 18 November 2025.
- [Regulation 33](https://www.legislation.gov.uk/uksi/2017/692/regulation/33). The same "on or before 26 October 2026" line. Regulation 33(1)(b), 33(1)(f)(i), and 33(3)(a) are annotated as substituted on 30 June 2026 by SI 2026/621.
- [SI 2026/621, regulation 19](https://www.legislation.gov.uk/uksi/2026/621/regulation/19), original version as made. In regulation 33(1)(b), for "high-risk third country", in both places, substitute "FATF call for action country". In regulation 33(1)(f)(i), for "complex or unusually large" substitute "unusually complex or unusually large in each case given the nature of the transaction". Regulation 33(3)(a) is replaced with the FATF call-for-action definition. The footnote gives a FATF web address. That FATF page was not opened.
- [SI 2026/621, regulation 1](https://www.legislation.gov.uk/uksi/2026/621/regulation/1). Regulation 19 is not in the list of provisions given a later commencement. The 30 June 2026 date is the legislation.gov.uk annotation on the revised regulation 33. It is not a date this repository calculated.
- [Regulation 40](https://www.legislation.gov.uk/uksi/2017/692/regulation/40). Opened the same day. The changes banner did not include the "up to date with all changes known to be in force on or before" sentence that regulations 28 and 33 carried. Amendments listed on the page are 26 June 2017, 25 May 2018, 6 October 2020, and 1 September 2023. The pending effects shown beside it insert Schedule 6 paragraph 7(ga) and regulation 34A. They do not amend regulation 40 in the text that was read.
- [Proceeds of Crime Act 2002, section 333A](https://www.legislation.gov.uk/ukpga/2002/29/section/333A). The page says it is up to date with all changes known to be in force on or before 26 October 2026.
- [FCA, second cohort for AI Live Testing](https://www.fca.org.uk/news/press-releases/fca-announces-second-cohort-ai-live-testing). First published 21 April 2026, last updated 21 April 2026. Use cases named on the page include anti-money laundering detection and Know Your Customer. This agent is not one of those tests.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), opened 27 October 2026. A last-updated date was not in the text retrieved for this experiment.

Not opened, and not applied:

- JMLSG Guidance, Part I. Cited by name and part only.
- Regulation 35 (PEPs).
- The FATF call-for-action list page named in the SI 2026/621 footnote.
- Sections 333B, 333C, and 333D (permitted disclosures). The customer note is not a disclosure under those sections. It is a document request that the agent does not send.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
