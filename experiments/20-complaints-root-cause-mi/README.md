# Experiment 20: Complaints root-cause and regulatory MI

Catalogue ID **UK04**. A draft management-information pack for a complaints owner. Stack in the catalogue: Fabric, Microsoft Foundry, and Microsoft 365. Autonomy **A0**.

It reads one batch of synthetic complaint records, proposes UK identifier redactions through [Experiment 08](../08-uk-pii-redaction-gateway/), and, for a financial-services batch, reuses [Experiment 02](../02-consumer-duty-complaint-intake/) `analyse()` for a suggested product and root cause. It groups the in-period records into themes. Every count lists the source record ids. It then drafts the words a complaints owner might take into one of three regulated contexts: a Consumer Duty governing-body report, a Housing Ombudsman Complaint Handling Code self-assessment pack, or Ofgem domestic complaints reporting. The complaints owner validates the clusters and the narrative before either is used.

**Status.** Available as a local starter. The draft runs in Python with no Azure credentials and no network. It is not an importable Copilot Studio solution, and a live model has not been scored.

`is_final_regulatory_return` stays false. `submitted`, `published`, and `sent` stay false. `clusters_validated` and `narrative_validated` stay false. `complying_with_consumer_duty` stays null. `code_compliant` stays null. `ofgem_return_complete` stays null.

Samples are synthetic. Northbridge Mutual, Harbourside Housing, and Lantern Energy are fictional. The National Insurance value in the sample is the non-allocatable fixture documented in Experiment 08.

## The problem

Boards and regulators expect an organisation to learn from complaints. The pack is still assembled by hand, and a language model will happily write a rate, a trend, or a sentence that the firm is complying. A figure that cannot be walked back to the records is not management information.

This starter is the clustering and the first draft. The complaints owner validates both. Nothing here is a return.

## Who it helps

**A complaints owner in an FCA-regulated firm.** They get suggested root causes from Experiment 02, counts that list record ids, and a draft that stops before the governing body is asked to confirm compliance under PRIN 2A.8.4R.

**A complaints officer at a social landlord.** They get a starter grouping of complaint narratives, a count of complaints the batch records as refused, and empty comply-fields against the Complaint Handling Code provisions this starter actually read. The annual submission is not filled in.

**A complaints lead at a domestic energy supplier.** They get a draft reading against the complaint types in Ofgem's November 2025 guidance, with unassigned records left unassigned. The monthly and quarterly templates are not completed and are not sent.

It does not help a team that wants the tool to file the return, publish the board report, or decide that the organisation is complying.

## Non-goals

- Approving clusters, approving a narrative, or presenting a draft as a final regulatory return.
- Confirming that a firm is complying with the Consumer Duty, including PRIN 2A.8.4R(2).
- Completing, publishing, or submitting a Housing Ombudsman annual submission, self-assessment, or Complaint Handling Failure response.
- Completing or sending an Ofgem monthly or quarterly complaints template, or the annual consumer complaints report in regulation 11 of the Gas and Electricity (Consumer Complaints Handling Standards) Regulations 2008.
- Deciding that a complaint was resolved to the consumer's satisfaction, or calculating "end of the first working day" from dates.
- Imputing a redress figure, a customer-account total, a per-100,000 rate, or a trend the prior file does not reconcile.
- Labelling a customer vulnerable. Experiment 02 flags are for a person to review.
- Upholding or rejecting a complaint, offering redress, or closing a case. That remains outside Experiment 02 as well.
- Writing a production complaints system, a board pack store, or a landlord website.
- Re-implementing Experiment 02 or Experiment 08.
- Publishing the draft, or sending it to the FCA, the Housing Ombudsman, Ofgem, or a resident.
- Autonomy A3.

## What the draft does

`src/report.py` reads one JSON batch and an as-of date and writes one JSON document. The same inputs produce the same JSON. `actions_taken` is empty.

**Period.** A record counts in the period figures only when `received_on` falls inside the period on the batch. Other records are listed and are not given a theme count. A sentence in a narrative does not move them.

**Financial services.** Each narrative is passed to Experiment 08, then to Experiment 02 `analyse()` on the redacted text. The suggested cause is the theme. If the batch also carries an Experiment 02 intake and its suggested cause differs, the record is `needs_owner` and is not given either cause. `breach_found` stays false. No customer is labelled vulnerable.

**Social housing.** A fixed starter lexicon, not an Ombudsman taxonomy, assigns one theme. First matching rule wins. Complaints the record marks as refused are counted by the recorded refusal type. Ombudsman materials are listed only when the batch supplies them. A missing list is "not supplied". It is not a finding that the Ombudsman published nothing.

