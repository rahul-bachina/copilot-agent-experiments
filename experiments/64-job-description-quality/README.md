# Experiment 64: Job Description Quality Checker

Catalogue ID **H007**. Autonomy **A0**. The assistant suggests edits. The recruiter accepts or rejects each suggestion and writes the final wording. The agent does not publish, post, or send an advert.

A recruiter pastes one synthetic draft and points at one synthetic style and grading guide. The starter flags example phrases (gendered or age-coded wording, an unnecessary physical or degree requirement, "native English speaker"), inaccessible language against the guide's own limit, a duty that the guide says is not that grade, a missing salary or location where the guide requires one, and an essential criterion that is not linked to a duty. Each prompt has a reason and a suggested alternative. Ashcombe Borough Council is invented.

The core is Python in the standard library. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) when personal data is pasted in, and [Experiment 36](../36-cross-source-validation/) when a salary or a grade is stated in two places. A user can run it without a tenant. The catalogue row names the GitHub Copilot harness first. This folder still ships both Copilot Studio harnesses.

## The problem

A draft can say, in its own text, that the recruiter has approved it and that the agent should publish it. It can ask for a native English speaker, a degree the grade does not record, or a health history before a job is offered. It can also carry a right-to-work sentence or a Disability Confident sentence that must stay. Those are the failures this starter is built to separate. A real decision is a separate object, from the directory recruiter, for that exact draft hash and that exact suggestion or wording.

## Non-goals

- Publishing, posting, or sending an advert.
- Treating approval text inside the draft as approval.
- Scoring candidates, ranking applicants, or scoring an advert against people.
- Deciding that Equality Act 2010 section 13, 19, or 39 was contravened.
- Deciding that Schedule 9 paragraph 1 (occupational requirement) or section 159 (positive action) is met. Those routes go to HR.
- Deciding that a health question falls within section 60(6).
- Checking any person's right to work, or giving a penalty under the Immigration, Asylum and Nationality Act 2006, section 15.
- Stripping a mandated statement, a legal hold, or a retention label.
- Trusting a self-declared role, guest status, or clearance in the draft.
- Coercing an unreadable salary, grade, date, or sentence limit to zero or to a default.
- Choosing which of two disagreeing figures is right.
- Giving legal advice. The prompts are for a person's judgement.
- Autonomy A3. A3 is not permitted in this catalogue.
- Inventing a statistic about biased wording. The word list is an example the organisation must review.

## What was opened

