# Experiment 11: Employment Rights Act 2025 HR assistant

Catalogue ID **UK03**. Related to, and kept separate from, the generic handbook and case-intake rows H001 and H009. This starter is the harassment-prevention and commencement checklist for a UK employer.

Small employers, charities, and multi-site organisations have a preventative duty now, and a stronger one appointed for 30 October 2026. The awkward part is showing what was considered, without a piece of software deciding that the employer took "all reasonable steps", and without it touching a disciplinary case.

**Autonomy A1.** The agent reads one synthetic employer pack and returns a draft: which pinned duties are in force on the as-of date, which preparatory items the pack records, a policy skeleton with blank headings, and, if supplied, a handbook quotation or an anonymised triage note. An HR lead decides. The agent does not decide compliance, discipline, or dismissal. It does not change a record or send anything.

Stack in the catalogue: Copilot Studio, Microsoft 365, and Power Platform. The checklist itself is Python in the standard library, so an HR lead can run it without a tenant.

The employer in the samples is Northwharf Community Kitchen CIC, an invented organisation. Workers are "Worker A" and "a visitor". There are no real people.

## The problem

Section 40A of the Equality Act 2010 already requires an employer to take reasonable steps to prevent sexual harassment of employees in the course of their employment. From 30 October 2026 the Employment Rights Act 2025 inserts the word "all", and it inserts a duty not to permit third-party harassment where the employer failed to take all reasonable steps. A power to specify steps by regulations is appointed for the same day. No such regulations were opened for this starter.

An HR lead still has to see which sentence is in force on the day they are reading the pack, which evidence the organisation has actually recorded, and which decisions stay with a person. This starter prepares that reading. It signposts Acas. It is not Acas, and it is not a solicitor.

## Non-goals

- Deciding that the employer has taken, or failed to take, reasonable steps or all reasonable steps.
- Deciding that harassment occurred, or that the employer permitted a third party to harass someone.
- A disciplinary outcome, a warning, a suspension, or a dismissal. That includes whether a dismissal was fair, unfair, or automatically unfair.
- Deciding that a disclosure was a protected disclosure.
- Calculating a tribunal time limit, or identifying the relevant date in SI 2026/954 regulation 4.
- Applying the six-month qualifying period, or the removal of the compensatory-award cap, to a named person. The core does not decide an effective date of termination.
- Publishing or amending a policy, a handbook, or an intranet page.
- Changing a personnel, grievance, or case record.
- Sending a message to a worker, an alleged harasser, Acas, a tribunal, a trade union, the Equality and Human Rights Commission, or anyone else.
- Treating the Acas preparation examples as regulations under the new Equality Act 2010 section 40B. No specifying regulations were opened.
- Inventing a closed list of steps that every employer must take. Acas says the steps depend on the organisation. This core does not decide which steps are reasonable for a given size or sector.
- Northern Ireland employment law. The sections read are marked E+W+S.
- The rest of the Employment Rights Act 2025: fire and rehire, zero-hours contracts, flexible working, bereavement leave, non-disclosure agreements, and the trade union provisions. Some of those dates appear only on the GOV.UK timetable.
- Giving legal advice.

## What was opened

