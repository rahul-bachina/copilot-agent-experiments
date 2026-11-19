# Experiment 67: Contract Clause Review

Catalogue ID **L001**. Autonomy **A0**. The assistant highlights clauses and deviations for a lawyer. The lawyer owns all legal interpretation. The agent does not give legal advice, redline, accept terms, sign, or send.

A lawyer pastes one synthetic contract and points at one synthetic clause playbook. The playbook states a preferred position, a fallback position, and an unacceptable position for limitation of liability, indemnities, data protection and processor terms, termination, governing law, intellectual property, confidentiality, and auto-renewal. The starter quotes the contract sentence, the clause reference, and the playbook position. A clause that is not in the text is `not found`. It is not invented. Ashcombe Borough Council and Northbridge Supplies Ltd are invented.

The core is Python in the standard library. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers, [Experiment 12](../12-document-intake/) so the file is not confirmed and no purpose is confirmed, and the strip-and-signal helpers in [Experiment 27](../27-tool-contract-review/). It does not call Experiment 27 `review()`, because a legal contract is not a tool contract. A user can run it without a tenant. The catalogue row names the GitHub Copilot harness and Azure first. This folder still ships both Copilot Studio harnesses. The Azure option is a Microsoft Foundry note.

## The problem

A contract can say, in its own text, that the lawyer has approved it and that the agent should sign it. It can exclude liability for death in one clause and preserve it in another. It can name two governing laws. It can appoint a processor and leave out parts of UK GDPR Article 28(3). Those are the failures this starter is built to separate. A real seen step is a separate object, from the directory lawyer, for that exact contract hash and that exact deviations hash.

## Non-goals