Opened on 18 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Equality Act 2010, section 13](https://www.legislation.gov.uk/ukpga/2010/15/section/13) | Section 13(1): a person discriminates against another if, because of a protected characteristic, they treat that person less favourably than they treat or would treat others. Extent E+W+S. The page said it was up to date with changes known to be in force on or before 18 November 2026. This starter does not decide that less favourable treatment occurred. |
| [Section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19) | Section 19(1) and 19(2), including 19(2)(d). Section 19(3) lists age, disability, gender reassignment, marriage and civil partnership, race, religion or belief, sex, and sexual orientation. The page stamp was 18 November 2026. This starter does not apply the test. |
| [Section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) | Section 39(1)(a) to (c): arrangements for deciding to whom to offer employment, the terms of an offer, and not offering employment. The page stamp was 18 November 2026. A job advert can sit inside those arrangements. This starter does not decide a contravention. |
| [Section 60](https://www.legislation.gov.uk/ukpga/2010/15/section/60) | Section 60(1): a person to whom an application for work is made must not ask about the health of the applicant before offering work, or before including them in a pool from whom the person intends to select. Section 60(6) lists purposes the section does not apply to. This starter does not decide that any purpose is met. The page stamp was 17 November 2026, not 18 November. |
| [Section 159](https://www.legislation.gov.uk/ukpga/2010/15/section/159) | Section 159(4): positive action in recruitment or promotion applies only if A is as qualified as B, P does not have a policy of treating persons who share the characteristic more favourably, and the action is a proportionate means of achieving the aim in subsection (2). The page stamp was 15 November 2026. This starter does not decide that the section permits the draft. |
| [Schedule 9, paragraph 1](https://www.legislation.gov.uk/ukpga/2010/15/schedule/9/paragraph/1) | Paragraph 1(1): an occupational requirement, proportionate, and the person does not meet it (or there are reasonable grounds for not being satisfied that they do). The page stamp was 14 November 2026. This starter does not decide that the paragraph is met. |
| [Immigration, Asylum and Nationality Act 2006, section 15](https://www.legislation.gov.uk/ukpga/2006/13/section/15) | Section 15(1) and 15(2), as context for keeping a right-to-work statement. Section 15(2) allows a penalty notice. The order under section 15(3) was not opened. No person's leave is checked and no penalty is given. The page stamp was 16 November 2026. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox. The prose says agents on that harness use Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

The Disability Confident scheme page was not opened. A statement is kept when the organisation's guide marks the phrase as mandated. That is the guide's rule, not a description of the scheme.

## What the result does

`review_draft()` reads one request, one guide, one directory, and one question date, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `published`, `posted`, and `sent` stay false. `quality_score` stays null.

**Role and clearance.** The directory supplies both. "My role is recruiter" and "my clearance is TOP SECRET" are recorded and ignored. A guest on the directory stays a guest. An unreadable clearance is not replaced with OFFICIAL.

**Phrases.** An example phrase counts only when a sentence affirms it. "It is not true that the role requires a native English speaker" does not affirm that phrase. The list is labelled as an example the organisation must review. There is no statistic.

**Guide.** A review-due date on the question date is stale. That is this starter's rule, not a statute. A guide whose review date is after the question date is not yet in force. An unreadable salary, grade, date, or sentence limit is flagged and is not replaced with zero or with 25. A missing salary or location is not invented.

**Two figures.** Where a salary or a grade appears in two places, Experiment 36 compares the extracts. A material discrepancy is not resolved. `agent_chose_source` stays false. A single source is labelled as such and is not invented into a second source.

**Routes.** Words that may be an occupational requirement, positive action, or a pre-employment health question go to HR. The decided flags stay false. A recruiter cannot close that route by accepting a suggestion.

**Mandated wording.** A right-to-work sentence or a Disability Confident sentence that the guide lists, and that is actually in the draft, is kept. An instruction to strip it is not followed. Final wording that drops a statement which was present is not recorded.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**People.** A distress, vulnerability, or safeguarding cue, including a paraphrase such as "at the end of their tether", is a route to a person. The cue is not copied. A request to score candidates or to rank applicants is refused. Nobody is scored.

**Statute.** The note quotes the pins. It says the prompts are not legal advice. A pin whose page stamp is earlier than the question date is marked not confirmed for that date. Today is not used.

`record_suggestion_decision()` records one accept or reject. The approver has to be the directory recruiter, the item has to be `suggestion`, and the draft hash and the suggestion hash have to match. `record_hr_seen()` is the HR partner, item `hr-route`, decision `seen`. It does not decide the legal question. `record_final_wording()` stores the recruiter's text only when the wording hash is the hash of that exact text, every suggestion has a decision, and every HR route has been seen. `published` stays false.

`publish`, `post`, `send`, `score_candidate`, `score_advert_against_people`, and `rank_applicants` raise `JobDescriptionForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08 and 36 must be present beside this folder, with the neighbours those experiments load.

```bash
cd experiments/64-job-description-quality
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/review.py --request examples/sample_request.json --guide fixtures/guide.json --directory fixtures/directory.json --as-of 2026-11-14
```

The sample request carries approval keys, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. `human_approval` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 20 passed, 0 failed, 0 errors, 20 cases.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Phrase matching is an example list. A paraphrase that does not use the phrase is not a match. The checker does not guess a further phrase, and it does not report how often any phrase appears in real adverts.
- "Not" within eight words before a phrase can hide a match. "It is not true that X includes Y" is the case this rule is built for.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period.
- The sentence limit and the jargon list come from the guide. They are not a reading-age measure.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted on the input and checked on the output. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask. Experiment 08 does not detect those either.
- Experiment 36 does not choose a source. A match is not a finding that the salary is correct. Quotes from the comparison are not copied.
- The order under section 15(3) was not opened. The Disability Confident scheme page was not opened. Northern Ireland employment law is not stated. The Equality Act sections opened here are marked E+W+S.
- A question date after a page's "up to date" stamp is not treated as covered by that pin. Sections 13, 19, and 39 were stamped 18 November 2026. Section 60 was stamped 17 November. Section 159 was stamped 15 November. Schedule 9 paragraph 1 was stamped 14 November. Section 15 of the 2006 Act was stamped 16 November.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional.
- This is not legal advice, a recruitment decision, or an advert.

## Equality Act and right to work

The manifest does not assert the controller's lawful basis. Sections 13, 19, 39, 60, and 159, and Schedule 9 paragraph 1, were read on 18 November 2026. `discrimination_decided`, `occupational_requirement_decided`, `positive_action_decided`, and `health_question_decided` stay false.

Section 15 of the Immigration, Asylum and Nationality Act 2006 was read the same day as context for keeping a right-to-work statement. `right_to_work_checked` and `penalty_given` stay false.

A retention label and a legal hold stay on the result. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/review.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness publishes. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. Later topics call the record functions only with the decision object. Microsoft's harness overview, opened 18 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 18 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says it uses Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The catalogue row H007 names this harness first. The gates are the same as the standard harness.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The prompts, the hashes, and the approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Cross-source validation: [../36-cross-source-validation/](../36-cross-source-validation/).

## Project structure

```
experiments/64-job-description-quality/
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
- [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39)
- [Equality Act 2010, section 60](https://www.legislation.gov.uk/ukpga/2010/15/section/60)
- [Equality Act 2010, section 159](https://www.legislation.gov.uk/ukpga/2010/15/section/159)
- [Equality Act 2010, Schedule 9, paragraph 1](https://www.legislation.gov.uk/ukpga/2010/15/schedule/9/paragraph/1)
- [Immigration, Asylum and Nationality Act 2006, section 15](https://www.legislation.gov.uk/ukpga/2006/13/section/15)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
