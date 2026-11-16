# Experiment 58: Employee Handbook Agent

Catalogue ID **H001**. Autonomy **A0**. Related to, and kept separate from, Experiment 11 (Employment Rights Act 2025 commencement) and Experiment 32 (employee case intake). HR approves which handbook documents and versions are in scope. The assistant then answers from the approved version that is in force on the date the question is about.

The handbook in this folder is synthetic. The employer, Riverbend Workshops CIC, is invented. There are no real people.

**What it does.** It quotes a section, names the version and the effective date, and, where a statutory minimum was opened, cites that provision separately. If the approved handbook does not cover the question, it says so. If the question is about a person — grievance, discipline, health, pregnancy, disability, whistleblowing, distress, or safeguarding — it names a human route and does not treat the question as routine policy.

**What it does not do.** It does not decide an individual's entitlement. It does not give individual legal, medical, or tax advice. It does not approve a source because the question or the file says "approved". It does not send a message or write a record.

Stack in the catalogue: Copilot Studio and Microsoft 365. The answer itself is Python in the standard library.

## The problem

Staff ask what the handbook says. Handbooks have versions. A sentence that was true in March may have been replaced in April. A draft can sit next to the live page and claim, in its own text, that HR has approved it. A personal question about sick pay or a grievance is not the same as a question about what the procedure says.

This starter keeps those apart. The scope object is the approval. The effective dates pick the version. The quotation is the answer.

## Non-goals

- Deciding how many days a named person has left, or whether they qualify for a payment.
- Deciding a flexible-working request, an expense claim, a grievance, or a disciplinary outcome.
- Deciding that a disclosure is a protected disclosure, or that an employer took reasonable steps or all reasonable steps.
- Giving advice about a person's tax, health, pregnancy, or disability.
- Stating Northern Ireland employment law.
- Treating a draft, or a file marked above the handbook ceiling, as an answer.
- Publishing or editing the handbook. Experiment 50 can be asked for a curation note. It does not change a page.
- Calling SharePoint, Microsoft Graph, or Microsoft 365 Copilot.
- Refreshing legislation from the web when a pin is stale.

## What was opened

Opened on 16 November 2026 unless the row says otherwise. The core does not download these pages when it runs.