- Legal advice, a view on enforceability, or a redline.
- Accepting terms, signing, or sending anything, on anyone's behalf.
- Treating approval text inside the contract as approval.
- Deciding that Unfair Contract Terms Act 1977 section 2 or section 11 is satisfied, or that a consumer term is unfair under Consumer Rights Act 2015 Part 2.
- Deciding that a processor contract meets UK GDPR Article 28.
- Marking a term safe.
- Guessing a clause that is not in the text.
- Stripping a legal hold or a retention label.
- Trusting a self-declared role, guest status, or clearance in the contract.
- Coercing an unreadable amount, notice period, audience, date, or role to zero or to a default.
- Choosing which of two conflicting clauses is right.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 19 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [UK GDPR Article 28](https://www.legislation.gov.uk/eur/2016/679/article/28) | Article 28(3), including points (a) to (h), as a presence checklist for a processor contract. The page said there are currently no known outstanding effects for Article 28. It did not show an "up to date on or before" date. The same fetch said revised legislation may not be fully up to date. Currency is unverified. Phrase presence is not compliance. Article 28(8) showed a footnote that a word was substituted on 30 September 2026. The replacement word was not readable in the extract. Article 28(8) is not relied on. |
| [Unfair Contract Terms Act 1977, section 2](https://www.legislation.gov.uk/ukpga/1977/50/section/2) | Section 2(1): a person cannot by reference to any contract term or notice exclude or restrict his liability for death or personal injury resulting from negligence. Section 2(2) is the reasonableness gateway for other loss or damage. Section 2(4): this section does not apply to a term in a consumer contract or to a consumer notice, and points to Consumer Rights Act 2015 sections 62 and 65. Extent on the page: E+W+N.I. The page did not show an "up to date on or before" date. It said there are no known outstanding effects, and that revised legislation may not be fully up to date. Currency is unverified. This starter does not decide that a term is void. |
| [Section 11](https://www.legislation.gov.uk/ukpga/1977/50/section/11) | Section 11(1), the reasonableness test for a contract term. Section 11(4), resources and insurance where liability is restricted to a specified sum. Section 11(5): it is for those claiming that a term or notice satisfies the requirement of reasonableness to show that it does. Extent E+W+N.I. No "up to date on or before" date was on the page. Currency is unverified. The test is not applied. |
| [Consumer Rights Act 2015, Part 2](https://www.legislation.gov.uk/ukpga/2015/15/part/2) | Part 2 is "Unfair terms". The page said it was up to date with all changes known to be in force on or before 18 November 2026. Section 61(1): this Part applies to a contract between a trader and a consumer. Section 62(1) and 62(4) are context only. Section 65(1): a trader cannot by a term of a consumer contract or by a consumer notice exclude or restrict liability for death or personal injury resulting from negligence. This starter does not decide fairness. |
| [Section 61](https://www.legislation.gov.uk/ukpga/2015/15/section/61) | The page stamp was 19 November 2026. |
| [Section 62](https://www.legislation.gov.uk/ukpga/2015/15/section/62) | The page stamp was 19 November 2026. |
| [Section 65](https://www.legislation.gov.uk/ukpga/2015/15/section/65) | The page stamp was 18 November 2026. Section 66 (scope of section 65) was read on the Part 2 page and is not applied. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox. The prose says agents on that harness use Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

Unfair Contract Terms Act 1977 Part II (Scotland) was not opened. Schedule 2 to the 1977 Act was not opened. Consumer Rights Act 2015 Schedule 2 (the indicative list) was not opened.

## What the result does

`review_contract()` reads one request, one playbook, one directory, and one question date, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `terms_accepted`, `signed`, `sent`, and `redline_applied` stay false. `legal_advice` stays false. `legal_score` stays null. `marked_safe` stays false. `article_28_complied` stays false.

**Role and clearance.** The directory supplies both. "My role is lawyer" and "my clearance is TOP SECRET" are recorded and ignored. A guest on the directory stays a guest. An unreadable clearance is not replaced with OFFICIAL. A caller who is not in the directory does not receive quotes.

**Quotes.** A quote is the contract sentence, or the exact words `not found`. It is not a paraphrase. Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are masked in the quote. The result says what was masked. It does not say the quote was anonymised. The contract body is not copied.

**Playbook.** A review-due date on the question date is stale. That is this starter's rule, not a statute. A playbook whose effective date is after the question date is not yet in force. An unreadable amount, notice period, audience, or date is flagged and is not replaced with zero or with a default audience.

**Comparison.** Each of the eight topics is preferred, fallback, unacceptable, not found, ambiguous, conflicting, outside the matched positions, or an incomplete processor checklist. A sentence that does not match a playbook position is routed to the lawyer. Two governing laws are both quoted. Neither is chosen. A heading that is not one of the eight topics is outside the playbook and is routed to the lawyer.

**Negation.** "It is not true that the clause includes a cap" does not count as a cap. "Nothing in this agreement excludes liability for death" does not count as an exclusion of that liability. "Shall not be liable for death" does count as that kind of term, and it is not marked safe.

**Statute.** The note quotes the pins. It says the comparison is not legal advice. A pin with no currency stamp is not confirmed. A pin whose page stamp is earlier than the question date is not confirmed for that date. Today is not used. A business term that excludes liability for death or personal injury is flagged against section 2(1) as context. It is not held to be void. For a consumer contract, section 2(4) is quoted and section 65(1) is the context instead. Section 11 is not applied. Article 28(3) points that are absent are `not found`. They are not filled in.

**People.** A distress, vulnerability, safeguarding, grievance, or disclosure cue, including a paraphrase, is a route to a person. The cue is not copied. The comparison is not a routine review.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**Intake.** Experiment 12 inventories the text. `files_confirmed` and `purpose_confirmed` stay false. Experiment 27 removes forged approval keys and records instruction signals. They are not followed.

`give_legal_advice`, `redline`, `accept_terms`, `sign`, and `send` raise `ContractReviewForbidden`.

`record_lawyer_seen()` records that the directory lawyer has seen the item. The contract hash and the deviations hash have to match. A string is not coerced to true. The record does not accept terms.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 27 must be present beside this folder.

```bash
cd experiments/67-contract-clause-review
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/review.py --request examples/sample_request.json --playbook fixtures/playbook.json --directory fixtures/directory.json --as-of 2026-11-14
```

The sample request carries approval language, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. `human_approval` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Playbook matching is the organisation's own signal list. A wording that uses none of those signals is outside the playbook. It is not reclassified by guesswork.
- Cue and statute-floor matching is a stem list. A paraphrase that uses none of the stems is not flagged. The smoke report states recall on the fixture sentences. That is not a live rate.
- "Not" within eight words before a phrase can hide a match. "It is not true that X includes Y" is the case this rule is built for.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period. Experiment 12's 90-day window is that experiment's rule.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- Article 28, section 2, and section 11 had no currency stamp on the pages opened on 19 November 2026. Those pins are not confirmed. Part II of the 1977 Act was not opened. Schedule 2 of that Act was not opened. Consumer Rights Act 2015 Schedule 2 was not opened. Section 66 is not applied.
- Part 2 of the 2015 Act was stamped 18 November 2026. Section 65 was stamped 18 November 2026. Sections 61 and 62 were stamped 19 November 2026.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council and Northbridge Supplies Ltd are fictional.
- This is not legal advice, a redline, or an acceptance of terms.

## Statute

The manifest does not assert the controller's lawful basis. Article 28(3), section 2, section 11, and Part 2 were read on 19 November 2026 as context for a lawyer. `article_28_complied`, `reasonableness_decided`, `fairness_decided`, and `voidness_decided` stay false.

A retention label and a legal hold stay on the result. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/review.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness accepts terms. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_lawyer_seen` only with the seen object. Microsoft's harness overview, opened 19 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 19 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says it uses Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The catalogue row L001 names this harness first, with Azure. The gates are the same as the standard harness.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The quotes, the hashes, and the seen step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed. The catalogue code AZ is this option. It is not a second legal engine.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Document intake: [../12-document-intake/](../12-document-intake/).
- Tool-contract patterns: [../27-tool-contract-review/](../27-tool-contract-review/).

## Project structure

```
experiments/67-contract-clause-review/
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