Opened on 27 October 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Equality Act 2010 section 40A](https://www.legislation.gov.uk/ukpga/2010/15/section/40A) | Inserted on 26 October 2024. Subsection (1): the employer must take reasonable steps to prevent sexual harassment of employees in the course of their employment. The changes list shows section 20 of the 2025 Act as not yet applied to the text. |
| [Employment Rights Act 2025 section 20](https://www.legislation.gov.uk/ukpga/2025/36/section/20) | Inserts "all" before "reasonable steps" in section 40A(1). The page was marked prospective. Commencement is SI 2026/1065 regulation 3(a): 30 October 2026. |
| [Section 21](https://www.legislation.gov.uk/ukpga/2025/36/section/21) | Inserts Equality Act 2010 section 40(1A) to (1C): an employer must not permit a third party to harass an employee, and "permits" requires both harassment in the course of employment and a failure to take all reasonable steps. Prospective. SI 2026/1065 regulation 3(b): 30 October 2026. Extent E+W+S. |
| [Section 22](https://www.legislation.gov.uk/ukpga/2025/36/section/22) | Inserts section 40B, a power to specify steps that are to be regarded as reasonable. Prospective. SI 2026/1065 regulation 3(c): 30 October 2026. The power is not a list. No regulations made under it were opened. |
| [SI 2026/1065 regulation 3](https://www.legislation.gov.uk/uksi/2026/1065/regulation/3/made) | Appoints sections 20, 21, and 22 for 30 October 2026, with other provisions this starter does not apply. |
| [Section 23](https://www.legislation.gov.uk/ukpga/2025/36/section/23) | Inserts sexual harassment into the qualifying disclosures in the Employment Rights Act 1996. The page says it is in force on 6 April 2026 by SI 2026/323 regulation 3. That SI was not opened as its own page. |
| [Section 25](https://www.legislation.gov.uk/ukpga/2025/36/section/25) | In the Employment Rights Act 1996, substitutes "six months" for "two years" in section 108, and omits section 124 (limit of compensatory award). Not in force at Royal Assent. The remainder is appointed for 1 January 2027. |
| [SI 2026/559 regulation 3](https://www.legislation.gov.uk/uksi/2026/559/regulation/3/made) | Section 25, so far as not already in force, and Schedule 3, on 1 January 2027, subject to the transitional provision in regulation 4. This core does not apply regulation 4 to a person. |
| [Section 152](https://www.legislation.gov.uk/ukpga/2025/36/section/152) | Schedule 12 increases employment tribunal time limits in Great Britain from three months to six months. In force on 1 October 2026 by SI 2026/954 regulation 3, subject to regulation 4. |
| [SI 2026/954](https://www.legislation.gov.uk/uksi/2026/954/body/made) | Regulation 4: the Schedule 12 amendments do not apply where the relevant date is before 1 October 2026. This core does not identify that date and does not count six months. |
| [GOV.UK timeline](https://www.gov.uk/government/publications/implementing-the-plan-to-make-work-pay-and-employment-rights-act/plan-to-make-work-pay-and-employment-rights-act-timeline-update), updated 22 October 2026 | Confirms the 30 October 2026 harassment measures, the 1 October 2026 tribunal limits, and the 1 January 2027 unfair-dismissal changes. It says the Scottish breach-of-contract time limit changes on 9 November 2026. That instrument was not opened. It says future dates remain subject to parliamentary processes. |
| [Acas: sexual harassment](https://www.acas.org.uk/employment-rights-act-2025/harassment-law-changes/sexual-harassment), last updated 26 August 2026 | Preparation examples: review policies, consider a standalone policy, more than one reporting route, suitable training, and prevention rather than only a response. Not a statutory list. The page's worked examples are not applied to any pack. |

The GOV.UK timetable also lists non-disclosure-agreement regulations in September 2027, and other 2027 measures. Those instruments were not opened. The core records the non-disclosure-agreement line as timetable-only and does not score it.

## What the checklist does

`src/review.py` reads one JSON pack and writes one JSON document. The same pack and the same as-of date produce the same JSON. `hr_decision` is null. `compliance_conclusion` is null. `disciplinary_decision` is null. `actions_taken` is empty.

**In force is a date comparison, not a finding about the employer.** On 27 October 2026, section 40A still says "reasonable steps". Sections 20 to 22 are appointed for 30 October 2026 and are not described as in force before that day. On and after 30 October 2026 the wording on the preventative duty is "all reasonable steps", and section 21 is in force. The core still does not say the employer met or missed it.

**Section 40B.** On and after 30 October 2026 the power to specify steps is in force. `specified_steps_regulations_made` stays false. Acas examples are prompts. `absence_is_not_a_breach` is true on every prompt. A pack in which every prompt is "evidenced" is still not a compliance conclusion.

**Evidence the employer recorded.** The pack says, for each prompt, `evidenced`, `not_evidenced`, or `not_supplied`. The core does not read a handbook and infer that a step was reasonable. A policy review date older than the threshold, default 365 days, is flagged stale. Equal to the threshold is not stale. A stale policy is not a breach.

**Handbook question.** If the question asks for a claim, a disciplinary outcome, a time limit, or a compliance conclusion, the draft refuses and quotes nothing. Otherwise it quotes an excerpt only when the policy owner has already approved that excerpt and the topic matches. No match is "not in the approved pack". The agent does not answer from the Act.

**Anonymised report.** The route is always HR review. The note is not closed. Language about sexual harassment, or about a visitor, customer, or contractor, is a flag for the reader, not a finding. A report that is not marked anonymised is refused, and the refusal does not echo the narrative.

**Unfair dismissal and time limits.** The draft states whether section 25 and section 152 are in force on the as-of date, and stops. It does not count months and it does not look up a person's start date.

**Northern Ireland.** The duties are not applied. The draft says this starter does not state Northern Ireland law.

**Stale pin.** If `last_verified` is older than the threshold, default 90 days, every source row is stale and `rules_current` is false. The core does not refresh itself from the web.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/11-era-2025-hr-assistant
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/review.py --input examples/sample_pack.json --as-of 2026-10-27
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A pack that is not marked synthetic is refused. The exit code is 0 when a draft is produced, including when evidence is missing. Missing evidence is not a failed run, and it is not a finding of breach. A refusal exits 2.

## Limitations

- A date comparison is not a finding that the employer has complied or breached.
- On 27 October 2026, sections 20 to 22 were still marked prospective on legislation.gov.uk. The commencement instrument appoints 30 October 2026. A reader who treats the Acas page, or this readme, as if that duty had already started is ahead of the instrument.
- The Scottish contract-claim date of 9 November 2026 is a sentence on the GOV.UK timeline. The instrument was not opened. The core does not apply it.
- SI 2026/323 was not opened as its own page. The commencement line on section 23 was.
- The monetary amount of the compensatory-award cap was not opened. The core says section 124 is omitted from 1 January 2027, and it does not state a figure.
- Acas illustrations of employers who did or did not take all reasonable steps are not used. They are fact-specific and they are not the statute.
- The core does not decide which steps are reasonable for an organisation of a particular size. Recording `worker_count` does not lower the duty.
- Sexual harassment material can be special-category data. This starter refuses a report that is not marked anonymised, and it does not assert an Article 9 basis. A production use needs the employer's own assessment.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. Licence coverage beyond the harness overview is unverified. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a statement of any employer's compliance.

## Two Copilot Studio harnesses

Both call `src/review.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness publishes a policy, writes a record, sends a message, or decides a case. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The HR lead pastes a pack, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/11-era-2025-hr-assistant/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── review.py
│   ├── sources.py
│   └── injection.py
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 27 October 2026

- [Equality Act 2010, section 40A](https://www.legislation.gov.uk/ukpga/2010/15/section/40A)
- [Employment Rights Act 2025, sections 20, 21, 22, 23, 25, and 152](https://www.legislation.gov.uk/ukpga/2025/36/contents)
- [SI 2026/1065, regulation 3](https://www.legislation.gov.uk/uksi/2026/1065/regulation/3/made)
- [SI 2026/559, regulation 3](https://www.legislation.gov.uk/uksi/2026/559/regulation/3/made)
- [SI 2026/954](https://www.legislation.gov.uk/uksi/2026/954/body/made)
- [Plan to Make Work Pay and Employment Rights Act: timeline update](https://www.gov.uk/government/publications/implementing-the-plan-to-make-work-pay-and-employment-rights-act/plan-to-make-work-pay-and-employment-rights-act-timeline-update)
- [Acas, sexual harassment law changes](https://www.acas.org.uk/employment-rights-act-2025/harassment-law-changes/sexual-harassment)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