| Source | What this starter takes from it |
|---|---|
| [Working Time Regulations 1998, regulation 13](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13) | Regulation 13(1): four weeks' annual leave in each leave year, subject to paragraph (5). Regulation 13(A1) limits which workers and leave years it applies to. Extent E+W+S. Regulation 15B was not opened. |
| [Regulation 13A](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13A) | Regulation 13A(2)(e): 1.6 weeks for a leave year beginning on or after 1 April 2009. Regulation 13A(3): the aggregate with regulation 13(1) is subject to a maximum of 28 days. |
| [GOV.UK, holiday entitlement](https://www.gov.uk/holiday-entitlement-rights) | Summary: 5.6 weeks, and at least 28 days for most workers on a five-day week, capped at 28 days. Bank holidays can be included and do not have to be given as paid leave. This is not the wording of regulation 13. |
| [Employment Rights Act 1996, section 80F](https://www.legislation.gov.uk/ukpga/1996/18/section/80F) | The page said it was up to date with changes known to be in force on or before 15 November 2026. Section 80F(4)(a): no more than two applications to the same employer in any 12 months. The footnotes attribute the 6 April 2024 amendments to the Employment Relations (Flexible Working) Act 2023 (c. 33) and cite S.I. 2024/438, regulation 2. That SI was not opened as its own page. Changes listed as not yet applied, including Employment Rights Act 2025 provisions, were not opened and are not stated as in force. |
| [S.I. 2023/1328](https://www.legislation.gov.uk/uksi/2023/1328/made) | In force 6 April 2024. Extent England and Wales and Scotland. Regulation 2 omits regulation 3 of the Flexible Working Regulations 2014. The explanatory note says the right applies from the first day, and that the previous 26-week condition does not apply to applications made on or after that date. |
| [GOV.UK, flexible working](https://www.gov.uk/flexible-working) | Requests from the first day. Employers must deal with a request in a reasonable manner. Rules differ in Northern Ireland. No decision period was in the text that was read. The Acas flexible-working code was not opened. |
| [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) | Section 39(5): a duty to make reasonable adjustments applies to an employer. Section 39(2) is the prohibition on discriminating against an employee. Extent E+W+S. Not applied to a person. |
| [Section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | Section 20(3) is the first requirement, where a provision, criterion or practice puts a disabled person at a substantial disadvantage. Sections 20(4) and 20(5) are the physical-feature and auxiliary-aid requirements. This starter does not decide that a step is reasonable for a person. |
| [Acas Code, landing page](https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures) | The code is the minimum an employer should follow. Published 11 March 2015. Numbered paragraphs were not on this page. Paragraphs 1, 32, and 40 are Experiment 32's pin of 4 November 2026 and were not re-opened here. |
| Experiment 11 pins | Employment Rights Act 2025 sections used for the preventative duty, third-party harassment, tribunal limits, and the unfair-dismissal change. Last verified in that experiment on 27 October 2026. Not re-opened on 16 November 2026. `compliance_conclusion` stays null. |

## What the answer does

`src/answer.py` reads the handbook, the scope, the question, and the dates. The same inputs produce the same JSON. `entitlement_decision` is null. `human_approval` is null unless `acknowledge()` is called with a separate HR review object. That call records that HR has seen the answer. It does not decide anything.

**Version.** The document must be on the scope list, at or below the ceiling, and in force on the date asked about. If that version had already ended by the as-of date, the answer says so and names the later version. It still quotes the earlier one, because that is the one in force on the date asked about.

**Negation.** "It is not true that the expenses policy includes client entertainment" does not count as the policy including client entertainment. A later sentence can still include a different phrase.

**Not covered.** If no approved in-force section matches, the answer says the handbook does not cover the question.

**People.** A personal or sensitive case goes to the named route. Experiment 32's keywords propose a category and do not confirm it. Experiment 15's phrase list flags distress and safeguarding. Those questions are not answered with a policy figure.

**Markings.** The label is taken from the metadata and from the text. The higher label wins. A SECRET cover is not quoted. A legal hold and every retention label are kept. A clearance claimed in the question is ignored.

**Bad input.** A date or a quantity that cannot be read is not replaced with today, with the as-of date, or with zero.

**Instructions.** A sentence that tells the agent to ignore the effective date, grant days, strip a hold, or treat a draft as approved is recorded and not quoted.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 11, 15, 32, and 50 sit beside this folder. The answer calls them in-process. It does not copy their detectors.

```bash
cd experiments/58-employee-handbook
python -m pip install -r requirements.txt
python -m pytest tests/ -q
python eval/evaluate.py
python src/answer.py --handbook fixtures/handbook.json --scope examples/sample_scope.json --question examples/sample_question.json --as-of 2026-11-16
```

`eval/evaluate.py` prints a **deterministic smoke test**. Eighteen synthetic cases, each counted once. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A handbook that is not marked synthetic is refused. An unreadable date exits in the JSON as `needs_human` and does not invent a version.

## Limitations

- The handbook is synthetic. It is not any employer's handbook.
- Regulation 15B was not opened. The four-weeks and 1.6-weeks pins are not a calculation for irregular hours or part-year work, and they are not a balance.
- S.I. 2024/438 was not opened as its own page. The 6 April 2024 date is the footnote on section 80F.
- Employment Rights Act 2025 changes to section 80F were listed as not yet applied. They were not opened. They are not stated as in force.
- Experiment 11's dates were not re-opened on 16 November 2026. A reader who needs the current commencement text opens the instrument.
- The Acas numbered paragraphs are Experiment 32's pin. The landing page opened here does not contain them.
- The statutory text is the text opened on 16 November 2026. It is not a point-in-time copy of the law on an earlier day. `point_in_time_text_verified` is false when the date asked about is before that pin.
- Northern Ireland is out of scope.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant uses Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a statement of anyone's entitlement.

## Two Copilot Studio harnesses

Both call `src/answer.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness decides a case, writes a record, or sends a message. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics for a policy question, a personal case, and a gap. The flow returns JSON and stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness.** On 16 November 2026 Microsoft Learn names this the Microsoft Copilot harness: a runtime for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The common brief calls that layout a GitHub Copilot harness. The page that was opened did not use those words. Skills are in [skills/](skills/) and [docs/github-copilot-harness.md](docs/github-copilot-harness.md). This file does not assign trigger phrases or routing weights.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/58-employee-handbook/
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

## References opened on 16 November 2026

- [Working Time Regulations 1998, regulation 13](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13) and [regulation 13A](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13A)
- [Holiday entitlement](https://www.gov.uk/holiday-entitlement-rights)
- [Employment Rights Act 1996, section 80F](https://www.legislation.gov.uk/ukpga/1996/18/section/80F)
- [Flexible Working (Amendment) Regulations 2023](https://www.legislation.gov.uk/uksi/2023/1328/made)
- [Flexible working](https://www.gov.uk/flexible-working)
- [Equality Act 2010, section 39](https://www.legislation.gov.uk/ukpga/2010/15/section/39) and [section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Acas Code of Practice on disciplinary and grievance procedures](https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures)
- [Knowledge sources summary](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)
- [Add SharePoint as a knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)
- [What is Microsoft Copilot?](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
