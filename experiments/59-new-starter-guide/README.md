# Experiment 59: New Starter Guide Agent

Catalogue ID **H002**. Autonomy **A1**. The line manager approves the personalised checklist before it is shared. Nothing is sent, provisioned, or recorded without that approval. Related to Experiment 58 (the handbook answer), Experiment 57 (a team-space membership proposal), Experiment 21 (the IT service desk), and Experiment 11 (Employment Rights Act 2025 dates that are not re-opened here).

The pack and the directory are synthetic. The employer, Riverbend Workshops CIC, is invented. There are no real people and no personal names on the directory.

**What it does.** From HR-approved role templates, policies with effective dates, and IT and facilities steps, it drafts a checklist for the role on the directory and answers a how-do-I question with the section and the date. Equipment, accounts, access, and training are proposals for the manager or the service desk.

**What it does not do.** It does not request equipment, create an account, grant access, or enrol training. It does not collect special-category data. It does not complete a right-to-work check or decide a reasonable adjustment. It does not treat a sentence in the request as the manager's approval.

Stack in the catalogue: Copilot Studio, Microsoft 365, and Power Platform. The draft itself is Python in the standard library. Calling Experiment 57 loads Experiment 03, which needs `jsonschema` and PyYAML. Those are in `requirements.txt`. No network call is made.

## The problem

A new starter and their manager need the first weeks written down: which policy is in force, which IT step is only a proposal, and which question has to go to a person. A draft policy can say, in its own text, that HR has approved it. A message can say the manager has already approved the list. A file can carry a SECRET cover under an OFFICIAL metadata label.

This starter keeps those apart. The scope object is HR's approval of the sources. The directory is the role and the line manager. The approval function is the only thing that can share the list, and only for that exact list.

## Non-goals

- Requesting equipment, creating an account, granting access, or enrolling anyone on training.
- Deciding that a right-to-work check was met, or that a step is a reasonable adjustment.
- Producing the written statement of particulars, or deciding that Employment Rights Act 1996 section 1 was met.
- Collecting a passport, a share code, a health detail, a pregnancy detail, or any other special-category data.
- Giving individual legal, medical, or tax advice.
- Stating Northern Ireland employment law. The Act pages opened here are marked England and Wales and Scotland, or United Kingdom for section 15. Northern Ireland employment legislation was not opened.
- Treating a draft, or a file marked above the ceiling, as a checklist item.
- Calling SharePoint, Microsoft Graph, Microsoft 365 Copilot, or a live service desk.
- Refreshing legislation from the web when a pin is stale or incomplete.

## What was opened

Opened on 17 November 2026. The core does not download these pages when it runs.

