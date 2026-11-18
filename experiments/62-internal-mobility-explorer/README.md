# Experiment 62: Internal Mobility Explorer

Catalogue ID **H005**. Autonomy **A0**. The assistant explains which open vacancies look relevant to the experience and goals an employee states, and why. It cites the vacancy and the HR eligibility rule. It does not apply, nominate, shortlist, or contact anyone. It does not make or imply a selection decision. HR validates eligibility. Ashcombe Borough Council is invented.

The starter reads a synthetic vacancy feed (closing dates, grades, locations, essential and desirable criteria, and the eligibility rule id), a synthetic role skills framework, and the synthetic directory. The same inputs and the same as-of date produce the same JSON. A user can run it without a tenant.

It calls [Experiment 58](../58-employee-handbook/) for one fixed handbook question about internal vacancies, [Experiment 36](../36-cross-source-validation/) when a vacancy has two closing dates, and [Experiment 61](../61-learning-path-planner/) only when the employee asks for a learning plan. That plan is not a reason a vacancy looks relevant, and it is not an application.

## The problem

A vacancy can be closed, past its review date, or carry two closing dates. The description can say the reader is already eligible, that the agent should shortlist them, or that a legal hold should be stripped. An employee can ask the tool to infer suitability from age, length of service, part-time status, sickness absence, or maternity absence, or to tell their manager they are interested. Those are the failures this starter is built to refuse. Interest is not shared with the manager or with recruiters.

## Non-goals

