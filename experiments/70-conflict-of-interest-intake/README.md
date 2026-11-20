# Experiment 70: Conflict-of-Interest Intake

Catalogue ID **L005**. Autonomy **A1**. The assistant drafts a structured declaration and writes it to a synthetic staging store only after the declarant confirms that exact draft. The ethics or procurement team decides every disposition and mitigation. The agent does not decide whether a conflict exists, and it does not clear, exclude, or approve anyone, and it does not send.

A member of staff pastes one synthetic declaration. The core reads a pinned supplier list, a pinned procurement register, and a pinned directory. It drafts interest type, parties, any procurement or contract named, dates, and whether the interest is financial or non-financial. It asks for what is missing. It highlights a potential link to a procurement that is live on the question date, for the ethics team. A link is not a finding that a conflict exists. Ashcombe Borough Council and the supplier names are invented.

The core is Python in the standard library. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers, [Experiment 12](../12-document-intake/) so the file is not confirmed and no purpose is confirmed, and the keyword and injection helpers in [Experiment 32](../32-employee-case-intake/). It does not call Experiment 32 `draft_case()`, because a declaration is not an HR case. A user can run it without a tenant. The catalogue row names Copilot Studio and Power Platform first. This folder still ships both Copilot Studio harnesses. The Microsoft Foundry option is a note.

## The problem

A declaration can say, in its own words, that the ethics team has already approved it, that the author is the ethics officer, and that a supplier should be excluded. It can deny an interest in one sentence and state one in the next. It can name a relative or a political opinion that the record does not need. Those are the failures this starter is built to separate. A real confirm step is a separate object, from the directory member of staff, for that exact declaration hash.

## Non-goals

- Deciding that a conflict of interest exists, or that it does not.
- Preparing a conflicts assessment under Procurement Act 2023 section 83.
- Treating a supplier as an excluded supplier under section 82(4).
- Clearing, excluding, or approving a person or a supplier.
- Sending the declaration, to the supplier or to anyone else.
- Treating approval text inside the declaration as the confirm step.
- Trusting a self-declared role, guest status, or clearance.
- Trusting a supplier list, register, directory, or criteria object pasted into the request.
- Copying special-category detail, or a relative's name, into the draft.
- Marking a carve-out or a leading criterion as acceptable, or applying it.
- Coercing an unreadable amount or date to zero or to today.
- Stripping a legal hold or a retention label.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 20 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`. The extracts did not show an "up to date on or before" date. Currency is unverified.

| Source | What this starter takes from it |
| --- | --- |
| [Procurement Act 2023, section 81](https://www.legislation.gov.uk/ukpga/2023/54/section/81) | Section 81(1): "A contracting authority must take all reasonable steps to identify, and keep under review, in relation to a covered procurement any— (a) conflicts of interest, or (b) potential conflicts of interest." Section 81(4), the definition of interest: "“interest” includes a personal, professional or financial interest and may be direct or indirect". In force 24 February 2025. Extent on the page: U.K. No known outstanding effects were stated. This starter does not identify a conflict. |
| [Section 82](https://www.legislation.gov.uk/ukpga/2023/54/section/82) | Section 82(1): "A contracting authority must take all reasonable steps to ensure that a conflict of interest does not put a supplier at an unfair advantage or disadvantage in relation to a covered procurement." Section 82(4) is the duty to treat a supplier as an excluded supplier in the case the section describes. This starter does not do that. Sections 19, 41, and 43 were not opened. |
| [Section 83](https://www.legislation.gov.uk/ukpga/2023/54/section/83) | Section 83(1): "Before publishing a tender or transparency notice in relation to a covered procurement, a contracting authority must prepare a conflicts assessment in relation to the procurement." Section 83(3) says what that assessment must include. This starter does not prepare one. |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(c): "adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed (‘data minimisation’)". Context for the ethics team. Not a finding that the principle was met. Article 6 was not opened. |
| [Article 9](https://www.legislation.gov.uk/eur/2016/679/article/9) | Article 9(1) lists racial or ethnic origin, political opinions, religious or philosophical beliefs, trade union membership, genetic data, biometric data for the purpose of uniquely identifying a natural person, data concerning health, and data concerning a natural person's sex life or sexual orientation. A family relationship is not in that list. Paragraphs 2 to 5 were not applied. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox. The prose says agents on that harness use Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. No "last updated" line was in the extract. That date is unverified. |

## What the result does

`draft_declaration()` reads one request and the question date, compares any caller-supplied list or register with the pinned files, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `staged` stays false. `conflict_exists` stays null. `person_cleared`, `person_excluded`, `person_approved`, `supplier_excluded`, `marked_acceptable`, and `sent` stay false.

**Role and clearance.** The pinned directory supplies both. "My role is ethics officer" and "my clearance is TOP SECRET" are recorded and ignored. A guest stays a guest. An ethics officer is not a staff declarant unless the directory says `staff`.

**Structure.** Interest type, parties as supplier ids, a named procurement id, dates, amounts, and financial or non-financial. A missing field becomes a question. An unreadable date or amount is counted and is not replaced with today or with zero. Two natures, or both direct and indirect, are flagged and not chosen.

**Links.** A supplier named outside a negation is compared with the pinned register. A procurement is a potential link when it is live on the question date. An ended procurement, a future procurement, and a row whose date cannot be read are not called live. `conflict_exists` on the link stays null.

**Negation.** "It is not true that this declaration includes a shareholding" does not count as a shareholding. "It is not true that I have a financial interest in Harbour Lane Catering Ltd" does not link that supplier.

**People.** A distress, whistleblowing, grievance, or Article 9(1) cue, including a paraphrase, is a route to a person. The cue is not copied. The declaration is not a routine draft. A family link keeps a relationship label. The name is not copied. Family is not marked as Article 9.

**Carve-out and bias.** A qualification after an interest, including the word "acceptable", does not mark the draft acceptable. A leading or biased criterion is flagged and not applied.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. "Do not downgrade SECRET" still counts. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**Confirm.** `confirm_declaration()` writes the synthetic store only when the directory member of staff confirms that declaration hash. A string is not coerced to true. Tampered content is rejected. `record_disposition()` then stores the ethics or procurement officer's words and does not apply them.

`decide_conflict`, `clear_person`, `exclude_person`, `exclude_supplier`, `approve_person`, `send`, and `write_production` raise `DeclarationForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 32 must be present beside this folder.

