# Experiment 66: Workforce Skills Inventory

Catalogue ID **H010**. Autonomy **A0**. The assistant proposes skills from evidence an employee supplied for this purpose. Each proposal has a cited snippet, a confidence band, and the state `needs employee confirmation`. The employee can reject or correct any skill. HR validates only after that step. The agent does not write to an HR system, rate performance, or feed pay, promotion, redundancy, or disciplinary decisions. Ashcombe Borough Council is invented.

The starter reads synthetic CV extracts, completed learning records, and project summaries, a synthetic example skills framework, and the synthetic directory. The same inputs and the same as-of date produce the same JSON. A user can run it without a tenant.

The framework is an example with a SFIA-style skill-and-level shape so the fields are visible. It is not SFIA. SFIA is a licensed framework. The organisation must license any framework it uses and must review these phrases.

It calls [Experiment 08](../08-uk-pii-redaction-gateway/) on a cited sentence, [Experiment 61](../61-learning-path-planner/) only after the employee has confirmed a skill, and [Experiment 62](../62-internal-mobility-explorer/) only from experience the employee states. Inferred skills are not passed to Experiment 62, and a learning plan is not a rating.

## The problem

A CV can say the employee has already confirmed every skill, that a legal hold should be stripped, or that the tool should rate performance. A pack can include a keystroke log, a sickness sentence, or a request to infer skill from age. A team count of two people names them if it is published. Those are the failures this starter is built to refuse.

## Non-goals

