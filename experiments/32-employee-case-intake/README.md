# Experiment 32: Employee Case Intake Agent

Catalogue ID **H009**. Autonomy **A1**. An HR officer confirms the classification and the routing. The catalogue stack is Copilot Studio and Power Platform. What you can run today is Python in the standard library. It calls [Experiment 15](../15-vulnerability-urgency-scanner/) for urgency indicators, [Experiment 12](../12-document-intake/) when a case has text attachments, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. It does not copy those detectors. No model is called and no network call is made. See [docs/foundry.md](docs/foundry.md).

The UK angle is case intake for a UK employer or a public body: grievance, absence, flexible working, whistleblowing or protected disclosure, and harassment. Samples are synthetic. No real person is in the fixtures.

[Experiment 11](../11-era-2025-hr-assistant/) (UK03) is the harassment-prevention and commencement checklist. This experiment does not call it and does not decide reasonable steps or all reasonable steps.

## The problem

An HR officer receives a free-text note and has to choose a category, notice whether the text looks urgent, find the statutory or Acas sentence that mentions time, and name a route. Doing that inside a chat can turn a keyword into a finding that harassment is made out, or that a disclosure is protected, or into an email to the manager named in the note.

This starter only proposes. The officer confirms.

## Who it helps

**An HR officer** who already has the note. They see a proposed category, an urgency flag, quoted time references, and a proposed route. They confirm the classification and the routing outside the agent.

**The employee and the manager** are not contacted. The draft is not a reply and not advice on the merits.

**A data protection officer** who needs the special-category handling written down. The narrative is not stored. No Article 9 condition is asserted. Where the text uses whistleblowing language, the routing summary omits the narrative and names the people who must not be notified from this draft.

**An organisation** that wants the approval points written down before anyone connects an HR system. Writes and sends stay disabled.

It does not help a team that wants the tool to decide a grievance, calculate a tribunal limit, or update the HR system.

## Non-goals

- Deciding an outcome of a grievance, an absence, a flexible-working request, a harassment complaint, or a disclosure.
- Advising on the merits.
- Deciding that Equality Act 2010 section 26 is met, or that a disclosure is a protected disclosure under Employment Rights Act 1996 section 43A.
- Contacting the employee, a line manager, the subject of a disclosure, Acas, a tribunal, or a prescribed person.
- Writing to an HR system, Dataverse, SharePoint, or a mailbox. A confirmation recorded by the test helper still does not write.
- Asserting a UK GDPR Article 6 basis or an Article 9 condition, or deciding that Data Protection Act 2018 Schedule 1 paragraph 1 is met.
- Calculating the last day of an Employment Rights Act 1996 section 80G decision period, or any tribunal time limit.
- Applying the Great Britain sources to Northern Ireland, or stating Northern Ireland law.
- Re-implementing Experiment 08, Experiment 12, or Experiment 15.
- Autonomy A3. There is no path on which the agent confirms, contacts, or writes.

## What the draft does

`src/draft.py` reads one JSON case and writes one JSON document. The label is `DRAFT FOR HR CONFIRMATION`. The same case and the same as-of date produce the same JSON. `classification.decided` is false. `hr_confirmation.classification_confirmed` and `routing_confirmed` are false. `outcome` and `merits_advice` are null. `actions_taken` is empty. `narrative_stored` is false. The draft keeps a SHA-256 and a character count.

**Category.** A closed keyword list proposes `grievance`, `absence`, `flexible_working`, `protected_disclosure`, or `harassment`. One match proposes that category and its route. A tie is `unresolved` and the route is `hr_officer_to_classify`, unless protected-disclosure language matched. That language keeps the proposed route as `designated_whistleblowing_officer` and does not decide that the disclosure is protected. No match is `unresolved`. A short negation window skips a keyword. Instruction sentences are blanked before the count. HTML comments and text after a form feed are dropped. Zero-width characters are stripped.

**Urgency.** Experiment 15 `scan()` runs on the narrative when it is within the character cap. A self-harm or safeguarding indicator proposes `same_day_officer_review`. A deadline or financial-hardship indicator proposes `time_sensitive_officer_review`. Otherwise the flag is `routine_officer_review`. `queue_priority_changed` and `person_labelled_vulnerable` stay false. Matched phrases are not copied into this draft.

