# Experiment 52: Word Proposal Drafting Agent

Catalogue ID **M004**. A structured bid draft in Word for one synthetic invitation.

UK public-sector bids ask a supplier to answer every requirement from material the organisation has already approved: past answers, capability statements, and placeholders for price. The failure mode is a draft that invents a certificate, a customer, a statistic, or a price, or that marks a requirement as met because the invitation said so, or that submits itself. This starter drafts. The author accepts the complete draft before it is used anywhere. It does not submit.

**Autonomy A1.** `draft_proposal()` leaves `human_approval` null. `record_acceptance()` can record that the author has accepted the draft for their own later use. `submitted` and `used_anywhere` stay false. The agent has no portal tool, no mail tool, and no Microsoft Graph call.

Stack in the catalogue: Microsoft 365 and Work IQ. The draft itself is Python in the standard library. It calls `screen_tone()` and `screen_plain_english()` in [Experiment 43](../43-response-drafting/), `line_applicability()` in [Experiment 09](../09-casework-correspondence-draft/) because Experiment 43 uses that gate, `score_claim()` and `passage_currency()` in [Experiment 29](../29-groundedness-evaluation/), and `normalise_value()` and `classify_values()` in [Experiment 36](../36-cross-source-validation/). An author can run it without a tenant.

The bidder in the samples is Northmere Digital Services. The buyer is Aldergate Borough Council. The case-study name Riverton District Council appears only inside an approved library entry, which says it is not a real customer. All three are invented.

## The problem

A bid assistant that fills a gap with a plausible certificate number, copies a price the buyer typed into the question, or submits because the invitation said "submit the bid now" is the failure this starter is built to refuse. The useful narrow job is: map every requirement to an approved quote or to a gap, name the source, withhold figures, and stop for the author.

## Non-goals