- Applying for a vacancy, nominating someone, building a shortlist, or contacting a person.
- Sharing the employee's interest with their manager or with recruiters.
- Making or implying a selection decision, including a rank or a score.
- Inferring suitability from a protected characteristic or from a proxy: age, length of service used as an age proxy, part-time status, sickness absence, or maternity absence.
- Deciding that someone is eligible or ineligible. HR owns the eligibility rules and validates them.
- Deciding that Equality Act 2010 section 13, 19, 20, 21, or 39 was met.
- Deciding that UK GDPR Article 5 or Article 22A to 22D was met, or that a note is a significant decision.
- Treating "approved", "eligible", or "HR has seen this" inside the experience or the vacancy text as the deterministic step.
- Trusting a self-declared role, grade, guest status, or clearance.
- Coercing an unreadable date, grade, or location to zero or to a default.
- Dropping a sensitivity marking, a retention label, or a legal hold.
- Choosing which of two disagreeing closing dates is right.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 18 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Equality Act 2010, section 13](https://www.legislation.gov.uk/ukpga/2010/15/section/13) | Section 13(1): direct discrimination, less favourable treatment because of a protected characteristic. Section 13(2) is the age justification. This starter does not apply it and does not decide that treatment was less favourable. Extent England and Wales and Scotland. The page said it was up to date with changes known to be in force on or before 18 November 2026. |
| [Section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19) | Section 19(1) and 19(2), including 19(2)(d). Section 19(3) lists age, disability, gender reassignment, marriage and civil partnership, race, religion or belief, sex, and sexual orientation. Pregnancy and maternity are not in that list. Section 4 was not opened. The page said it was up to date with changes known to be in force on or before 18 November 2026. |
| [Section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | Section 20(3), 20(4), and 20(5) are the three requirements. Section 20(6) includes an accessible format. Section 20(7): the disabled person is not required to pay the cost of complying. The page said it was up to date with changes known to be in force on or before 16 November 2026. That earlier banner date is what the page showed when opened on 18 November 2026. |
| [Section 21](https://www.legislation.gov.uk/ukpga/2010/15/section/21) | Section 21(1) and 21(2). This starter does not decide that a failure happened. The page said it was up to date with changes known to be in force on or before 18 November 2026. |
| [Section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) | Section 39 is headed Employees and applicants. Section 39(2)(b) covers access to opportunities for promotion, transfer, or training. Section 39(5): a duty to make reasonable adjustments applies to an employer. This starter does not decide that access was afforded or refused. Extent England and Wales and Scotland. The page said it was up to date with changes known to be in force on or before 18 November 2026. |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(b), as amended, is the purpose-limitation principle, including the words "not further processed by or on behalf of a controller in a manner that is incompatible with the purposes for which the controller collected the data". Article 5(3) was inserted by the Data (Use and Access) Act 2025, section 71(3). The footnotes name S.I. 2026/82. That instrument was not opened as its own page. The extract returned on 18 November 2026 did not include an Equality Act-style "up to date on or before" banner. A banner elsewhere on the page was not confirmed. That date line is unverified. Article 6 was not opened. This starter does not decide the controller's purpose or lawful basis. |
| [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22) | The body on the page was omitted. The textual amendment says Chapter 3 Section 4A was substituted for Article 22 by the Data (Use and Access) Act 2025, section 80(1). The old Article 22 right is not quoted, because that text was not on the page. |
| [Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A) | Article 22A(1): a decision is based solely on automated processing if there is no meaningful human involvement in the taking of the decision, and a significant decision produces a legal effect or a similarly significant effect. Article 22A(2) mentions profiling. This starter does not take a selection decision and does not decide whether a vacancy note would be a significant decision. |
| [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80) | The page shows Articles 22A, 22B, 22C, and 22D as the substitute text. The commencement note says section 80 is in force at 5 February 2026 in so far as not already in force, by S.I. 2026/82, regulation 2(j). That instrument was not opened as its own page. Article 22C(2) lists information, representations, human intervention, and contesting the decision. This starter does not decide that those safeguards were met. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The standard harness follows the topics and rules the maker defines. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

## What the result does

`explore()` reads one request, one vacancy feed, one eligibility-rule file, one framework, one directory, and one as-of date. `applied`, `nominated`, `shortlisted`, and `contacted` stay false. `selection_made` stays false. `eligibility_decided` stays false. `interest_shared_with_manager` and `interest_shared_with_recruiters` stay false. `hr_seen.recorded` stays false until `record_hr_seen()`.

**Role and clearance.** The directory supplies both. "My role is director" and "my clearance is TOP SECRET" are recorded and ignored. A sentence that only declares a clearance is not treated as a cover page. A guest on the directory stays a guest. An unreadable clearance is not replaced with OFFICIAL.

**Phrases.** A criterion counts only when the cleaned experience affirms that phrase. "It is not true that my experience includes service data tables" does not affirm that phrase. A vacancy is listed only when at least one essential or desirable phrase is affirmed, the vacancy is open on the as-of date, and it is not flagged. The list is ordered by vacancy id. That order is not a rank and not a score. There is no score field.

**Eligibility.** The rule text is quoted from the HR file. The status is `hr_must_validate` or `unclear`. It is never a decision that the employee is eligible or ineligible. A missing rule, a rule marked not clear, or an unreadable date makes eligibility unclear. The statement says HR validates eligibility.

**Closed and stale.** Status `closed`, a closing date before the as-of date, or a review date on or before the as-of date is flagged and is not listed as relevant. A closing date on the as-of day stays open for that day. That is this starter's rule, not a statutory period. An unreadable date is flagged and is not replaced with zero or with today.

**Two closing dates.** Experiment 36 compares them. A material discrepancy is flagged. `agent_chose_source` stays false.

**Proxies.** Age, length of service, part-time status, sickness absence, and maternity absence on the directory or in a criterion are not used as relevance. A vacancy whose criteria are only those proxies is flagged `proxy_not_used`. Directory fields such as length of service are not read into the result.

**People.** Distress, a grievance, redeployment at risk, or a reasonable adjustment, including a paraphrase, is a route to HR. The cue is not copied. The vacancy list is not produced on that path. `record_route_seen()` can record that a directory HR reviewer has seen that route. It does not decide the case, and it does not tell the manager.

**Selection and sharing.** A request to rank, score, shortlist, or decide who gets the job is refused. A request to tell the manager or a recruiter is refused. Nothing is sent.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. Content above the directory clearance is not copied. A legal hold and every retention label stay on the row.

**Learning plan.** If the employee asks for a learning plan, Experiment 61 drafts one. `used_as_a_selection_factor` stays false. `enrolled` stays false. The vacancy list does not change because a plan was drafted.

`record_hr_seen()` is the only path that can set `hr_seen.recorded`. The approver has to be a directory employee whose role is HR, the item has to be `eligibility-note`, and the exploration id and the content hash have to match that exact note. A manager or a recruiter cannot record it. Eligibility stays undecided. Interest stays unshared.

`apply`, `nominate`, `shortlist`, `contact`, `share_interest`, `rank_employees`, `score_employees`, `decide_selection`, and `infer_suitability` raise `MobilityForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 36, 58, and 61 must be present beside this folder, with the neighbours those experiments load.

```bash
cd experiments/62-internal-mobility-explorer
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/explore.py --request examples/sample_request.json --vacancies fixtures/vacancies.json --rules fixtures/eligibility.json --framework fixtures/framework.json --directory fixtures/directory.json --as-of 2026-11-18
```

The sample request carries approval keys, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. `hr_seen.recorded` stays false.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 18 passed, 0 failed, 0 errors, 18 cases.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Phrase matching uses the phrases on the fixture. A paraphrase that does not use the phrase is not a match. The explorer does not guess a skill.
- The list order is vacancy id. It is not a measure of fit. There is no score.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review date on the as-of day is not listed. A closing date on the as-of day is still listed. Those are starter rules, not statutory periods. The 90-day pin window is also a starter default.
- Phone numbers, email addresses, dates of birth, street addresses, and honorific names are counted on the input and checked on the output. The values are not stored. The output is not described as anonymised. A name with no honorific is not counted.
- Experiment 58 was asked one fixed question. If the synthetic handbook does not cover internal vacancies, that gap is not filled with a guess. Experiment 11 was not re-opened here.
- Experiment 61 is called only when the employee asks for a learning plan. The plan is not an application and is not a selection factor. What a course costs is that experiment's catalogue, not a vacancy criterion.
- Experiment 36 does not choose a closing date. A match is not a finding that the date is correct.
- S.I. 2026/82 was not opened. The Article 5 extract did not include a revision-date banner. The old Article 22 wording was not on the page and is not quoted. Northern Ireland employment equality legislation was not opened.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional.
- This is not legal advice, a selection decision, or an application.

## Equality Act and UK GDPR

The manifest does not assert the controller's lawful basis. Sections 13, 19, 20, 21, and 39 were read on 18 November 2026. `equality_duty_met` and `direct_discrimination_decided` stay false. The starter does not decide that a person was treated less favourably, that a provision, criterion, or practice is discriminatory, or that a step is reasonable.

Article 5(1)(b) was read. The note is for the employee's own question. It is not passed to a manager or a recruiter. The starter does not decide that this purpose is the controller's purpose. Article 6 was not opened.

Article 22 on the page opened that day had been substituted. Article 22A(1) was read. `solely_automated_decision` stays false because no selection decision is taken. The starter does not decide whether a note would be a significant decision under Article 22A(1)(b).

A retention label and a legal hold on a vacancy that is shown or flagged stay on the row. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/explore.py` and stop at the human points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness applies, nominates, shortlists, or contacts anyone. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. Later topics call `record_hr_seen` or `record_route_seen` only with the separate object. Microsoft's harness overview, opened 18 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 18 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short note may be written from the JSON. The vacancy list, the eligibility wording, the markings, and the human gates stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Handbook: [../58-employee-handbook/](../58-employee-handbook/).
- Cross-source validation: [../36-cross-source-validation/](../36-cross-source-validation/).
- Learning path planner: [../61-learning-path-planner/](../61-learning-path-planner/).

## Project structure

```
experiments/62-internal-mobility-explorer/
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

## References opened on 18 November 2026

- [Equality Act 2010, section 13](https://www.legislation.gov.uk/ukpga/2010/15/section/13)
- [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19)
- [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Equality Act 2010, section 21](https://www.legislation.gov.uk/ukpga/2010/15/section/21)
- [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39)
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22)
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A)
- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