**Time references.** The draft quotes pinned text. `days_encoded` is null. Acas Code paragraph 33 says a formal meeting should be arranged without unreasonable delay. It does not state a number of days. The non-statutory guide's "ideally within five working days" is not encoded. Paragraph 38's five working days is a postponement where a companion is unavailable, and it is not used as a meeting deadline. Section 80G(1B)(a) states a period of two months beginning with the date the application is made. The last day is not calculated. `application_made_on` is used only when the officer supplies that field. A date written in the narrative is ignored. No statutory response period is encoded for absence. Statutory sick pay and fit-note rules were not opened.

**Whistleblowing confidentiality.** `identity_in_routing_summary` and `narrative_in_routing_summary` are false. The summary says not to notify the employee, a line manager, or the subject of the disclosure. Section 43J is quoted when the Great Britain sources apply. `section_43j_applied_as_a_finding` and `protected_disclosure_decided` stay false.

**Special category.** Indicators can mark health, sex life or sexual orientation (explicit phrases only), racial or ethnic origin, religion, or trade union membership. A sexual-harassment keyword can set `sexual_harassment_may_engage_article_9`. That is not a finding that Article 9 sex-life data is present. `article_9_condition_asserted` is false. `schedule_1_paragraph_1_met` is null. `appropriate_policy_document_checked` is false.

**Article 22.** The legislation.gov.uk page for UK GDPR Article 22 shows the article as substituted. Data (Use and Access) Act 2025 section 80 substitutes Articles 22A to 22D. The draft quotes Article 22A(1). It sets `solely_automated_decision` and `significant_decision` to false because an HR officer confirms classification and routing. It does not quote the pre-substitution Article 22 text as current law.

**Jurisdiction.** `england`, `wales`, `scotland`, `england_and_wales`, and `great_britain` use the Great Britain extracts. `northern_ireland` does not. Equality Act 2010 section 26, Employment Rights Act 1996 Part IVA, and section 80G are marked England, Wales, and Scotland on the pages opened. The Acas Code HTML page did not state a Northern Ireland extent, so the Code is not applied to `northern_ireland` either. A missing jurisdiction still quotes the Great Britain sources and says that is not a finding that the employment is in Great Britain.

**PII and attachments.** Experiment 08 `propose()` runs with caller `exp-32-employee-case-intake`, model suggestions off, and `reversible` false. This draft keeps entity types and hashes, not the redacted text. `output_is_anonymised` stays false. Experiment 08 does not redact names, email addresses, or telephone numbers. An optional attachment batch is passed to Experiment 12 `intake()` with `requested_purpose` `general_records`. File bodies and filenames are not copied. `files_confirmed` and `purpose_confirmed` stay false.

**Stale sources.** Extracts are pinned on 4 November 2026. If the as-of date is more than `stale_after_days` after that pin, `sources_stale` is true. The default window is 90 days. A gap of exactly 90 days is not stale. A sentence in the narrative does not refresh the pin. The test helper `record_hr_confirmation` refuses `confirm_classification_and_routing` while sources are stale unless `acknowledge_stale` is true. The skills say the agent must not call that function. The tool schema sets `callable_by_agent` to false.

**Prompt injection.** Phrases in the body, in an HTML comment, after a form feed, after trailing blank lines, or split by zero-width characters are recorded. `followed` is false. Payload keys that try to set the category, the route, an outcome, a contact, or a write are stripped.

**Oversized text.** A narrative over 20,000 characters is not classified and not scanned. The urgency flag is `not_scanned`. A safeguarding phrase in that text is not detected. That is a limitation, not a clean result.

**Human steps, outside `draft_case()`.** `record_hr_confirmation` accepts only the role "HR officer", and only `confirm_classification_and_routing` or `return_for_edit`. A route such as `line_manager` is rejected. After confirmation, `write_hr_system`, `contact_employee`, `contact_manager`, `decide_outcome`, `advise_on_merits`, `send_external`, `approve_case`, and `reject_case` still raise `CaseForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 15 must sit beside this folder, which they do in this repository.

```bash
cd experiments/32-employee-case-intake
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/draft.py --input examples/sample_case.json --as-of 2026-11-04
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. `total_cases` is the number of cases. It is not the number of checks inside those cases. It is not a model score. A live Microsoft Foundry run has not been done.

A case that is not marked synthetic is refused. The exit code is 2. The refusal does not echo the narrative. Exit code 0 means a draft was produced, including when sources are stale or an instruction was detected. Those are findings, not an HR confirmation.

## Limitations