| Source | What this starter takes from it |
|---|---|
| [Employment Rights Act 1996, section 1](https://www.legislation.gov.uk/ukpga/1996/18/section/1) | The page said it was up to date with all changes known to be in force on or before 16 November 2026. Section 1(1): where a worker begins employment, the employer shall give the worker a written statement of particulars of employment. Section 1(2)(b): the statement must be given not later than the beginning of the employment. Section 1(2) opens with "Subject to sections 2(2) to (4)". Extent E+W+S. The footnote attributes the substitution of section 1(2), in force 6 April 2020, to S.I. 2018/1378, regulations 1 and 3(a). That instrument was not opened. Sections 2(2) to 2(4) were not opened. |
| [GOV.UK, written statement](https://www.gov.uk/employment-contracts-and-conditions/written-statement-of-employment-particulars) | "The employer must provide the principal statement on the first day of employment and the wider written statement within 2 months of the start of employment." This is the GOV.UK summary. It is not the text of section 2. |
| [Immigration, Asylum and Nationality Act 2006, section 15](https://www.legislation.gov.uk/ukpga/2006/13/section/15) | The page said it was up to date with all changes known to be in force on or before 16 November 2026. Extent U.K. Section 15(1) makes it contrary to the section to employ an adult subject to immigration control in the cases the subsection lists. Section 15(3): an employer is excused from paying a penalty if he shows that he complied with any prescribed requirements. Section 15(7)(d): an order may require action to be taken before employment begins. The order itself was not opened. |
| [Right to work checks: an employer's guide](https://www.gov.uk/government/publications/right-to-work-checks-employers-guide) | The HTML page, last updated 1 October 2026, says the guidance explains what employers must do to prevent illegal working by carrying out right to work checks on people before employing them. The PDF "Employer's guide to right to work checks: 1 October 2026" (83 pages) was not opened. No paragraph number from that PDF is cited. |
| [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) | The page said it was up to date with all changes known to be in force on or before 17 November 2026. Section 39(5): a duty to make reasonable adjustments applies to an employer. Extent E+W+S. Not applied to a person. |
| [Section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | The page said it was up to date with all changes known to be in force on or before 16 November 2026. Section 20(3) is the first requirement. Sections 20(4) and 20(5) were on the page and are not applied to a person. Schedule 8 was not opened. |
| [UK GDPR, Article 13](https://www.legislation.gov.uk/eur/2016/679/article/13) | Article 13(1): where personal data are collected from the data subject, the controller shall, at the time when personal data are obtained, provide the information listed, including Article 13(1)(a). Article 13(4), as amended on the page: paragraphs 1, 2 and 3 do not apply to the extent that the data subject already has the information. A currency banner of the kind shown on the Act pages was not in the text returned. An ICO privacy-notice URL tried the same day returned 404. No ICO sentence is cited. Article 6 and Article 9 are not asserted. |
| Experiment 11 pins | Employment Rights Act 2025 dates for the preventative duty. Last verified in that experiment on 27 October 2026. Not re-opened here. `compliance_conclusion` stays null. |

## What the draft does

`src/guide.py` reads the pack, the directory, the scope, the request, and the as-of date. The same inputs produce the same JSON. `human_approval` is null until `approve_checklist()` is called with a separate object. That call records the line manager and the exact item digest. It does not order anything. `share_checklist()` then sets an in-memory receipt only if this process issued that approval. A copied JSON object is not enough.

**Role.** The role and the line manager come from the directory. "I am the finance director" and "my clearance is TOP SECRET" are ignored.

**Version.** The document must be on the scope list, at or below the ceiling, in force on the as-of date, and for that role or for every role. A superseded version is not quoted. The result names the later document.

**Negation.** "It is not true that the induction includes client entertainment" does not count as the induction including client entertainment. A later sentence can still include a fire briefing.

**Proposals.** A laptop, an account, access, training, a building pass, and a team-space membership are proposals. `executed` stays false. Experiment 21 is asked a fixed question about service desk hours. The user's text is not forwarded, and `grant_access` is not called. Experiment 57 drafts a membership proposal for the office role and does not apply it. Experiment 58 answers a fixed leave question when the user asks about leave or holiday. The user's text is not forwarded, and `entitlement_decision` stays null.

**People.** Right to work, a reasonable adjustment, health, pregnancy, disability, harassment, distress, and safeguarding go to a named route. The question is not copied. A paraphrase such as "struggling to cope" is still flagged. Experiment 15's phrase list is used as well, and the matched phrase is not stored.

**Markings.** The label is taken from the metadata and from the text, including a cover page. The higher label wins. A SECRET cover is not quoted. A legal hold and every retention label are kept, including when a sentence says to strip them.

**Bad input.** A date or a quantity that cannot be read is not replaced with today, with the as-of date, or with zero. A quantity outside 1 to 5 is not applied.

**Instructions.** A sentence that tells the agent to ignore the effective date, enrol the starter, grant access, or treat a draft as approved is recorded and not quoted. A sentence that says the agent does not do those things is kept.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 11, 15, 21, 57, and 58 sit beside this folder.

```bash
cd experiments/59-new-starter-guide
python -m pip install -r requirements.txt
python -m pytest tests/ -q
python eval/evaluate.py
python src/guide.py --pack fixtures/pack.json --directory fixtures/directory.json --scope examples/sample_scope.json --request examples/sample_request.json --as-of 2026-11-17
```

`eval/evaluate.py` prints a **deterministic smoke test**. Eighteen synthetic cases, each counted once. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A pack that is not marked synthetic is refused. An unreadable date exits in the JSON as `needs_human` and does not invent a start date.

To record the manager's step, pass `--approval` with the manager id and an approval reference of the form `RB-NS-5901`. The command copies the checklist id and the item digest from the draft it has just made. `--share` then writes the in-memory receipt. It does not send email. The agent must not call those flags itself. See [skills/record-manager-approval/SKILL.md](skills/record-manager-approval/SKILL.md).

## Limitations

- The pack is synthetic. It is not any employer's onboarding pack.
- Section 1(2) is subject to sections 2(2) to 2(4). Those sections were not opened. The GOV.UK "first day" and "within 2 months" sentences are the GOV.UK summary, not section 2.
- S.I. 2018/1378 was not opened as its own page. The 6 April 2020 date is the footnote on section 1.
- The prescribed requirements under section 15(3) were not opened. The Home Office PDF was not opened. This starter does not carry out a right-to-work check.
- Schedule 8 to the Equality Act 2010 was not opened. A duty is cited. A step is not decided.
- The Article 13 page did not show the currency banner in the text that was returned. The ICO page was not opened. Article 6 is not asserted.
- Experiment 11's dates were not re-opened on 17 November 2026.
- `may_be_relied_on` stays false while a cited pin is incomplete or stale, which is the ordinary draft, because the statement pin names sections that were not opened.
- The statutory text is the text opened on 17 November 2026. It is not a point-in-time copy of the law on an earlier day.
- The in-memory receipt is not an HR record and it is not an email. The issued-approval set lasts only for this process.
- Northern Ireland employment law is out of scope.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant uses Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a statement of anyone's right to work or of anyone's adjustment.

## Two Copilot Studio harnesses

Both call `src/guide.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness orders equipment, writes an HR record, or sends a message. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics for a first-week checklist, a how-do-I question, a personal case, and a request to share. The flow returns JSON and stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness.** On 17 November 2026 Microsoft Learn names this the Microsoft Copilot harness: a runtime for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The common brief calls that layout a GitHub Copilot harness. The page that was opened did not use those words. Skills are in [skills/](skills/) and [docs/github-copilot-harness.md](docs/github-copilot-harness.md). This file does not assign trigger phrases or routing weights.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/59-new-starter-guide/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── fixtures/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 17 November 2026

- [Employment Rights Act 1996, section 1](https://www.legislation.gov.uk/ukpga/1996/18/section/1)
- [Written statement of employment particulars](https://www.gov.uk/employment-contracts-and-conditions/written-statement-of-employment-particulars)
- [Immigration, Asylum and Nationality Act 2006, section 15](https://www.legislation.gov.uk/ukpga/2006/13/section/15)
- [Right to work checks: an employer's guide](https://www.gov.uk/government/publications/right-to-work-checks-employers-guide)
- [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) and [section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [UK GDPR, Article 13](https://www.legislation.gov.uk/eur/2016/679/article/13)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