- Submitting a bid, sending an email, or uploading a file to a portal or to Microsoft Graph. A recorded acceptance is not a submission.
- Inventing a capability, a case study, a customer, an accreditation, a statistic, or a price.
- Marking a requirement as met when no approved source is cited, or when Experiment 29 does not call the quote supported.
- Copying the requirement text into the answer, including a price the buyer wrote in the question.
- Writing an assessment summary. Section 50 of the Procurement Act 2023 is the contracting authority's duty. This starter is a supplier draft.
- Deciding that PPN 026, PPN 002, PPN 014, or UK GDPR was met, or that a Cyber Essentials certificate is held.
- Choosing which social-value edition applies. On 12 November 2026 the 1 January 2027 date in PPN 026 is still ahead.
- Using a real bidder, a real buyer, a real certificate number, or a real price. Northmere is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 12 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Procurement Act 2023, section 21](https://www.legislation.gov.uk/ukpga/2023/54/section/21) | Section 21(1) is the duty to publish a tender notice for an open procedure, or, for a competitive flexible procedure, to invite a request to participate or the first or only tender. Section 21(5) and (6) say the notice or associated tender documents must contain enough detail, and the requirements must be sufficiently clear and specific and must not break section 56. Section 56 was not opened. In force at 24 February 2025. |
| [Section 50](https://www.legislation.gov.uk/ukpga/2023/54/section/50) | Section 50(1) is the contract award notice. Section 50(3) and (4) require an assessment summary, before that notice, for a contract awarded under section 19. This starter does not write one. Section 19 was not opened beyond that cross-reference. |
| [PPN 026](https://www.gov.uk/government/publications/ppn-026-the-social-value-model/ppn-026-the-social-value-model-html) and the [guide](https://www.gov.uk/government/publications/ppn-026-the-social-value-model/guidance-on-using-ppn-026-the-social-value-model-html) | Updated 28 October 2026. Paragraph 10 of the note says in-scope organisations should apply it to procurements commenced on or after 1 January 2027, when a tender notice is published. The guide says it replaces earlier social-value PPNs and points back to PPN 002 or PPN 06/20 for some frameworks. This starter does not apply a weighting and does not decide which edition applies. |
| [PPN 002](https://www.gov.uk/government/publications/ppn-002-taking-account-of-social-value-in-the-award-of-contracts/ppn-002-taking-account-of-social-value-in-the-award-of-central-government-contracts-html) | Updated 5 March 2025 and still listed on the collection page opened the same day. Paragraph 11 says social-value commitments made in the procurement must be reflected in the contract. A commitment in this draft is flagged for the author. It is not treated as a contract term. |
| [PPN 014](https://www.gov.uk/government/publications/ppn-014-cyber-essentials-scheme/ppn-014-cyber-essentials-scheme-html) and the [NCSC overview](https://www.ncsc.gov.uk/cyberessentials/overview) | PPN 014 paragraph 14 names Cyber Essentials or Cyber Essentials Plus for the higher-risk characteristics in paragraph 12, and paragraph 20 says the scheme must not be applied as a blanket. The NCSC page lists five controls. This starter does not decide that a certificate is held, and it does not copy a price from that page into a bid. |
| [PPN 020](https://www.gov.uk/government/publications/ppn-020-guidance-on-data-protection-legislation/ppn-020-guidance-on-data-protection-legislation-html) | Paragraph 9 says the primary UK legal framework is the UK GDPR. Paragraph 10 says the Data Protection Act 2018 has to be read with it. Articles 6, 9, and 28 were not opened. No lawful basis is asserted. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It can create and edit Word files and uses Copilot Credits. The page states no price. |
| [Word.Body.insertParagraph](https://learn.microsoft.com/en-us/javascript/api/word/word.body?view=word-js-preview) and [Graph upload](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0) | The Word JavaScript API inserts a paragraph in an add-in. Graph `PUT` content uploads a file of up to 250 MB as a driveItem. Neither is called. The local `.docx` is Office Open XML written with the standard library. |
| [Current Channel release notes](https://learn.microsoft.com/en-us/OfficeUpdates/current-channel) | Version 2602 (Build 19725.20172), dated 10 March on that page, describes Agent mode in Word as a chat that can draft and rewrite. A dedicated Copilot in Word product overview was not opened. |

The [procurement policy notes collection](https://www.gov.uk/government/collections/procurement-policy-notes) was opened the same day. Its header said last updated 5 August 2026, while the list included later items, including PPN 026 dated 28 October 2026. The item pages are the ones this starter relies on.

The Procurement Regulations 2024, including regulation 31, were not opened. The Public Services (Social Value) Act 2012 was not opened. PPN 06/20 was not opened beyond the cross-reference on the PPN 026 guide.

## What the starter does

`src/proposal.py` reads one JSON pack and writes one JSON document. The same pack and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. The requirement text is not copied into the draft.

**Met.** One approved capability entry matches an affirmative sentence, Experiment 09's gate says it may be cited, Experiment 43's tone screen passes, and Experiment 29's `score_claim` returns `supported`. The body is quoted. The entry has no price, commitment, accreditation, case study, or digit. The sample service-desk line is this case.

**Cited, for the author.** The quote is supported, and the entry is a commitment, an accreditation, a case study, or anything else with a sensitive cue. Cyber Essentials, social value, and data protection in the sample library are this case. `requirement_met` stays false.

**Price.** Placeholders may carry an amount for Experiment 36 to compare. The amount is not copied. Two day-rate placeholders that normalise to different pence are a material discrepancy. Two half-day placeholders that normalise to the same pence are an immaterial difference, and the figure is still withheld.

**Gap.** No approved phrase matches. The fixed gap sentence does not answer the requirement. A number in the question, including a launch code, is not copied. Anything unrecognised goes to the author.

**Negation.** A sentence that contains a negation, and a following sentence that is only "no", is not used as a request to cite a source. "It is not true that…" does not mark a capability as held.

**Prompt injection.** A sentence that tells the agent to ignore the library, invent a case study, or submit the bid is recorded. `followed` is false. A later instruction does not remove an earlier affirmative sentence, and it does not submit.

**Stale data.** On the review date, Experiment 09's gate does not cite the entry. A review stamp outside Experiment 29's window is not quoted. If the as-of date is more than 180 days after 12 November 2026, no entry is quoted. Equal to 180 days is still inside the window. The 180-day figure is a starter default, not a review duty.

**Word.** `src/word_draft.py` writes the same matrix as a `.docx`. It does not call the Word JavaScript API and it does not call Graph.

**Synthetic only.** A pack that is not marked synthetic, or whose proposal id is not `SYN-BID-` plus four digits, is refused. The refusal does not echo the text.

`record_acceptance` accepts `author_accept_complete_draft`, `author_request_revision`, or `reject_draft` from a separate review object. Acceptance is refused when a row, a gap, or an author check has not been acknowledged. It still does not submit. `submit_bid`, `send_proposal`, `upload_to_portal`, and `invent_claim` raise `ProposalForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 09, 29, 36, and 43 must be present beside this folder. This experiment does not carry a second copy of them.

```bash
cd experiments/52-word-proposal-drafting
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/proposal.py --input examples/sample_invitation.json --as-of 2026-11-12 --docx /tmp/northmere-draft.docx
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. Each case is counted once. A live Microsoft Foundry run has not been done. The checked-in report is 22 passed, 0 failed, 0 errors, 22 cases.

The exit code is 0 when a draft or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a phrase list. Wording that is not on the list becomes a gap. That is deliberate. A gap is not a failed run.
- A sentence that contains a negation is dropped in full. "Describe the service desk, not the ISO line" does not cite the service desk. Split the ask into its own sentence. A negation the list does not catch can still cite an approved line. The author still has to accept the draft, and nothing is submitted.
- Experiment 29 treats a quote as unsupported when a content word is not in the source. A fair paraphrase of an approved line would be refused. The draft therefore quotes the library body.
- The 180-day window and Experiment 29's review-stamp window are starter defaults. They are not a duty in the Procurement Act 2023.
- Experiment 43's plain-English screen is recorded. It is not a reading-age certificate and it is not a finding that a bid answer was clear.
- Price amounts exist in the library file so Experiment 36 can compare them. They are not written into the JSON answer or the Word file. A bidder's real price book is not in this repository.
- The local `.docx` is a simple document. It is not a styled template and it is not a portal upload.
- A dedicated Copilot in Word product overview, the Graph upload-session page, and Microsoft 365 Copilot licensing were not opened. Agent mode in Word is described only as far as the Current Channel note that was read.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. The overview says that. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Northmere Digital Services, Aldergate Borough Council, and Riverton District Council are fictional.
- This is not legal advice, a tender submission, a social-value commitment, or an ATRS submission.

## UK public-sector bids

Section 21 is why a supplier is answering a notice and its associated documents. This starter does not check that a notice was published, and it does not decide that the requirements were clear enough under section 21(6).

Section 50 is the authority's assessment summary. `assessment_summary_produced` stays false.

PPN 026 and PPN 002 both appear on the collection page that was opened. The starter quotes an approved social-value line or it states a gap. It does not invent a jobs figure, and it does not set `ppn_026_met`.

PPN 014 and the NCSC page are why a Cyber Essentials question is common. The sample answer says the certificate number is not stored here. `cyber_essentials_held` stays null.

PPN 020 is why a data-protection question is common. The sample answer says this starter does not decide a lawful basis.

## Two Copilot Studio harnesses

Both call `src/proposal.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness submits. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The author pastes a pack, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 12 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a follow-up on the same JSON: which source was refused, which figure was withheld, and why an acceptance did not submit. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The overview says this harness can create a Word file. This starter's Word file is still the local core. The skill does not tell the harness to upload it.

## Microsoft Foundry

Optional. A short narrative may be written from the JSON. The quotes, the gaps, the matrix, and the empty approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The response screens this experiment calls: [../43-response-drafting/](../43-response-drafting/).
- The groundedness check: [../29-groundedness-evaluation/](../29-groundedness-evaluation/).
- The currency comparison: [../36-cross-source-validation/](../36-cross-source-validation/).

## Project structure

```
experiments/52-word-proposal-drafting/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── schema/
├── fixtures/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 12 November 2026

- [Procurement Act 2023, section 21](https://www.legislation.gov.uk/ukpga/2023/54/section/21)
- [Procurement Act 2023, section 50](https://www.legislation.gov.uk/ukpga/2023/54/section/50)
- [PPN 026: The Social Value Model](https://www.gov.uk/government/publications/ppn-026-the-social-value-model/ppn-026-the-social-value-model-html)
- [Guidance on using PPN 026](https://www.gov.uk/government/publications/ppn-026-the-social-value-model/guidance-on-using-ppn-026-the-social-value-model-html)
- [PPN 002](https://www.gov.uk/government/publications/ppn-002-taking-account-of-social-value-in-the-award-of-contracts/ppn-002-taking-account-of-social-value-in-the-award-of-central-government-contracts-html)
- [PPN 014: Cyber essentials scheme](https://www.gov.uk/government/publications/ppn-014-cyber-essentials-scheme/ppn-014-cyber-essentials-scheme-html)
- [NCSC Cyber Essentials overview](https://www.ncsc.gov.uk/cyberessentials/overview)
- [PPN 020: Guidance on data protection legislation](https://www.gov.uk/government/publications/ppn-020-guidance-on-data-protection-legislation/ppn-020-guidance-on-data-protection-legislation-html)
- [Procurement policy notes](https://www.gov.uk/government/collections/procurement-policy-notes)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Word.Body.insertParagraph](https://learn.microsoft.com/en-us/javascript/api/word/word.body?view=word-js-preview)
- [Upload small files, Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0)
- [Office Current Channel release notes](https://learn.microsoft.com/en-us/OfficeUpdates/current-channel)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
