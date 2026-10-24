# Experiment 06: Policy Q&A — UK public-sector / NHS corporate services

Catalogue ID **M003**. Stack: Microsoft 365 and Copilot Studio. Autonomy **A0**.

A starter for corporate-services teams in an NHS organisation, and for other UK public bodies with the same shape of policy library. A member of staff asks a question. The answer is a quotation from an approved, versioned policy, with the policy's review date. If nothing in that register supports an answer, the agent says "I don't know" and logs the question for the policy owner.

The corpus in this folder is synthetic. The organisation is **Northmere NHS Foundation Trust**, which is fictional. These are not NHS England policies and they are not the policies of any real trust.

**The policy owner approves authoritative sources.** A document the owner has not approved is invisible to staff answers. The agent cannot approve a source, publish a change, decide a person's entitlement, place an order, or give clinical advice.

This revision contains the permissions manifest, the deterministic register, synthetic policies, a mock smoke test, a measured time-saving evaluation design, and build notes for two Copilot Studio harnesses. Nothing here calls a model.

## The problem

NHS England announced on 8 June 2026 that it is providing Microsoft 365 Copilot to 505,000 clinicians and support staff, with rollout to more than 500,000 staff expected by October 2026, and a typical trust allocation starting at around 2,000 licences. The same announcement names human resources, finance, and procurement among the uses it anticipates. The page was opened on 24 October 2026: [NHS England](https://www.england.nhs.uk/2026/06/500000-nhs-staff-to-get-new-artificial-intelligence-tools-to-help-free-up-more-time-for-patients/).

A large Copilot estate creates demand for answers grounded in local policy. An ungrounded answer, a superseded document, or a clinical reply from a corporate assistant is the failure this starter is built to avoid.

The announcement says a trial of more than 30,000 staff in 90 organisations found that administrative support could save an average of 43 minutes per person per day or more. It does not describe the measurement method. A Microsoft feature dated 21 October 2026 says participants in that trial "reported" saving 43 minutes a day ([Source EMEA](https://news.microsoft.com/source/emea/features/before-the-ambulance-arrives-how-ai-is-helping-the-nhs-rethink-patient-care/)). This experiment does not use either figure as a result. The evaluation design below measures elapsed time with timestamps, and only on answers that stay grounded.

## Who it helps

**Staff in HR, finance, procurement, IT, and estates.** They get the clause, the version, and the review date, or a clear "I don't know".

**Policy owners.** A second harness reviews which topics have an approved in-date source, which policies are past their review date, and which approved policies disagree. It drafts a change note. The owner accepts that note outside the agent.

**A trust, a board, or a council** that wants a pattern it can read before anyone points Copilot at a live intranet. The Python register runs with no tenant and no credentials.

## Non-goals

- Answering a clinical question, interpreting a guideline, or advising on a patient's care. Those questions are refused and signposted.
- Deciding a person's leave balance, pay, sickness, flexible-working request, or disciplinary outcome. Quoting the published rule is in scope. Applying it to a person is not.
- Approving a policy, a source, a purchase, a contract award, or an expense.
- Publishing a change note, or writing SharePoint, a policy register, payroll, finance, or a clinical system.
- Sending email or Teams messages.
- Answering from a draft, a superseded version, a document the policy owner has not approved, or a clause that contains an instruction to the model.
- Choosing between two approved policies that disagree.
- Treating a policy past its review date as current.
- Guessing when no approved clause matches.
- Using the NHS trial's 43-minute figure as a measured saving.
- Acting as a medical device, a clinical safety case, or legal advice.

## What the register does

`src/answer.py` answers one question from `fixtures/policies.json`. It does not call a model and it does not read the network. The same question and the same as-of date always produce the same JSON.

A clause can be quoted only when all of the following are true:

- the policy status is `approved`;
- `approved_by_policy_owner` is true (the owner set that flag; the agent cannot);
- the policy is not superseded or withdrawn;
- the clause is not quarantined (its text does not contain an instruction to the model);
- the review date is on or after the as-of date the caller supplies.

The answer is the clause text, not a paraphrase. Each citation carries the policy id, version, clause id, and review date.

| Outcome | When | What the staff member sees |
| --- | --- | --- |
| `answered` | One or more in-date approved clauses match, and they do not disagree | The quotation and the citations. `may_be_relied_on` is true. |
| `i_dont_know` | No approved clause matches | "I don't know." The question is recorded for the owner. Nothing is persisted by this starter. |
| `stale_withheld` | The only matches are past their review date | "I don't know", plus the policy id, version, and review date. The clause text is not returned as an answer. |
| `conflict` | In-date approved clauses take different positions on the same topic | "I don't know which rule applies." Both sources are listed. A draft change note is attached. It is not published. |
| `refused_clinical` | The question is about patient care, diagnosis, treatment, medicines, or clinical guidance | A fixed signpost. No policy text. |
| `refused_decision` | The question asks the agent to apply a rule to a person, or to approve spend or an award | A refusal. The published rule is not calculated into a personal result. |
| `refused_injection` | The question tells the agent to ignore its rules, approve a source, or change a review date | A refusal. No flag on a policy changes. |

A policy is stale when `review_due` is before the as-of date. On the review date itself it is still in date. The next day it is stale. That is a property of the date written on the document. It is not a legal opinion that the text is still good law.

`src/review.py` is the policy-owner path: coverage, stale policies, conflicts, quarantined clauses, and draft change notes. `accepted_by_policy_owner` and `published` are false on every note.

Conflict detection reads structured claims on clauses (`topic` and `position`). It does not infer a contradiction from free text. A disagreement that has not been marked as a claim will not be flagged. That limit is deliberate: the starter does not guess.

## Clinical boundary

Questions about patients, diagnosis, prescribing, medicines, symptoms, clinical guidelines, or treatment are refused. The signpost sends the asker to the organisation's clinical guidance owner, the on-call clinician for the service, or the clinical librarian.

The NHS England announcement also describes clinical administration, such as drafting letters and discharge paperwork. That work is outside this starter. A Microsoft feature of 21 October 2026 reports Dr Alec Price-Forbes, national chief clinical information officer for NHS England, as saying Copilot is for administrative tasks and not clinical work. That sentence is Microsoft's report of his words. This folder's refusal rule is its own control, and it is narrower than the announcement: HR, finance, procurement, IT, and estates policies only.

IT and estates are in this corpus because they are corporate services. The NHS England page named HR, finance, and procurement. It did not, on the page opened, name IT or estates.

This starter does not claim a medical-device classification. A clinical safety officer decides what applies before any deployment that could touch care.

## Measured time saving

Self-reported minutes are not the endpoint. `eval/time_saving_design.md` sets the rule. `src/time_saving.py` applies it.

The primary endpoint is the median of paired differences in elapsed seconds (manual search minus agent path). Elapsed seconds are computed from two timestamps recorded by the test harness: when the question was shown, and when the person submitted the answer they would rely on. A field carrying a self-reported "minutes saved" is rejected and cannot enter the median. An item whose agent outcome is wrong, or whose citations are not grounded in the approved in-date register, is excluded. A fast wrong answer is not a saving.

`eval/time_observations.json` is synthetic fixture arithmetic so the scorer can be tested. It is not a study of NHS staff, and it is not the 43-minute trial figure. A live study would instrument both arms on the same questions and the same corpus. This repository does not run that study.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/06-nhs-policy-qa
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
```

`eval/evaluate.py` prints a **mock smoke test**. The questions are synthetic and the matcher is a phrase list tuned to them. `eval/smoke_report.json` is that same run. It is not a model score and it is not a staff study.

Answer one question:

```bash
python src/answer.py \
  --question "How much notice do I need to book annual leave?" \
  --as-of 2026-10-24
```

Review the register as a policy owner:

```bash
python src/review.py --as-of 2026-10-24
```

## Sample

As-of date 24 October 2026. Question: how much notice to book annual leave.

- The answer quotes Northmere annual leave policy HR-LEAVE-003, version 4.1, clause 4.2.
- The review date on that policy is 31 March 2027. It is in date.
- The superseded policy that asked for more notice is not cited.

Question: what antibiotic to give a patient.

- Outcome `refused_clinical`. No clause is returned.

Question: can alcohol be claimed on expenses?

- Two approved, in-date policies disagree. Outcome `conflict`. A draft change note is returned. `published` is false.

Question: how long should a password be?

- The only match is past its review date (30 June 2025). Outcome `stale_withheld`. The clause is not given as an answer.

## Limitations

- The matcher needs the question to contain a phrase listed on the clause. A paraphrase that misses every phrase returns "I don't know". That is the safe side of a guess. It will under-answer.
- Conflicts are only the claim pairs written in the corpus. Unmarked contradictions are not detected.
- The review date is the date in the file. The starter does not check statute, Agenda for Change, or the organisation's standing orders.
- Quoting an allowance is not a calculation of anyone's balance. The refusal of personal decisions is a phrase check. A novel way of asking can slip through to a quotation, which is still not a decision, or miss and return "I don't know".
- The smoke test is a pipeline check of that phrase list. It is not a measure of a model's groundedness.
- The time-saving numbers in the smoke report are computed from invented timestamps. They are there to prove the scorer rejects self-report and drops ungrounded items.
- Pointing Copilot Studio's generative answers at a whole SharePoint library would bypass the approval flag, the version, and the review date. The build guide says not to do that. This repository cannot stop a tenant from doing it.
- No live Microsoft Foundry run has been done.

This is not clinical advice, legal advice, or a statement of any organisation's compliance.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Copilot Studio standard harness, the lead path for staff questions: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness, for policy owners reviewing coverage, conflicts, stale policies, and change notes: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry path: [docs/foundry.md](docs/foundry.md).
- Time-saving design: [eval/time_saving_design.md](eval/time_saving_design.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/06-nhs-policy-qa/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── fixtures/
│   └── policies.json
├── src/
│   ├── answer.py
│   ├── corpus.py
│   ├── review.py
│   └── time_saving.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened for this revision

Pages retrieved on 24 October 2026.

- [NHS England, 8 June 2026, Copilot for 505,000 staff](https://www.england.nhs.uk/2026/06/500000-nhs-staff-to-get-new-artificial-intelligence-tools-to-help-free-up-more-time-for-patients/)
- [Microsoft Source EMEA, 21 October 2026](https://news.microsoft.com/source/emea/features/before-the-ambulance-arrives-how-ai-is-helping-the-nhs-rethink-patient-care/)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview)
- [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness)
- [Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)

The NHS England page does not, in the copy opened that day, mention Copilot Studio. This starter uses Copilot Studio because that is the catalogue stack for M003 (M365 + CS), not because the announcement said so.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
