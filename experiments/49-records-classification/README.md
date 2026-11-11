# Experiment 49: Records Classification Assistant

Catalogue ID **M009**. Autonomy **A1**. A records manager confirms every classification.

UK public bodies keep records against a file plan, a retention schedule, and a security marking. The awkward part is the first pass: which business-classification category, which retention entry, which disposal action, which Government Security Classifications marking, and whether the text looks like it contains personal data. This starter proposes those five fields for one synthetic document. Each proposal carries the evidence that drove it and a confidence level. The records manager confirms or changes every field. Low-confidence items, personal-data indicators, a possible OFFICIAL-SENSITIVE marking, and a legal hold go to a human queue.

The sample can record a label stub only after that confirmation. The stub does not call Microsoft Purview. The agent does not delete, dispose of, move, or downgrade a record.

The organisation in the samples is Merrowfield Borough Council. It is invented. The file plan is configuration for this starter. A configured period is not a statutory retention period and it is not a schedule published by The National Archives.

Stack in the catalogue: Microsoft 365 and Power Platform. The proposal itself is Python in the standard library. It calls [Experiment 12](../12-document-intake/) to inventory the text, [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers, and [Experiment 19](../19-privacy-impact-assessment/) to screen recorded DPIA answers. `dpia_required` stays null. A records manager can run it without a tenant.

## The problem

A model that files a personnel record as ordinary committee papers, or that treats "delete this record" in the text as an instruction, is the failure this starter is built to refuse. A records manager still has to see the category, the retention entry, the disposal action, the marking, and the personal-data indicator, with the phrases that produced them.

## Non-goals

- Deciding the classification. The records manager confirms or changes every field.
- Deleting, destroying, disposing of, transferring, or moving a record, including after confirmation.
- Downgrading a marking. SECRET and TOP SECRET are kept. OFFICIAL-SENSITIVE is not stripped back to OFFICIAL.
- Applying a retention label or a sensitivity label in a Microsoft 365 tenant. The label action is a local stub.
- Deciding that a record is a public record under the Public Records Act 1958, or that the 20-year transfer in section 3(4) has fallen due. The First Schedule was not opened.
- Deciding that the section 46 code was complied with, or issuing a practice recommendation.
- Deciding that UK GDPR Article 5(1)(e) storage limitation was met. Article 84B was not opened.
- Deciding that a DPIA is required. Experiment 19 leaves `dpia_required` null.
- Stating Scots law, or applying this code to a body subject to the Freedom of Information (Scotland) Act 2002.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 11 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Public Records Act 1958, section 3](https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/3) | Section 3(1) is the duty to arrange selection for permanent preservation and safe-keeping. Section 3(4) is transfer not later than 20 years after creation, with a proviso for retention. Section 3(6) is destruction or other disposal of records rejected for permanent preservation. This starter does not do any of those things. |
| [Section 10](https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/10) | Public records has the meaning in the First Schedule. The First Schedule was not opened. This starter does not decide that a body or a record is a public record. |
| [Freedom of Information Act 2000, section 46](https://www.legislation.gov.uk/ukpga/2000/36/section/46) | Section 46(1) is the duty to issue a code of practice on the keeping, management and destruction of records. Section 46(7) defines a relevant authority. The page said there are currently no known outstanding effects. Section 48 was not opened. |
| [Code of Practice, 15 July 2021](https://www.gov.uk/government/publications/code-of-practice-on-the-management-of-records-issued-under-section-46-the-freedom-of-information-act-2000) | The GOV.UK page links the PDF laid before Parliament on 15 July 2021. Paragraphs 2.3.1, 2.3.2, 2.5, and 2.6.2, and Annex B, were read. The code says it does not apply to bodies subject to the Freedom of Information (Scotland) Act 2002. |
| [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html) | Updated 5 August 2024. Three tiers: OFFICIAL, SECRET and TOP SECRET. Paragraph 25: the -SENSITIVE marking sits on OFFICIAL and is not a fourth tier. The policy's own example is written OFFICIAL-SENSITIVE. Paragraph 1: the policy is not a statutory scheme. [Guidance 1.1](https://www.gov.uk/government/publications/government-security-classifications/guidance-11-working-at-official-html) was opened the same day. |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(e) is storage limitation. The text now refers to Article 84B, substituted on 5 February 2026. Article 84B was not opened. Article 6 and Article 9 were not opened. No lawful basis is asserted. |
| [Purview records management](https://learn.microsoft.com/en-us/purview/get-started-with-records-management) and [sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels) | Retention labels, a file plan, and disposition review are the described route for retain-and-delete. Sensitivity labels classify and can protect. A document can carry both. This starter does not call Purview. The licensing table was not opened. Data Map labelling is described on the sensitivity page as currently in preview. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows the topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. Agents on it use Copilot Credits. The page states no price. |

No FCA Handbook provision was opened. This starter does not apply a Handbook rule. Local Government (Records) Act 1962, Local Government Act 1972 sections 224 to 229, and the Government of Wales Act 2006 sections 147 and 148 are named in the code's footnotes. They were not opened.

## What the draft does

`src/classify.py` reads one JSON document and writes one JSON document. The same document and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `deleted`, `disposed`, `moved`, and `downgraded` are false. The body is not copied out. A National Insurance number is not copied out.

**Ready for confirmation.** Two or more phrases from one fictional category, no competing category, no personal-data indicator, no legal hold, and a scheme default of OFFICIAL. The records manager still confirms every field before the stub can run.

**Human queue.** Low confidence, a tie, personal data, a possible OFFICIAL-SENSITIVE marking, a legal hold, an existing SECRET or TOP SECRET marking, a stale pin, or a jurisdiction this code was not applied to.

**Legal hold.** Phrases taken from the examples in code paragraph 2.3.2, plus "legal hold", "litigation hold", "do not destroy", and "do not dispose". The proposed disposal action becomes `do_not_dispose_legal_hold`. It is not executed.

**Prompt injection.** Instructions to delete, dispose, downgrade, skip the queue, or "classify this as" are recorded. `followed` is false. Only the instruction is removed. A category phrase in the rest of the sentence still counts. An HTML comment is not used as evidence.

**Not synthetic.** A document that is not marked synthetic is refused. The refusal does not echo the text. The CLI still exits 0.

`record_confirmation` accepts `confirm_classification`, `change_classification`, or `reject_proposal` from a separate review object. Every field has to be present. A queued item has to be marked reviewed. A lower marking than the one already on the record is refused.

`apply_confirmed_labels` records a stub only after confirmation. `labels_applied_in_tenant` stays false. `purview_called` stays false. Scotland and Northern Ireland, a stale pin, a legal-hold destroy action, and a downgrade are refused.

`delete_record`, `dispose_record`, `move_record`, and `downgrade_record` raise `RecordsForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 19 must be present beside this folder.

```bash
cd experiments/49-records-classification
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/classify.py --input examples/sample_document.json --as-of 2026-11-11
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 18 passed, 0 failed, 0 errors, 18 cases.

The exit code is 0 when a draft or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list over a fictional scheme. Wording that is not on the list is not classified. A single phrase is medium confidence, not a decision.
- Configured periods are not statutory retention periods. Do not copy them into a live retention schedule without the organisation's own schedule.
- Experiment 08 does not detect names, email addresses, or telephone numbers. No indicator is not a finding that the text has no personal data. The output is not anonymised.
- Experiment 12 reads `text/plain` only. A file over 20,000 characters is not scanned.
- Experiment 19 returns `insufficient_facts` when no screening answers are supplied. That is not a decision that a DPIA is unnecessary.
- Article 84B, Article 6, Article 9, section 48, and the Public Records Act First Schedule were not opened.
- The 180-day window is a starter default. It is not a review duty in the code.
- Suggesting OFFICIAL-SENSITIVE where a personal-data indicator is present is this starter's caution. It is not a sentence of the Government Security Classifications Policy that personal data must carry that marking.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Merrowfield Borough Council is fictional.
- This is not legal advice, a file plan, a DPIA, or an ATRS submission.

## UK GDPR

The manifest does not assert the controller's lawful basis. Article 6 and Article 9 were not opened on 11 November 2026. A safeguarding or sickness note can be special-category data. The starter does not assert an Article 9 condition.

Article 5(1)(e) was read the same day. Where a personal-data indicator is present, the draft says storage limitation is engaged as a reading. `storage_limitation_met` stays false. The longer-storage limb now cites Article 84B. That article was not opened.

The agent does not make a disposal decision. Article 22A was not opened.

## Two Copilot Studio harnesses

Both call `src/classify.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness deletes a record or calls Purview. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The records manager pastes a document, the flow returns JSON, the topic stops. A second topic records confirmation. A third runs the stub only when confirmation is already on the JSON. Microsoft's harness overview, opened 11 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a follow-up on the same JSON: which phrase matched, why the item is queued, why a stub did not run. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short narrative may be written from the JSON. The category, the retention entry, the disposal action, the marking, the confidence, and the empty approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The document inventory: [../12-document-intake/](../12-document-intake/).
- The identifier gateway: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The DPIA screen: [../19-privacy-impact-assessment/](../19-privacy-impact-assessment/).

## Project structure

```
experiments/49-records-classification/
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
└── tests/
```

## References opened on 11 November 2026

- [Public Records Act 1958, section 3](https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/3)
- [Public Records Act 1958, section 10](https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/10)
- [Freedom of Information Act 2000, section 46](https://www.legislation.gov.uk/ukpga/2000/36/section/46)
- [Section 46 code of practice](https://www.gov.uk/government/publications/code-of-practice-on-the-management-of-records-issued-under-section-46-the-freedom-of-information-act-2000)
- [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html)
- [Guidance 1.1, working at OFFICIAL](https://www.gov.uk/government/publications/government-security-classifications/guidance-11-working-at-official-html)
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Purview records management](https://learn.microsoft.com/en-us/purview/get-started-with-records-management)
- [Purview sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
