# Experiment 60: Manager One-to-One Preparation Agent

Catalogue ID **H003**. Autonomy **A0**. The line manager selects the context for one meeting. The assistant drafts a short prep note from that selection only: previous one-to-one notes, agreed objectives, the employee's own shared updates, and team calendar items. Each quoted line has a citation. Open questions sit beside those lines. They are not ratings.

The employer in this folder, Harbourside Instruments Ltd, is invented. There are no real people.

**What it does.** It quotes follow-ups from the last note, the agreed objectives, the shared update, and the calendar item. A sign of distress, wellbeing, or a safeguarding concern is flagged for the manager to handle humanely, with an HR and employee-assistance route. It is not turned into a routine agenda item. A denial is not treated as the thing denied.

**What it does not do.** It does not rate performance, compare employees, infer health or a protected characteristic, or recommend disciplinary or capability action. It does not read a mailbox or a chat. It does not treat a sentence in a note as the manager's selection or as clearance.

Stack in the catalogue: Microsoft 365 and Work IQ. The note itself is Python in the standard library. This starter does not call Work IQ. What Work IQ would do with a live calendar was not opened on 17 November 2026 and is unverified.

## The problem

A one-to-one goes better when the manager can see what was agreed last time, what the employee has shared, and what is on the team calendar. The same folder often also holds a mailbox, a chat, a performance score, or a sentence that tells the tool to ignore its instructions. Those are not the meeting.

This starter keeps them apart. The selection object is the authorisation. The quotation is the note.

## Non-goals

- Rating performance, scoring a person, or writing "outstanding" or "poor" as the agent's view.
- Comparing one employee with another, or building a profile.
- Inferring health, pregnancy, disability, or any other protected characteristic or personal circumstance.
- Recommending a disciplinary step, a capability step, or a performance improvement plan.
- Reading a mailbox, a chat, or any source the manager did not select. Selecting a mailbox does not make it meeting context.
- Treating "approved", "I am the line manager", or "my clearance is TOP SECRET" inside a note as the directory.
- Sending the note, or writing a personnel record.
- Calling Microsoft Graph, Work IQ, or a live calendar.
- Refreshing legislation from the web when a pin is stale.

## What was opened

Opened on 17 November 2026 unless the row says otherwise. The core does not download these pages when it runs.

