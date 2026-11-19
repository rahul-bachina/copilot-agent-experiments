# Experiment 65: Interview Pack Builder

Catalogue ID **H008**. Autonomy **A1**. The assistant drafts an interview pack. The recruiter approves the questions and the scoring rubric through the deterministic approval step before use. The agent does not contact candidates, schedule interviews, score or rank anyone, or make a hiring decision.

A recruiter pastes one synthetic job description, one synthetic person specification, and points at one synthetic interview guide. The starter drafts a competency or strengths-based question for each essential criterion, a behaviourally anchored rubric, reasonable-adjustment prompts for the invitation, and the guide's note-taking rules for the panel. Ashcombe Borough Council is invented.

The core is Python in the standard library. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) when personal data is pasted in, and [Experiment 64](../64-job-description-quality/) for the example wording list. A user can run it without a tenant. The catalogue row names the GitHub Copilot harness first. This folder still ships both Copilot Studio harnesses.

## The problem

A pack can ask how old someone is, whether they are planning a family, or how many sick days they took, and it can say in its own text that the recruiter has already approved it. It can also carry a right-to-work sentence that should stay, and a SECRET cover page that must not be copied. Those are the failures this starter is built to separate. A real approval is a separate object, from the directory recruiter, for that exact pack hash and that exact questions hash or rubric hash.

## Non-goals

- Contacting a candidate, sending an invitation, or scheduling an interview.
- Scoring a candidate, ranking applicants, or making a hiring decision.
- Treating approval text inside the job description, the specification, or the guide as approval.
- Deciding that Equality Act 2010 section 13, 15, 19, 20, 39, 60, 158, or 159, or Schedule 9 paragraph 1, was met or contravened.
- Deciding that a health question falls within section 60(6).
- Inventing a criterion the person specification does not state.
- Inventing an anchor the guide does not state.
- Checking any person's right to work.
- Stripping a legal hold or a retention label.
- Trusting a self-declared role, guest status, or clearance in the input.
- Coercing an unreadable scale, date, or criterion list to zero or to a default.
- Giving legal advice. The pack is for a person's judgement.
- Autonomy A3. A3 is not permitted in this catalogue.
- Inventing a statistic about biased questions. The probe list is an example the organisation must review.

## What was opened