**Energy.** Phrases are mapped to categories B5 to B22 in the Ofgem guidance opened on 29 October 2026. Where the category depends on the meter and the record does not settle the meter, the record is unassigned. Unassigned records are not placed in B22. While any record is unassigned, the draft does not say category B23 is complete. A resolved-by-the-next-working-day flag is counted only when the record already contains the boolean. Dates are not converted into that flag.

**Trace.** Every count figure's value equals the length of its record-id list. Cluster membership partitions the in-period records. Narrative sentences are templates. A number in a sentence is a figure value or part of the as-of date or the period dates. Redress is the sum of the pence on the records that have a figure. Records with no figure are a separate count. Nothing is imputed as zero.

**Redaction.** Each narrative, organisation name, service-improvement string, and supplied Ombudsman title is passed to Experiment 08 `propose()`. Model suggestions are off. The reversible vault is not requested. `output_is_anonymised` stays false.

**Prompt injection.** Instructions in the body, in an HTML comment, after a form feed, after blank lines, or between zero-width characters are recorded. `followed` is false. The phrase is removed before classification and before any string is copied. A payload key such as `submitted` or `is_final_regulatory_return` is stripped.

**Stale sources.** The pin of 29 October 2026 is stale when the as-of date is more than 90 days later. The draft is still a draft. A sentence in a record does not clear the flag. The 90-day window is a freshness flag for this starter. It is not a review period in PRIN, the Code, or the Ofgem guidance.

**Prior period.** A prior file is quoted only when each supplied figure's value equals the length of its record-id list. Otherwise the narrative does not contain the prior number.

**Human steps, outside `draft_report()`.** `approve_clusters`, `approve_narrative`, `submit_regulatory_return`, `publish_report`, `send_report`, and `write_production_record` raise `ReportForbidden`. `record_external_attestation` accepts only `caller` `human_outside_agent`, only the complaints owner, and only a matching checksum. The skills say the agent must not call it. The effect is none.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 02 and 08 must sit beside this folder, which they do in this repository.

```bash
cd experiments/20-complaints-root-cause-mi
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/report.py --input examples/sample_batch.json --as-of 2026-10-29
```

`eval/evaluate.py` prints a **deterministic smoke test** of the synthetic batches in `eval/synthetic_dataset.json`. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

The exit code is 0 when a draft is produced, including when a cluster is unassigned or an injection phrase is present. Those are findings, not a validation. A batch that is not marked synthetic is refused, and the refusal does not echo the narratives.

## Limitations

- **The draft is not a regulatory return.** `is_final_regulatory_return` is false on every result, including a batch whose text says otherwise.
- **One theme per record.** The first matching rule wins. A complaint about both damp and the time taken to answer it is not split. The complaints owner can.
- **The housing lexicon is not the Ombudsman's.** The Code does not publish a root-cause list. Categories here are labels for this starter.
- **Energy categories follow the November 2025 guidance examples, not a complete dictionary.** A phrase that is not on the list stays unassigned. B22 is not a bin for those records. The Excel templates themselves were not opened.
- **Standard Licence Conditions 5 and 32 were not opened.** The Ofgem guidance cites both. This starter quotes the guidance, not the licence text.
- **Working-day resolution is not calculated.** Regulation 2 defines a resolved complaint and a working day. Satisfaction is not inferred from a closed date, and this starter does not apply a bank-holiday calendar.
- **No per-100,000 rate is stated.** The guidance calculates one in the template. This draft will show the supplied account totals and the complaint count, and it will not round.
- **Experiment 02 is a starter taxonomy for a fictional firm.** It is not an FCA root-cause list. A suggested cause is not the firm's cause until the complaints owner validates it.
- **Experiment 08's misses are inherited.** Names, email addresses, and telephone numbers are not redacted. The draft must not be described as anonymised.
- **The injection list is a word list.** A novel instruction would pass it. The complaints owner still reads the draft.
- **The smoke test is not a model score.**
- **DISP 1.10, the FCA complaints-return form, was not opened.** This draft is not that return, and it does not cite a DISP reporting rule.