- Writing to an HR system, a payroll system, or a performance form.
- Rating performance, scoring a person, or setting a numeric level as a rating.
- Feeding pay, promotion, redundancy selection, or a disciplinary decision.
- Inferring a skill from a protected characteristic or from health data.
- Profiling a person from data they did not supply for this purpose, including monitoring, a mailbox, an absence record, or a manager's notes.
- Deciding that UK GDPR Article 5, 6, 13, 21, or 22A was met, or that Data Protection Act 2018 section 10 was met.
- Treating "confirmed" or "HR has validated" inside the evidence as the deterministic step.
- Trusting a self-declared role or clearance.
- Coercing an unreadable date, consent flag, or threshold to zero or to a default.
- Dropping a sensitivity marking, a retention label, or a legal hold.
- Describing the output, or the team view, as anonymised.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 19 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(a) to (f), Article 5(2), and Article 5(3). Article 5(1)(b) includes the purpose-limitation words as amended. Article 5(1)(e) refers to Article 84B. Article 84B was not opened. Article 5(3): processing is not lawful by virtue only of being compatible with the purposes for which the personal data was collected. The extract did not include an up-to-date banner. That date line is unverified. |
| [Article 6](https://www.legislation.gov.uk/eur/2016/679/article/6) | Article 6(1)(a) to (f), including point (ea). Points (ea) and (f) shall not apply to processing carried out by public authorities in the performance of their tasks. Article 6(4) is shown as omitted. This starter does not choose a basis. No Equality Act-style stamp was in the extract. That date line is unverified. |
| [Article 13](https://www.legislation.gov.uk/eur/2016/679/article/13) | Article 13(1) and 13(2), including 13(2)(b) and 13(2)(f). Article 13(2)(f) refers to safeguards under Article 22C. Article 22C was not opened. A missing or unreadable field is flagged. `article_13_met` stays false. No banner was in the extract. That date line is unverified. |
| [Article 21](https://www.legislation.gov.uk/eur/2016/679/article/21) | Article 21(1) and 21(4) were read. An objection stops the inventory. Compelling grounds are not decided. Paragraphs 2 and 3 were not in the extract and are not quoted. No banner was in the extract. That date line is unverified. |
| [Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22) | The body was omitted. Chapter 3 Section 4A was substituted by the Data (Use and Access) Act 2025, section 80(1). The old Article 22 wording is not quoted. S.I. 2026/82 was not opened. |
| [Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A) | Article 22A(1) and 22A(2). This starter does not take a decision and does not decide that a skills note would be a significant decision. Articles 22B, 22C, and 22D were not opened. No banner was in the extract. That date line is unverified. |
| [Data Protection Act 2018, section 4](https://www.legislation.gov.uk/ukpga/2018/12/section/4) | Section 4(1) and 4(2). The page said it was up to date with all changes known to be in force on or before 18 November 2026. Article 2 of the UK GDPR was not opened. |
| [Section 10](https://www.legislation.gov.uk/ukpga/2018/12/section/10) | Section 10(1) refers to Article 9(1) as the prohibition on special-category data. Article 9 was not opened as its own page. Schedule 1 was not opened. The page said it was up to date on or before 19 November 2026. This starter does not decide that a condition was met. |
| [ICO, monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/data-protection-and-monitoring-workers/) | The page says you must be clear about the purpose and must document it, and that you should not monitor workers just in case. It says a purpose can change only if the new purpose is compatible, you get consent, or you have a clear legal obligation or function. The ethernet example says that information should not be reused for performance management without a new lawful basis. The page says the guidance is under review because of the Data (Use and Access) Act. |
| [ICO, lawfulness in AI](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-lawfulness-in-ai/) | The chapter says the controller must identify a purpose and a lawful basis for each operation, and that the controller decides the basis. It says an inference is likely to be special category data if you can or intend to infer it, or intend to treat someone differently because of it. Latest update on the page: 28 October 2024. The page says the guidance is under review because of the Data (Use and Access) Act. |
| [What is Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview) | Fabric is described as a SaaS analytics platform with OneLake. Fabric IQ is marked preview. Microsoft 365 and Microsoft Foundry integration are named. This starter does not deploy a Fabric item. No last-updated line was in the extract. That date is unverified. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The page does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. No price is stated. |

## What the result does

`propose_inventory()` reads one request, one evidence pack, one framework, one directory, one transparency record, and one as-of date. `wrote_to_hr_system`, `performance_rated`, `pay_decision`, `promotion_decision`, `redundancy_decision`, and `disciplinary_decision` stay false. Every proposal starts as `needs_employee_confirmation`.

**Role and clearance.** The directory supplies both. "My role is director" and "my clearance is TOP SECRET" are recorded and ignored. A sentence that only declares a clearance is not treated as a cover page.

**Phrases.** A skill counts only when a cleaned sentence affirms a framework phrase. "It is not true that this evidence includes depot forklift" does not affirm that phrase. The band is `high` when two evidence items affirm it, `medium` when one learning record or project summary does, and `low` when one CV extract does. The band is not a performance rating. There is no score.

**Purpose.** Only items marked `supplied_for` `skills_inventory`, with consent recorded as the boolean true, from `employee_supplied`, are used. Monitoring, a mailbox, an absence record, manager notes, and a health record are skipped. A string `"true"` is not coerced to true.

**People.** Distress, a grievance, or a safeguarding cue, including a paraphrase, is a route to HR. The cue is not copied. An objection stops the inventory. A request to use the inventory for redundancy, performance, pay, promotion, or discipline is out of scope and is not turned into proposals. "Do not use this for performance management" is not that request.

**Confirmation.** `record_employee_decision()` is the only path that can confirm, reject, or correct a skill. The approver has to be that employee on the directory. The inventory id, the inventory hash, and the skill hash have to match. A correction is bound to the hash of the correction text. `record_hr_validation()` accepts HR only, and only after the employee has confirmed or corrected. It does not write to an HR system. The employee can still reject afterwards. A manager cannot take either step.

**Team view.** Counts are shown only when the cell and its complement are both at or above the threshold. Otherwise the count is null. References are not listed. The default threshold is 5 when the framework omits it. That is a starter default, not a statutory number. An unreadable threshold is not replaced with zero. The view is not described as anonymised. The ICO anonymisation guidance was not opened.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. Content above the directory clearance is not copied. A legal hold and every retention label stay on the row.

**Dates.** The as-of date is the date the question is about. An unreadable date is flagged and is not replaced with today. A question date after the section 4 stamp (18 November 2026) is not treated as covered by that pin. `may_be_relied_on` stays false.

`write_hr`, `rate_performance`, `set_pay`, `decide_promotion`, `select_for_redundancy`, `decide_discipline`, `infer_from_protected`, and `profile_unsupplied` raise `InventoryForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 61, and 62 must be present beside this folder, with the neighbours those experiments load.

```bash
cd experiments/66-workforce-skills-inventory
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/inventory.py --request examples/sample_request.json --evidence fixtures/evidence.json --framework fixtures/framework.json --directory fixtures/directory.json --transparency fixtures/transparency.json --as-of 2026-11-18
```

The sample request carries approval keys, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. Every skill stays `needs_employee_confirmation`.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added into the case total. The checked-in report is 16 passed, 0 failed, 0 errors, 16 cases. Each paraphrase category in that file is 24 of 24, and the negated variants are not counted as hits.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The bands use the example phrases. A paraphrase that does not use the phrase is not a skill. The inventory does not guess a skill.
- The paraphrase patterns are an example list. A sentence that uses none of them is not caught. Recall on the checked set is a smoke figure, not a measure of every way a person might write.
- The threshold of 5, and the complement rule, are starter controls. They are not a statutory test and they are not anonymisation. A viewer who already knows the team can still try to infer. The ICO anonymisation guidance was not opened.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- A review date before the as-of date is stale. A review date on the as-of day is still used. That is a starter rule, not a statutory period. The 180-day pin window is a starter default.
- Phone numbers, email addresses, dates of birth, street addresses, and honorific names are masked on a cited sentence. The values are not stored. The output is not described as anonymised. A name with no honorific is not counted by that mask. Experiment 08 covers UK identifiers it already detects.
- Experiment 61 is called only for a skill the employee has confirmed. Nobody is enrolled. Experiment 62 is not given the inferred skills. What either neighbour returns is that experiment's result, not a rating.
- Article 84B, Article 2, Article 9, Article 22B, Article 22C, Article 22D, and Schedule 1 were not opened. Article 21 paragraphs 2 and 3 were not in the extract. S.I. 2026/82 was not opened. The UK GDPR article extracts had no revision-date banner. Those points are unverified where the table says so.
- The ICO pages say they are under review because of the Data (Use and Access) Act.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, and Application Insights were not opened. Treat that product behaviour as unverified.
- Fabric is described from the overview only. No lakehouse, notebook, or report is deployed. Fabric IQ is preview on that page. A connector was not tested.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional.
- This is not legal advice, a performance rating, or an HR record.

## UK GDPR and the Data Protection Act 2018

The manifest does not assert the controller's lawful basis. Article 6 was read. `article_6_basis_decided` stays false. Article 5(3) was read: staying inside a purpose is not, by itself, a finding of lawfulness.

Article 13 fields are compared with the record the caller supplies. A false or unreadable field is flagged. The inventory is not marked as meeting Article 13.

Article 21(1) was read. An objection stops processing for this inventory. The starter does not decide compelling legitimate grounds.

Article 22 was substituted on the page that was opened. Article 22A(1) was read. `solely_automated_decision` stays false because no decision is taken. The starter does not decide whether a skills note would be a significant decision.

Section 4(2) says Part 2 supplements the UK GDPR and must be read with it. Section 10(1) points at Article 9(1). This starter does not decide a Schedule 1 condition. The ICO chapter on AI inferences was read. A request to infer a special-category detail is refused rather than drawn.

A retention label and a legal hold on a proposal or a withheld item stay on the row. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/inventory.py` and stop at the human points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness writes to an HR system. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. Later topics call the decision functions only with the separate object. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 19 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Fabric and Microsoft Foundry

The catalogue row is Fabric and Microsoft 365. What the Fabric overview actually says, and what this starter does not deploy, is in [docs/fabric.md](docs/fabric.md). Microsoft Foundry is optional, for a short note from the JSON. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed. The retired product name is not used.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Learning path: [../61-learning-path-planner/](../61-learning-path-planner/).
- Internal mobility: [../62-internal-mobility-explorer/](../62-internal-mobility-explorer/).

## Project structure

```
experiments/66-workforce-skills-inventory/
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

## References opened on 19 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [UK GDPR Article 6](https://www.legislation.gov.uk/eur/2016/679/article/6)
- [UK GDPR Article 13](https://www.legislation.gov.uk/eur/2016/679/article/13)
- [UK GDPR Article 21](https://www.legislation.gov.uk/eur/2016/679/article/21)
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22)
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A)
- [Data Protection Act 2018, section 4](https://www.legislation.gov.uk/ukpga/2018/12/section/4)
- [Data Protection Act 2018, section 10](https://www.legislation.gov.uk/ukpga/2018/12/section/10)
- [ICO, monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/data-protection-and-monitoring-workers/)
- [ICO, how do we ensure lawfulness in AI?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-lawfulness-in-ai/)
- [What is Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