Opened on 19 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Equality Act 2010, section 13](https://www.legislation.gov.uk/ukpga/2010/15/section/13) | Section 13(1). Extent E+W+S. The page said it was up to date with changes known to be in force on or before 18 November 2026. This starter does not decide that less favourable treatment occurred. |
| [Section 15](https://www.legislation.gov.uk/ukpga/2010/15/section/15) | Section 15(1). A sickness-absence question is routed, not decided. The page stamp was 18 November 2026. |
| [Section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19) | Section 19(1) and 19(2), including 19(2)(d). Section 19(3) lists age, disability, gender reassignment, marriage and civil partnership, race, religion or belief, sex, and sexual orientation. Pregnancy and maternity are not in that list. The page stamp was 18 November 2026. This starter does not apply the test. |
| [Section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | Section 20(7): a person who is subject to the duty is not entitled to require a disabled person to pay A's costs of complying with the duty. Schedule 8 was not opened. The page stamp was 18 November 2026. This starter does not decide that the duty arose. |
| [Section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) | Section 39(1)(a), arrangements for deciding to whom to offer employment. Section 39(5) says a duty to make reasonable adjustments applies to an employer. The page stamp was 18 November 2026. This starter does not decide a contravention. |
| [Section 60](https://www.legislation.gov.uk/ukpga/2010/15/section/60) | Section 60(1). Section 60(6) lists purposes the section does not apply to. Section 60(12) says an assessment includes an interview. Section 60(13) says whether a person has a disability is an aspect of health. This starter does not decide that any purpose is met. The page stamp was 17 November 2026. |
| [Section 158](https://www.legislation.gov.uk/ukpga/2010/15/section/158) | Section 158(2). Section 158(4) says the section does not apply to action within section 159(3). The page stamp was 19 November 2026. This starter does not decide that the section permits the text. |
| [Section 159](https://www.legislation.gov.uk/ukpga/2010/15/section/159) | Section 159(4). The page stamp was 18 November 2026. This starter does not decide that positive action is permitted. |
| [Schedule 9, paragraph 1](https://www.legislation.gov.uk/ukpga/2010/15/schedule/9/paragraph/1) | Paragraph 1(1). The page stamp was 14 November 2026. This starter does not decide that the paragraph is met. |
| [ICO recruitment and selection](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/recruitment-and-selection/) | The page says the consultation on this draft guidance is closed and the final version will be published in due course. It also says the guidance is under review because of the Data (Use and Access) Act. It is not treated as final. |
| [Employment practices code (PDF)](https://ico.org.uk/media2/migrated/1064/the_employment_practices_code.pdf) | Paragraph 1.5.1 and paragraph 1.7.1 were read. The PDF also mentions a subject-access fee of up to £10. That fee is not relied on. Status as current ICO guidance is unverified. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The prose says agents and workflows on the Microsoft Copilot harness use Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

## What the result does

`draft_pack()` reads one request, one guide, one directory, and one question date, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `approved_for_use` stays false. `contacted`, `scheduled`, `scored`, `ranked`, and `hiring_decision` stay false.

**Questions.** One question is drafted for each essential criterion whose text is not itself a probe or an occupational requirement. The style is `competency` or `strengths`, and only when the guide says so. A desirable criterion is asked only when `ask_desirable` is the boolean true. A proposed question is reviewed and is not added to the pack. A question that does not name a stated criterion is excluded as untied. No criterion is invented.

**Probes.** A question that asks about age, marriage, pregnancy or childcare plans, religion, nationality beyond right to work, disability or health, sex, sexual orientation, gender reassignment, or race is excluded. "It is not true that the interview includes a question about your age" does not count. "Do you have the right to work in the United Kingdom?" does not count as a nationality question. An adjustment sentence that says the person need not disclose health does not count as a health question.

**Routes.** A pre-offer health question goes to HR under section 60. A sickness-absence question is also routed under section 15. An occupational requirement goes to HR under Schedule 9 paragraph 1. Positive action is routed under section 158 or section 159. A sentence that requires the candidate to pay for an adjustment is flagged against the opened text of section 20(7). None of those routes is decided.

**Rubric.** Anchors come from the guide. A missing anchor stays null. An unreadable scale is not replaced with 1 to 5. `scores_a_candidate` stays false.

**People and markings.** The directory supplies the role and the clearance. A distress, grievance, or safeguarding cue, including a paraphrase, is a route to a person. The cue is not copied. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A legal hold and every retention label stay on the result.

**Approval.** `record_questions_approval()` and `record_rubric_approval()` take the directory recruiter and the exact hashes. `record_hr_seen()` takes the directory HR partner and the route hash. `record_pack_approval()` sets `approved_for_use` only after both accepts and every route has been seen. Approving the pack still does not contact anyone.

`contact_candidate`, `schedule_interview`, `score_candidate`, `rank_candidates`, and `make_hiring_decision` raise `InterviewPackForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08 and 64 must be present beside this folder.

```bash
cd experiments/65-interview-pack-builder
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/pack.py --request examples/sample_request.json --guide fixtures/guide.json --directory fixtures/directory.json --as-of 2026-11-14
```

The sample request carries approval keys, a self-declared role, and a self-declared clearance on purpose. They are ignored. `human_approval` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 20 passed, 0 failed, 0 errors, 20 cases. Paraphrase recall is a separate block and is not added to that total. On the checked-in run, nine categories were 22/23 and prohibited-action requests were 24/25. The misses are idioms that use none of the concept words. They are listed in the report.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Probe matching is an example list. An idiom that uses none of the concept words is not a match. The checked-in recall is below 1. The misses are in `eval/smoke_report.json`.
- "Not" within eight words before a probe can hide a match. "It is not true that the pack includes a question about your age" is the case this rule is built for. A distress cue is still routed when the cue words are present, including inside a denial.
- A job whose duty is safeguarding work contains the word safeguarding and is routed to a person. That is cautious. It is not a finding that the role is a disclosure.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period. Requiring one anchor per scale point, when the guide states no minimum, is also a starter rule.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted on the input and checked on the output. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- Schedule 8 was not opened. Northern Ireland employment law is not stated. The Equality Act sections opened here are marked E+W+S.
- The ICO recruitment page is draft and under review. The employment practices code paragraphs are unverified as current guidance. A £10 subject-access fee in that PDF is not relied on.
- A question date after a page's "up to date" stamp is not treated as covered by that pin. Section 60 was stamped 17 November 2026. Schedule 9 paragraph 1 was stamped 14 November 2026. Section 158 was stamped 19 November 2026. The other Equality Act sections opened here were stamped 18 November 2026.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional.
- This is not legal advice, a recruitment decision, or an invitation that has been sent.

## Equality Act and recruitment records

The manifest does not assert the controller's lawful basis. The sections listed above were read on 19 November 2026. `discrimination_decided`, `section_15_decided`, `section_20_decided`, `section_20_met`, `occupational_requirement_decided`, `positive_action_decided`, and `health_question_decided` stay false.

A retention label and a legal hold stay on the result. They are not a disposal decision. The code PDF says interview notes should be relevant to the recruitment process and that interviewers should know people may ask for access. That status is unverified. This starter does not answer a subject-access request.

## Two Copilot Studio harnesses

Both call `src/pack.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness contacts a candidate. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. Later topics call the record functions only with the decision object. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 19 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says it uses Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The catalogue row H008 names this harness first. The gates are the same as the standard harness.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The questions, the hashes, and the approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Wording list: [../64-job-description-quality/](../64-job-description-quality/).

## Project structure

```
experiments/65-interview-pack-builder/
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

- [Equality Act 2010, section 13](https://www.legislation.gov.uk/ukpga/2010/15/section/13)
- [Equality Act 2010, section 15](https://www.legislation.gov.uk/ukpga/2010/15/section/15)
- [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19)
- [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39)
- [Equality Act 2010, section 60](https://www.legislation.gov.uk/ukpga/2010/15/section/60)
- [Equality Act 2010, section 158](https://www.legislation.gov.uk/ukpga/2010/15/section/158)
- [Equality Act 2010, section 159](https://www.legislation.gov.uk/ukpga/2010/15/section/159)
- [Equality Act 2010, Schedule 9, paragraph 1](https://www.legislation.gov.uk/ukpga/2010/15/schedule/9/paragraph/1)
- [ICO, Employment practices and data protection: recruitment and selection](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/recruitment-and-selection/)
- [ICO, The employment practices code (PDF)](https://ico.org.uk/media2/migrated/1064/the_employment_practices_code.pdf)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