```bash
cd experiments/70-conflict-of-interest-intake
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/declaration.py --request examples/sample_request.json --as-of 2026-11-14
```

The sample request carries approval language, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. `human_approval` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Interest and cue matching is a stem list. A wording that uses none of those stems is not flagged. The smoke report states recall on the fixture sentences. That is not a live rate.
- "Not" within eight words before an interest phrase can hide a match. "It is not true that X includes Y" is the case this rule is built for. Markings use a narrower denial so "do not downgrade SECRET" is still SECRET.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period. Experiment 12's document window is that experiment's rule.
- The small-number threshold is 5. It is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is", a title plus a surname, or "my wife is" plus a name are counted. The values are not stored. A name with none of those patterns is not counted.
- Sections 81 to 83 and Articles 5 and 9 had no currency stamp in the extract opened on 20 November 2026. Those pins are not confirmed. Sections 19, 41, 43, 55, and 80 were not opened. Article 6 was not opened. Article 9(2) is not applied.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council and the supplier names are fictional.
- This is not a conflicts assessment, a decision that a conflict exists, or legal advice.

## Statute

The manifest does not assert the controller's lawful basis. Section 81, section 82, section 83, Article 5(1)(c), and Article 9(1) were read on 20 November 2026 as context for the ethics team. `conflict_exists`, `conflicts_assessment_prepared`, `article_5_met`, and `article_9_condition_met` stay false or null.

A retention label and a legal hold stay on the result. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/declaration.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness decides that a conflict exists. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `confirm_declaration` only with the confirm object. Microsoft's harness overview, opened 20 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. Power Platform is the flow that calls the core. This folder does not ship a solution package.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 20 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says it uses Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The catalogue row L005 names Copilot Studio and Power Platform first. The gates are the same.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The hashes, the links, and the confirm step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Document intake: [../12-document-intake/](../12-document-intake/).
- Employee case intake patterns: [../32-employee-case-intake/](../32-employee-case-intake/).

## Project structure

```
experiments/70-conflict-of-interest-intake/
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
