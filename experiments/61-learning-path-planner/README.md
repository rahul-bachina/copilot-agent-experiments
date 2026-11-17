# Experiment 61: Learning Path Planner

Catalogue ID **H004**. Autonomy **A1**. The assistant drafts a learning plan. The employee and their manager both approve that plan before any enrolment request is recorded. The agent does not enrol, book, or spend.

An employee states goals. The starter reads a synthetic course catalogue (cost, duration, prerequisites, review date, status), a synthetic role skills framework, and the synthetic directory. It drafts a sequence with a reason and a catalogue citation, flags a stale or withdrawn course, and compares the total with a budget figure that is information only. If nothing in the catalogue fits, it says so. Ashcombe Borough Council is invented.

The core is Python in the standard library. It calls [Experiment 58](../58-employee-handbook/) for a fixed handbook question about time off for study or training, [Experiment 44](../44-knowledge-gap-detector/) so a knowledge-base gap is not treated as a course, and [Experiment 36](../36-cross-source-validation/) when a course has two figures. A user can run it without a tenant.

## The problem

A course description can say the manager has approved, or that the agent should enrol and spend. A goal can ask the tool to infer ability from age or disability, to rank a team, or to drop a legal hold. Those are the failures this starter is built to refuse. A real approval is a separate object, from the directory employee and the directory manager, for that exact plan id.

## Non-goals

