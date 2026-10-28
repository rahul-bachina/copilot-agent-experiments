# Experiment 17: Invoice Exception Triage Agent

Catalogue ID **F004**. An accounts-payable assistant for a UK public body or a regulated firm. It takes one synthetic invoice that failed an automated 2-way or 3-way match, classifies the exception, gathers the evidence, and drafts a recommended resolution for an AP reviewer.

**Autonomy A1.** The AP reviewer approves the resolution. A bank-detail change is routed to a bank-detail verifier first. The agent never posts, approves, holds, or pays an invoice, and it never changes supplier bank details.

Stack in the catalogue: Power Platform, AI Builder, and Copilot Studio. What you can run today is Python in the standard library, plus [Experiment 12](../12-document-intake/) for the file inventory and, through that intake, [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. AI Builder is not called. No Azure credentials and no network. See [docs/foundry.md](docs/foundry.md).

Samples are synthetic. North Quay Supplies Ltd and Harbour Test Council are fictional. No real person, firm, or invoice is in the case.

## The problem

A failed match still needs a person to see why: the price, the quantity, a missing purchase order, a possible duplicate, a VAT or supplier detail that does not line up, or a bank detail that has changed. The last of those is a fraud control. The useful draft is the classification and the evidence, with the payment decision left where it already sits.

## Who it helps

**An AP reviewer.** They see a closed set of exception classes, the pence or quantity difference, and a recommended resolution. Approving that draft does not post the invoice.

**A bank-detail verifier.** When the invoice text, or a fingerprint token, does not confirm the supplier master, the draft routes there first. The route does not change the bank record and does not verify the account.

**A finance lead in a contracting authority.** The draft shows the 30-day arithmetic in the Procurement Act 2023 where the case says that Act might apply, and it shows that the Public Contracts Regulations 2015 regulation 113 is revoked. It does not decide that a sum is due.

**A privacy reviewer.** UK identifier spans are proposed by Experiment 08, through Experiment 12. This agent does not release the text and does not describe it as anonymised.

## Non-goals

- Posting an invoice to a ledger, or approving it for payment.
- Holding an invoice.
- Paying a supplier, or instructing a payment date.
- Changing supplier bank details, or deciding that a new account has been verified.
- Deciding that an invoice is valid, undisputed, or a true duplicate.
- Deciding that input tax can be recovered.
- Sending a question to a supplier, a buyer, or a payee.
- Writing a production record, including a finance system, Dataverse, or SharePoint.
- Re-implementing Experiment 12 or Experiment 08.
- Calling AI Builder, Document Intelligence, or HMRC.
- Applying the Public Contracts Regulations 2015 regulation 113. That regulation no longer has effect.
- Treating a sentence in the invoice as the receipt date, the tolerance, or a clearance of a stale flag.
- Autonomy A3. There is no path on which the agent pays or posts without a person.

## What the triage does

`src/triage.py` reads one JSON case and writes one JSON document. The same case and the same as-of date produce the same JSON. `resolution.executed` is false. `actions_taken` is empty. Every payment flag is false.

**Intake.** Experiment 12 `intake()` runs with `requested_purpose` `general_records`. That catalogue has no accounts-payable purpose, and this experiment does not add one. The call is a preview. Hashes, a keyword class, that experiment's injection list, document dates, and Experiment 08 spans come back. This draft does not copy the file body.

**Fields.** Labelled lines on the visible text only. A price after a form feed, in an HTML comment, or after a run of blank lines is not extracted. Bank account numbers and sort codes are not stored. A bank fingerprint is a token, compared with the master, and the raw account is not copied out.

**Classes, in this order when more than one applies.** `bank_detail_change`, `duplicate_suspicion`, `missing_po`, `vat_supplier_mismatch`, `price_variance`, `quantity_variance`. The first one sets the recommended resolution. The others stay on the draft.

**Bank details.** A listed phrase, an unsafe fingerprint, or a token that does not match the master sets the bank class. The resolution is `route_to_separate_bank_verification`. It outranks a price difference.

**VAT.** VAT Notice 700/21 section 4.1 is a field checklist. Sections 4.4 and 4.5 are the £250 simplified-invoice ceiling, including VAT, and only when the currency is GBP. The draft does not decide input tax and does not decide that the supplier is a retailer. The six-year record sentence in section 2.4 is quoted. No destruction date is calculated.

**Prompt payment.** For a case marked `contracting_authority`, section 68 of the Procurement Act 2023: 30 days beginning with the day `received_on` says the invoice was received, or a later day the case gives as the day payment falls due. A stated concession, private utility, or school means section 68(1) is not applied, and no payment day is emitted. Section 88 is the same shape for `regulated_below_threshold`, with that section's own "first became due" wording. Regulation 113 of the 2015 Regulations is recorded as revoked on 24 February 2025 and is not applied. `payment_instructed` stays false.

**Prompt injection.** Instructions in the body, in an HTML comment, after a form feed, after blank lines, or between zero-width characters are recorded. `followed` is false.

**Human steps, outside `triage()`.** `record_bank_route` accepts only the role "Bank-detail verifier", and only when the flag is set. `record_ap_reviewer_decision` accepts only the role "AP reviewer". Approval is refused while a file is unread, a checksum fails, material is stale and not acknowledged, or a bank flag has no verifier record. Neither function posts, pays, or changes a bank record. The skills say the agent must not call them. `post_invoice`, `approve_invoice`, `hold_invoice`, `pay_invoice`, `change_supplier_bank_details`, `send_external`, and `write_production_record` raise `TriageForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 12 and 08 must sit beside this folder, which they do in this repository.

```bash
cd experiments/17-invoice-exception-triage
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/triage.py --input examples/sample_case.json --as-of 2026-10-28
```

`eval/evaluate.py` prints a **deterministic smoke test** of 24 synthetic cases. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A case that is not marked synthetic is refused. The exit code is 0 when a draft is produced, including when the invoice is stale or carrying an injection phrase. Those are findings, not a failed run, and they are not a payment.

## Limitations

- **Text only.** Whatever Experiment 12 cannot read, this triage cannot treat as an invoice. A PDF is `not_read`, which is a gap, not a clean result.
- **One line.** A second invoice line is not matched. Keywords in Experiment 12 can still suggest the class `invoice`. That suggestion is not a decision.
- **Labelled lines only.** "Unit price: 6.00" is read. A price written in a sentence is not.
- **The tolerance is the caller's.** Zero is the default. It is not a statutory rule. A tolerance written inside the invoice is ignored.
- **Ltd and Limited do not match.** The name comparison is case and whitespace only.
- **The VAT shape stored is GB and nine digits.** It is not an HMRC lookup and not a checksum. Other shapes are not copied into the draft.
- **£250 is not converted.** A currency other than GBP does not use the simplified-invoice ceiling, and prices are not compared.
- **The 30-day figure is arithmetic.** It is not a finding that a sum is due. Section 67 (electronic invoicing) and the text of section 73 (sub-contracts) were not encoded. Saving provisions in SI 2024/716 regulations 5 and 6 were not encoded, so this draft does not decide that a contract has left the 2015 Regulations.
- **The Late Payment of Commercial Debts (Interest) Act 1998 was not opened.** A case marked `not_a_public_contract` does not get a substitute clock.
- **A hidden fingerprint without a listed phrase can be missed** if it is not on a `Bank fingerprint:` line. Account numbers are deliberately not parsed.
- **A file over 20,000 characters is not scanned** by Experiment 12, and this experiment does not scan it either.
- **Experiment 08's misses are inherited.** Names, email addresses, and telephone numbers are not redacted.
- **The 90-day window is not the six-year VAT record period.**
- **The smoke test is not a model score.**

This is not legal advice, a DPIA, or a statement that a deployment complies with the Procurement Act or the VAT rules. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `triage()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness pays, posts, or changes a bank record. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The reviewer pastes a case, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the draft explained. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, retrieved 28 October 2026, says agents on that harness use Copilot Credits. Prices were not copied. The overview did not mark the harness itself as preview. It gives an accounts-payable example. This experiment still does not pay.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry, and the services that were not called: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The inventory this experiment calls: [../12-document-intake/](../12-document-intake/).
- The identifier gateway Experiment 12 calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/17-invoice-exception-triage/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── ap_injection.py
│   ├── rules.py
│   └── triage.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 28 October 2026

- [Record keeping (VAT Notice 700/21)](https://www.gov.uk/guidance/record-keeping-for-vat-notice-70021). Page last updated 18 March 2024. Sections 2.4, 3.1, 3.2, 4.1, 4.4, and 4.5.
- [Procurement Act 2023, section 68](https://www.legislation.gov.uk/ukpga/2023/54/section/68). In force 24 February 2025.
- [Procurement Act 2023, section 88](https://www.legislation.gov.uk/ukpga/2023/54/section/88). In force 24 February 2025.
- [Procurement Act 2023, Schedule 11](https://www.legislation.gov.uk/ukpga/2023/54/schedule/11), paragraph 5, which names the Public Contracts Regulations 2015. In force 24 February 2025.
- [Public Contracts Regulations 2015, regulation 113](https://www.legislation.gov.uk/uksi/2015/102/regulation/113). The legislation.gov.uk page records that the provision no longer has effect.
- [SI 2024/716, Schedule](https://www.legislation.gov.uk/uksi/2024/716/schedule), which brings sections 68 and 88 and Schedule 11 into force on 24 February 2025. Regulations 5 and 6 are named on the commencement information for paragraph 5 and were not encoded.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