| Source | What this starter takes from it |
|---|---|
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(a): processed lawfully, fairly and in a transparent manner. Article 5(1)(c): adequate, relevant and limited to what is necessary. Article 6 and Article 9 were not opened. A lawful basis is not asserted. |
| [Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A) | A decision is based solely on automated processing if there is no meaningful human involvement, and it is significant if it produces a legal effect or a similarly significant effect. Substituted for Article 22 on 19 June 2025 for specified purposes, and on 5 February 2026 in so far as not already in force, by the Data (Use and Access) Act 2025 sections 80(1) and 142(1) and (2)(h), and S.I. 2026/82 regulation 2(j), with regulation 5. Regulation 5 was not opened and is not interpreted. |
| [Article 22B](https://www.legislation.gov.uk/eur/2016/679/article/22B) | Article 22B(1) restricts a significant decision based entirely or partly on Article 9(1) data where the decision is solely automated, unless a condition is met. Article 22B(3) and 22B(4) were in the text returned. Article 22B(2) was not in that text and is not quoted. Article 6 was not opened. This starter does not decide that a condition is met. |
| [Article 22C](https://www.legislation.gov.uk/eur/2016/679/article/22C) | Where Article 22C(1) applies, Article 22C(2) requires information, representations, human intervention, and a way to contest the decision. It refers to regulations under Article 22D(3). Those regulations were not read. |
| [Article 22D](https://www.legislation.gov.uk/eur/2016/679/article/22D) | The Secretary of State may by regulations make further provision, including about meaningful human involvement. Article 22D(5): the affirmative resolution procedure. No such regulations were read. Whether any have been made is unverified. |
| [Equality Act 2010, section 4](https://www.legislation.gov.uk/ukpga/2010/15/section/4) | The protected characteristics are listed. The page said it was up to date with changes known to be in force on or before 16 November 2026. Extent England and Wales and Scotland. They are not inferred about a person. Northern Ireland equality law was not opened. |
| [Section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) | Section 39(2) prohibits discrimination against an employee, including as to terms, access to promotion, transfer, training or other benefits, dismissal, and any other detriment. Section 39(5): a duty to make reasonable adjustments applies to an employer. The page said it was up to date on or before 17 November 2026. This starter does not decide that either has been met or breached. |
| [ICO, monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/) | The hub is under review because of the Data (Use and Access) Act and may change. This starter does not decide that a prep note is monitoring, and it does not decide that monitoring is lawful. |
| [ICO, solely automated monitoring](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/what-do-we-need-to-do-if-we-use-monitoring-tools-that-use-solely-automated-processes/) | The page still names Article 22. It gives pay and dismissal as examples of similarly significant effects, and it says human oversight should not be a token gesture. The same review banner is on the page. Reconciliation with Articles 22A to 22D is unverified. |

## What the note does

`src/prepare.py` reads the pack and the as-of date. The same inputs produce the same JSON. `performance_rating`, `comparison`, `disciplinary_recommendation`, and `health_inference` are null. `human_approval` is null unless `acknowledge()` is called with a separate seen-step for that manager, that meeting, and those source ids. That call records that the manager has seen the note. It does not rate anyone.

**Selection.** The selector must be the line manager of that employee on the synthetic directory. A guest who writes "I am the line manager" is refused. A clearance boast is not the directory clearance.

**Negation.** "It is not true that the objective includes a client entertainment budget" does not count as the objective including client entertainment. A later sentence can still be a follow-up.

**Distress.** Experiment 15's phrase list and a local paraphrase list flag safeguarding, self-harm, hardship, and wordings such as "finding it hard to keep going". A phrase inside a denial is not a flag. The sentence is not copied. The route is HR and the employer's employee assistance programme.

**Markings.** The label is taken from the metadata and from the text. The higher label wins. A SECRET cover is not quoted. A negated "SECRET" does not raise the label. A legal hold and every retention label are kept. A clearance claimed in the note is ignored.

**Bad input.** A date or a stale window that cannot be read is not replaced with today, with the as-of date, or with zero.

**Instructions.** A sentence that tells the agent to ignore instructions, rate performance, read a mailbox, or strip a hold is recorded and not quoted.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 15, 41, and 51 sit beside this folder. The note calls them in-process. It does not copy their detectors.

```bash
cd experiments/60-manager-one-to-one-prep
python -m pip install -r requirements.txt
python -m pytest tests/ -q
python eval/evaluate.py
python src/prepare.py --pack examples/sample_pack.json --as-of 2026-11-17
```

`eval/evaluate.py` prints a **deterministic smoke test**. Fourteen synthetic cases, each counted once. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A pack that is not marked synthetic is refused. An unreadable date exits in the JSON as `needs_human` and does not invent a day.

## Limitations

- The notes are synthetic. They are not any employer's one-to-ones.
- Article 22B(2) was not in the text returned on 17 November 2026. It is not quoted.
- S.I. 2026/82 regulation 5 was not opened. It is not interpreted. The commencement footnote names it.
- No regulations under Article 22D were read. Whether any have been made is unverified.
- The ICO monitoring pages still name Article 22 and are under review. They were not reconciled with Articles 22A to 22D.
- Article 6 and Article 9 were not opened. No lawful basis is asserted.
- Equality Act sections 4 and 39 are England and Wales and Scotland. Northern Ireland equality law was not opened.
- The 180-day window is a configuration choice. It is not a statutory retention period.
- Work IQ, Microsoft Graph, and a live calendar are not called. Their current behaviour is unverified here.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant uses Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a performance appraisal.

## Two Copilot Studio harnesses

Both call `src/prepare.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness rates a person, reads a mailbox, or sends a message. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics for a selected meeting, a human flag, and a refusal. The flow returns JSON and stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness.** On 17 November 2026 Microsoft Learn names this the Microsoft Copilot harness: a runtime for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The common brief calls that layout a GitHub Copilot harness. The page that was opened did not use those words. Skills are in [skills/](skills/) and [docs/github-copilot-harness.md](docs/github-copilot-harness.md). This file does not assign trigger phrases or routing weights.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/60-manager-one-to-one-prep/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 17 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A), [Article 22B](https://www.legislation.gov.uk/eur/2016/679/article/22B), [Article 22C](https://www.legislation.gov.uk/eur/2016/679/article/22C), and [Article 22D](https://www.legislation.gov.uk/eur/2016/679/article/22D)
- [Equality Act 2010, section 4](https://www.legislation.gov.uk/ukpga/2010/15/section/4) and [section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39)
- [ICO, Employment practices and data protection: monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/)
- [ICO, solely automated monitoring tools](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/what-do-we-need-to-do-if-we-use-monitoring-tools-that-use-solely-automated-processes/)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