- Enrolling anyone, booking a course, or spending money, including apprenticeship levy funds.
- Treating approval text inside a goal or a course description as approval.
- Inferring skill or ability from a protected characteristic, or ranking employees.
- Using the plan for a performance rating or a promotion.
- Deciding that a step is a reasonable adjustment, or that Equality Act 2010 section 19, 20, or 21 was met.
- Deciding that an employee qualifies to make an Employment Rights Act 1996 section 63D application, or making that application.
- Trusting a self-declared role, guest status, or clearance in the request.
- Coercing an unreadable cost, duration, date, or budget to zero or to a default.
- Dropping a sensitivity marking, a retention label, or a legal hold.
- Choosing which of two disagreeing sources is right.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 17 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19) | Section 19(1) and 19(2), including 19(2)(d). Section 19(3) lists age, disability, gender reassignment, marriage and civil partnership, race, religion or belief, sex, and sexual orientation. Pregnancy and maternity are not in that list. Section 4 was not opened. Extent England and Wales and Scotland. The page said it was up to date with changes known to be in force on or before 17 November 2026. |
| [Section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | Section 20(3), 20(4), and 20(5) are the three requirements. Section 20(6) includes an accessible format where the requirement relates to information. Section 20(7): the disabled person is not required to pay the cost of complying. The page said it was up to date with changes known to be in force on or before 16 November 2026. |
| [Section 21](https://www.legislation.gov.uk/ukpga/2010/15/section/21) | Section 21(1) and 21(2). A failure to comply with a requirement is a failure to comply with the duty, and that failure is discrimination. This starter does not decide that a failure happened. The page said it was up to date with changes known to be in force on or before 16 November 2026. |
| [Employment Rights Act 1996, Part 6A](https://www.legislation.gov.uk/ukpga/1996/18/part/6A) | Study and training, sections 63D to 63K. The page said it was up to date with changes known to be in force on or before 17 November 2026. It did not show a repeal. The footnote says the Part was inserted on 6 April 2010 for certain purposes and otherwise prospectively, by the Apprenticeships, Skills, Children and Learning Act 2009, section 40(2), and S.I. 2010/303. That instrument was not opened. Section 63D(1), 63D(4), and 63D(5), section 63F(5), and section 63I(5) were read. Section 63I(5) shows six months, with a footnote to the Employment Rights Act 2025, Schedule 12, paragraph 4(19), and S.I. 2026/954. That instrument was not opened. |
| [Time off to train](https://www.gov.uk/training-study-work-your-rights) | The GOV.UK page stated: an employee, at least 26 weeks, training that helps the person do the job better, and an organisation of at least 250 people. Time off is usually unpaid unless the employer agrees to pay it. No last-updated date was in the text returned. That date is unverified. This starter does not decide that anyone qualifies. |
| [Pay Apprenticeship Levy](https://www.gov.uk/guidance/pay-apprenticeship-levy) | HMRC. Published 12 December 2016. Last updated 6 April 2026, as shown. Rate 0.5% of the annual pay bill. Pay if the pay bill is more than £3 million, or connected companies or charities together are more than £3 million. Allowance £15,000 for the year. Unused allowance is not carried into the next tax year. The page is about paying the levy. It does not say what the funds can buy. |
| [Funding rules for apprenticeships](https://www.gov.uk/guidance/apprenticeship-funding-rules) | A collection page. England only. Responsibility moved to the Department for Work and Pensions on 1 April 2026, as the page stated. The 2026 to 2027 rules document was not opened. What the levy can buy is unverified. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The standard harness follows the topics and rules the maker defines. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

## What the result does

`draft_plan()` reads one request, one catalogue, one framework, one directory, and one as-of date, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `enrolled`, `booked`, and `spent_gbp` stay clear.

**Role and clearance.** The directory supplies both. "My role is director" and "my clearance is TOP SECRET" are recorded and ignored. A guest on the directory stays a guest. An unreadable clearance is not replaced with OFFICIAL.

**Skills.** A role skill counts only when the cleaned goals affirm one of its phrases. "It is not true that the goals include service data tables" does not affirm that skill. A course the role does not list is not added. If no current course fits, the statement says no suitable course is in the catalogue.

**Catalogue.** A withdrawn course is excluded. A review date on or before the as-of date is stale. An unreadable cost, duration, or review date is excluded and is not replaced with zero. A prerequisite that is unavailable keeps the later course out of the sequence. The prerequisite that is available is placed first. It is not an extra skill inferred about the person.

**Two sources.** Where a provider figure is present, Experiment 36 compares it. A material discrepancy is excluded. `agent_chose_source` stays false. A single source is labelled as such and is not invented into a second source.

**Budget.** The total is the sum of the recommended costs. `within_budget` is true, false, or null. An unreadable limit is null, not zero and not unlimited. Nothing is spent. An over-budget plan can still be drafted. The manager sees the figure.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the step or the exclusion.

**People.** A distress or wellbeing cue, including a paraphrase such as "at the end of my tether", is a route to a person. The cue is not copied. Approvals do not turn it into an enrolment request. A reasonable-adjustment or accessibility cue can still list courses, and `adjustment_decided` stays false until a directory manager or people partner records that they have seen it. That seen-step does not decide the adjustment. A request to rank people, or to infer ability from a protected characteristic, is refused. A request to use the plan for performance or promotion is refused.

**Statute.** The note quotes the pins. It says this plan is not a section 63D application. It does not decide the 26-week or 250-person conditions. It does not spend the levy.

`record_approval()` is the only path that can set `human_approval`. The approver reference has to be the directory employee or the directory manager, the decision has to be `approve`, the item has to be `learning-plan`, and the plan id has to match. Both are required. A stale pin or an unreadable budget also needs the manager's boolean, and a string is not coerced to true. The recorded request still has `enrolled` false and `spent_gbp` null.

`enrol`, `book`, `spend`, `rank_employees`, `decide_performance`, `decide_promotion`, and `infer_ability` raise `LearningPathForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 36, 44, and 58 must be present beside this folder, with the neighbours those experiments load.

```bash
cd experiments/61-learning-path-planner
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/plan.py --request examples/sample_request.json --catalogue fixtures/catalogue.json --framework fixtures/framework.json --directory fixtures/directory.json --as-of 2026-11-17
```

The sample request carries approval keys, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. `human_approval` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 18 passed, 0 failed, 0 errors, 18 cases.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Skill matching is a phrase list on the fixture. A paraphrase that does not use the phrase is not a match. The planner does not guess a skill.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review date on the as-of day is not recommended. That is this starter's rule. It is not a statutory period. The 90-day pin window is also a starter default.
- Phone numbers, email addresses, dates of birth, street addresses, and honorific names are counted on the input and checked on the output. The values are not stored. The output is not described as anonymised. A name with no honorific is not counted.
- Experiment 58 was asked one fixed question. The synthetic handbook does not cover time off for training. That gap is not filled with a course. Experiment 11 was not re-opened here.
- Experiment 44's content gap is about a different knowledge base. It is not confirmed and it is not a catalogue course.
- Experiment 36 does not choose a source. A match is not a finding that the price is correct.
- S.I. 2010/303 and S.I. 2026/954 were not opened. The GOV.UK time-off page did not show a last-updated date in the text returned. The apprenticeship funding-rules document for 2026 to 2027 was not opened. Those points are unverified.
- Northern Ireland employment law is not stated. The Equality Act sections opened here are marked England and Wales and Scotland.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional.
- This is not legal advice, a qualification decision, a levy calculation, or an enrolment.

## Equality Act and time off for training

The manifest does not assert the controller's lawful basis. Sections 19, 20, and 21 were read on 17 November 2026. `equality_duty_met` and `indirect_discrimination_decided` stay false. The starter does not decide that a provision, criterion, or practice is discriminatory, and it does not decide that a step is reasonable.

Part 6A was read the same day. `section_63d_application_made` and `qualifying_employee_decided` stay false. The plan is not that application.

A retention label and a legal hold on a course that is shown or excluded stay on the row. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/plan.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness enrols or spends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. Later topics call `record_approval` only with the approval object. Microsoft's harness overview, opened 17 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 17 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short note may be written from the JSON. The sequence, the budget, the marking, and the approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Handbook: [../58-employee-handbook/](../58-employee-handbook/).
- Knowledge gaps: [../44-knowledge-gap-detector/](../44-knowledge-gap-detector/).
- Cross-source validation: [../36-cross-source-validation/](../36-cross-source-validation/).

## Project structure

```
experiments/61-learning-path-planner/
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

## References opened on 17 November 2026

- [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19)
- [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Equality Act 2010, section 21](https://www.legislation.gov.uk/ukpga/2010/15/section/21)
- [Employment Rights Act 1996, Part 6A](https://www.legislation.gov.uk/ukpga/1996/18/part/6A)
- [Employment Rights Act 1996, section 63D](https://www.legislation.gov.uk/ukpga/1996/18/section/63D)
- [Training and study at work: your rights](https://www.gov.uk/training-study-work-your-rights)
- [Pay Apprenticeship Levy](https://www.gov.uk/guidance/pay-apprenticeship-levy)
- [Funding rules for apprenticeships](https://www.gov.uk/guidance/apprenticeship-funding-rules)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