This is not legal advice, a Consumer Duty assessment, a Code self-assessment, or an Ofgem submission. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `draft_report()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness validates the clusters, validates the narrative, or submits a return. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic for a complaints owner. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. It is not a public chat. The Customer Conversation harness is the wrong harness, because this draft is internal management information.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a complaints owner who wants one cluster explained against the record ids. It is not the GitHub Copilot service. Skills are in [skills/](skills/). The harness overview, opened 29 October 2026, says agents and workflows on that harness use Copilot Credits. The comparison table on that page points the GitHub Copilot harness billing cell at a separate overview, which was not opened. No price is copied. A last-updated line was not in the text retrieved. The overview did not mark the harness itself as preview.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The intake this experiment calls for a financial-services batch: [../02-consumer-duty-complaint-intake/](../02-consumer-duty-complaint-intake/).
- The gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/20-complaints-root-cause-mi/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── report.py
│   ├── classify.py
│   ├── figures.py
│   ├── injection.py
│   ├── narratives.py
│   ├── reuse.py
│   └── sources.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 29 October 2026

Legislation, Handbook, Ombudsman, and Ofgem pages are quoted from the addresses below. The operative words used in the draft are in `src/sources.py`.

- [FCA Handbook, PRIN 2A.8](https://handbook.fca.org.uk/handbook/PRIN/2A/8.html). The page says the section was last updated on 26 June 2026. PRIN 2A.8.3R, dated 31 July 2023 on that page, says a firm must prepare a report for its governing body setting out the results of its monitoring under PRIN 2A.9 and any actions required as a result of the monitoring. PRIN 2A.8.4R, dated 26 June 2026, says that at least annually the governing body must review and approve the report on outcomes, confirm whether it is satisfied that the firm is complying with the Consumer Duty, and assess whether the future business strategy is consistent with the Duty. PRIN 2A.8.5R, dated 26 June 2026, says that when approving the report under PRIN 2A.8.4R(1) the governing body must also agree the actions and any strategy amendments there set out.
- [FCA Handbook, PRIN 2A.9](https://handbook.fca.org.uk/handbook/PRIN/2A/9.html). PRIN 2A.9.8R to PRIN 2A.9.12R are each dated 31 July 2023 on that page. PRIN 2A.9.11R says a firm must have in place processes to identify the root causes of any failure to deliver the outcomes listed in PRIN 2A.9.9R. This starter does not decide that those outcomes were failed.
- [Housing Ombudsman Complaint Handling Code](https://www.housing-ombudsman.org.uk/app/uploads/2024/09/03.Complaint-Handling-Code-24.pdf) (PDF dated applicable 1 April 2024, last revised 17 April 2024). Paragraph 1.2 defines a complaint. Section 8 requires an annual complaints performance and service improvement report, including the self-assessment. Section 9.4 says the senior lead must assess themes or trends. Section 9.7 lists the minimum information for the Member Responsible for Complaints and the governing body.
- [Housing Ombudsman, guidance on annual submissions](https://www.housing-ombudsman.org.uk/landlords-info/complaint-handling-code/guidance-on-annual-submissions/). The page says member landlords demonstrate compliance at least annually through a submission on a dedicated electronic form, and it gives the deadlines of 30 September for landlords with 1,000 homes or more, and six months after financial year-end for landlords with fewer than 1,000 properties. On 29 October 2026 the same page displayed a notice that the landlord portal and some online services were unavailable while systems were restored. This starter does not submit to that portal. The section of the Social Housing (Regulation) Act 2023 was not opened on legislation.gov.uk. The page says the Act empowered the Ombudsman to issue a code and to monitor compliance.
- [Ofgem, Guidance on submitting domestic customer complaints data](https://www.ofgem.gov.uk/sites/default/files/2025-11/Guidance%20on%20submitting%20domestic%20customer%20complaints%20data.pdf) (publication date 4 November 2025). It says monthly and quarterly complaint information is required by an enduring request for information pursuant to Standard Licence Condition 5, and that completed templates must be sent to the address named in the guidance. Table 1 lists categories B5 to B22. Paragraph 4.9 says item B23 is the sum of B5 to B22 and must equal complaints received. Paragraph 5.15 describes the per-100,000 and, below 100,000 accounts, per-10,000 indicators. Standard Licence Conditions 5 and 32 were not opened. The Excel templates were not opened.
- [The Gas and Electricity (Consumer Complaints Handling Standards) Regulations 2008, regulation 2](https://www.legislation.gov.uk/uksi/2008/1898/regulation/2). Defines "complaint", "consumer complaint", "resolved complaint", and "working day". No known outstanding effects are listed.
- [The same Regulations, regulation 11](https://www.legislation.gov.uk/uksi/2008/1898/regulation/11). A licensed supplier must publish annually a consumer complaints report containing the items in regulation 11(2).
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). A last-updated date was not in the text retrieved.

Not opened, and not applied:

- The DISP complaints-return rule and form.
- The text of Standard Licence Conditions 5 and 32.
- The Ofgem Excel templates attached to the guidance.
- The Social Housing (Regulation) Act 2023 on legislation.gov.uk.
- The billing overview and the standard-harness licensing article linked from the harness comparison table.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