- **Keywords misclassify.** Two hits tie as `unresolved`. A genuine grievance that does not use the listed words is `unresolved`. A negation of about 16 characters is skipped. A longer denial is not.
- **A narrative over 20,000 characters is not scanned.** An instruction or a safeguarding phrase in that text is not detected.
- **No day is calculated.** "Without unreasonable delay" is not turned into a date. The two-month period in section 80G(1B)(a) is quoted and not applied as a last day. Tribunal limits are not calculated.
- **Absence has no encoded response period.** Statutory sick pay and fit-note rules were not opened.
- **The Acas Code in force on the pin date is the Code published 11 March 2015, paragraphs 1 to 47.** A draft updated code was in consultation. It is not applied. Trade Union and Labour Relations (Consolidation) Act 1992 sections 199 and 207A were not opened. The foreword's sentence on awards adjustable by up to 25 per cent is quoted from the Code. It is not a finding under section 207A.
- **Section 43B(5) still says a relevant failure means a matter within paragraphs (a) to (f).** Paragraph (da), sexual harassment, was inserted on 6 April 2026. This starter does not decide whether (da) is inside that cross-reference. It does not decide reasonable belief or public interest.
- **Section 80G shows both an older and a newer refusal test** because the newer text is in force for specified purposes. SI 2026/3 was not opened. Refusal grounds are not applied.
- **Northern Ireland law is not stated.** The Great Britain extracts are not applied when `jurisdiction` is `northern_ireland`.
- **No Article 9 condition is asserted.** Schedule 1 paragraph 39 was not opened. An appropriate policy document was not checked.
- **Experiment 08's misses are inherited.** Names, email addresses, and telephone numbers are not redacted. This draft does not repeat the narrative. It also does not claim the text was anonymised.
- **Experiment 15 phrases are not stored here.** Only indicator categories are kept.
- **The smoke test is not a model score.**
- **Recording a confirmation is not a write.** The helper exists so a test can show the role check. It is not a tool of the agent.

This is not legal advice, a DPIA, or a statement that a deployment is compliant. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `draft_case()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness confirms a classification, contacts anyone, or writes. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The officer pastes a case, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. Skills are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Generative orchestration, where the tenant uses it, selects a skill from its description. These skills do not assign trigger phrases or routing weights. Microsoft bills that harness in Copilot Credits. Prices were not copied. The harness overview, retrieved 4 November 2026, did not mark the harness itself as preview. The page had no last-updated date in the text retrieved that day.

The permissions manifest for this experiment is [agent-manifest.yaml](agent-manifest.yaml). That is the repository format. It is validated against `schemas/agent-manifest.schema.json`.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md). Flow: [copilot-studio/power-automate-flow.md](copilot-studio/power-automate-flow.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry, described and not called: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/32-employee-case-intake/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── case_categories.py
│   ├── case_injection.py
│   ├── case_sources.py
│   └── draft.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 4 November 2026

Legislation.gov.uk currency lines on these pages often say "on or before" 2 or 3 November 2026. Retrieval for this pin was 4 November 2026.

- [Acas Code of Practice on disciplinary and grievance procedures](https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures/html), published 11 March 2015. Paragraphs 1 to 47 are the Code.
- [About the Code](https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures), which says Acas will update the Code. The [draft code in consultation](https://www.acas.org.uk/about-us/acas-consultations/code-of-practice-disciplinary-grievance-2026/draft-code) was not applied.
- [Employment Rights Act 1996, Part IVA](https://www.legislation.gov.uk/ukpga/1996/18/part/IVA). Extent England, Wales, and Scotland. Headings 43A to 43H, 43FA, 43J, 43K, 43KA, and 43L. No section 43I on that page.
- [Section 43A](https://www.legislation.gov.uk/ukpga/1996/18/section/43A), [section 43B](https://www.legislation.gov.uk/ukpga/1996/18/section/43B), [section 43C](https://www.legislation.gov.uk/ukpga/1996/18/section/43C), [section 43J](https://www.legislation.gov.uk/ukpga/1996/18/section/43J), and [section 80G](https://www.legislation.gov.uk/ukpga/1996/18/section/80G).
- [Equality Act 2010, section 26](https://www.legislation.gov.uk/ukpga/2010/15/section/26). Extent England, Wales, and Scotland.
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5), [Article 9](https://www.legislation.gov.uk/eur/2016/679/article/9), and the [Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22) page, which shows the article as substituted.
- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80), which substitutes Articles 22A to 22D.
- [Data Protection Act 2018, section 10](https://www.legislation.gov.uk/ukpga/2018/12/section/10) and [Schedule 1, paragraph 1](https://www.legislation.gov.uk/ukpga/2018/12/schedule/1/paragraph/1). Paragraph 39 was not opened.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 4 November 2026. Billing articles and the skills upload schema were not opened.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
