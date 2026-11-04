# Experiment 34: EHCP Draft Assembler

Catalogue ID **UK10**. Autonomy **A1**. The catalogue stack is Microsoft Foundry, Azure, and Copilot Studio. This folder does not call Microsoft Foundry or Azure. It ships a Copilot Studio standard harness, a Copilot Studio GitHub Copilot harness, and a Microsoft Foundry note, because every experiment in this repository does.

A starter for a SEND caseworker who has synthetic advice reports and wants them filed under the statutory section headings, with a citation back to the report, and with gaps, conflicts, and unsupported statements flagged. The caseworker authors the final education, health and care plan. The agent does not decide needs, provision, placement, or outcomes, and it does not send the draft.

The filing is the code in `src/assemble.py`. The same bundle and the same as-of date produce the same JSON. Nothing here calls a model or the network.

The organisation in the samples is invented. Northfen Borough Council is not a client. Child A is not a real child. The samples contain no real names.

## The problem

Advice for an education, health and care plan arrives as several reports. A paragraph belongs under the section the advice already names. A sentence that is not in a cited paragraph should not appear as if it were advice. Two reports can describe the same point differently, and the draft should keep both rather than pick one. A draft sent to a parent or young person must not name a school or a type of school.

This starter files only a paragraph the advice tagged. It withholds section I. It lists what is missing. It does not write the plan.

## Who it helps

A SEND caseworker, or a colleague sitting with one, who wants a first filing of synthetic advice before they write the plan in the local authority's own template.

It does not help a team that wants the tool to decide provision, name a placement, or send the plan to a parent or a school.

## Non-goals

- Deciding needs, provision, placement, or outcomes. Those flags stay false.
- Editing the final plan. The caseworker authors the final text. `final_plan_edited` stays false.
- Sending the draft to a parent, a young person, a school, or a local authority system.
- Securing provision. Children and Families Act 2014 s.42 applies where the local authority maintains a plan. This draft is not a maintained plan. `provision_secured` stays false.
- Treating a missing advice report as a finding that the local authority failed regulation 6. Regulation 6(4) is not applied.
- Finding a breach of the 20-week timescale. The marker is arithmetic. `breach_found` stays false.
- Checking the headings against a local template. `agent_checked_template` stays false. The caseworker confirms that check before any local copy.
- Releasing anonymised text. `output_is_anonymised` stays false.
- Recommending autonomy A3, approving an assessment, changing a production record, or spending.
- Calling Microsoft Foundry or Azure. The catalogue names them. This command does not.
- Legal advice, a DPIA, or a statement that a deployment meets UK GDPR or the ICO Children's code.

## What the draft does

`src/assemble.py` reads one JSON bundle. The label is **DRAFT FOR CASEWORKER — NOT A PLAN**.

| Rule | What it does |
|---|---|
| Section letters | Headings follow regulation 12 of the Special Educational Needs and Disability Regulations 2014 (SI 2014/1530). SEND Code of Practice paragraph 9.62 restates the letters and says the format is agreed locally. Paragraph 9.69 is about shorter-term targets. It is not the section list. |
| Placement | A paragraph is filed only under the letter the advice tagged. Untagged text is listed as unplaced and as a gap. The agent does not infer a section from the words. |
| Section I | Quotes tagged I are not copied. The line records the citation and the reason. Children and Families Act 2014 s.38(5). |
| Section K | The advice list is report metadata. Appendices are not attached. |
| Gaps | Missing advice under regulation 6(1)(a) to (e) is a gap. Paragraph (f) is discretionary. Paragraph (g) is required here only when `year_group` is an integer from 9 to 14. Paragraph (h) is a gap only when the bundle lists `requested_further_advice`. An empty section in A, B, C, D, E, F, G, H1, H2, or J is a gap. Empty section B is not a finding of no needs. |
| Conflicts | A structured claim is used only when its value is a substring of a placed or unplaced paragraph. The same key with two different values is one conflict. Both citations are kept. `resolved` stays false. `chosen_value` stays null. |
| Unsupported statements | A candidate statement is not copied into a section. A supported statement is listed and is not a second section line. |
| Stale advice | A report date older than the threshold, default 90 days, is flagged. The quote is still shown. The 90-day window is not a statutory expiry. A future or missing date is not copied. |
| Timescale | Regulation 13(2) is the 20-week limit. This starter counts 20 weeks as 140 days, which is an assumption. `twenty_week_marker_passed` is a marker. Regulation 13(3) exceptions are not applied. Regulation 13(1), the 15-day representation period, is not started because this starter does not send a draft. |
| Identifiers | Experiment 08 `propose` is called with model suggestions off. A paragraph with an applied deterministic finding is withheld. The redacted text is not copied. |
| Injection | A matching sentence is not placed. Payload keys are stripped and not echoed. `followed` stays false. A sentence that already says "do not" is not a hit. |
| Export | A local copy is included only when a separate sign-off object passes. The string "true" does not pass. The sign-off is not stored. `final_text` on the sign-off is not copied. The label on that copy is **LOCAL COPY FOR THE CASEWORKER — NOT SENT**. |

Free text cannot set `needs_decided`, `provision_decided`, `placement_decided`, `outcomes_decided`, `exported`, or `caseworker_signoff`.

The sample, case `SYN-EHCP-001`, child reference Child A, year group 4, request received 3 August 2026, as-of date 4 November 2026, places 7 quotes. Days since the request are 93, so the 20-week marker has not passed and `breach_found` is false. There is one unresolved conflict on `instruction_following`. One unsupported statement is absent from the JSON. Section I has no lines and one withheld citation. `do_not_rely` is false on that run. Those figures are the fixture. They are not a plan and they are not a tribunal outcome.

## How this differs from Experiments 08, 12, and 33

| Experiment | What it does | What this starter does |
|---|---|---|
| 08, UK PII redaction gateway | Proposes redaction of UK identifier patterns. | Calls `propose`. Does not copy the detectors. Sets `output_is_anonymised` to false. Does not release text. If Experiment 08 is missing, the assembler stops and does not invent a redactor. |
| 12, document intake | Inventories a batch and can suggest a purpose. | Does not call intake. Intake does not file SEND advice under sections A to K. |
| 33, case-bundle summariser (UK09) | Summarises a bundle for a reader, where that folder exists. | Does not narrate. Files advice the report already tagged, withholds section I, and blocks export. Detects a `33-*` folder if one is present and does not import it. |

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only. Experiment 08 has to sit beside this folder.

```bash
cd experiments/34-ehcp-draft-assembler
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/assemble.py --bundle examples/sample_bundle.json --as-of 2026-11-04
```

`eval/evaluate.py` prints a **deterministic smoke test**. It has 13 cases. `eval/smoke_report.json` is that run. On the fixtures committed with this folder, 13 passed and the agreement rate is 100.0. The summary does not add quote counts together. `northfen-child-a` and `northfen-child-a-again` each report 7 placed quotes. Those two sevens are not added. It is not a model score and it is not an education, health and care plan. A live Microsoft Foundry run has not been done.

A stale-data check, without editing the advice:

```bash
python src/assemble.py --bundle examples/sample_bundle.json --as-of 2027-05-04 --stale-after-days 90
```

A local copy, still not a send:

```bash
python src/assemble.py --bundle examples/sample_bundle.json --as-of 2026-11-04 --export --signoff examples/sample_signoff.json
```

Passing `--decide-needs`, `--decide-provision`, `--decide-placement`, `--decide-outcomes`, `--edit-final-plan`, `--send-to-parents`, `--send-to-school`, `--write-la-system`, or `--secure-provision` is a mistake. The command exits 2 and does not write a file. `--export` without a passing sign-off also exits 2 and writes nothing.

The exit code is 0 when the JSON is produced, including when advice is stale or a gap is open. That is not a decision and it is not sign-off. The caseworker authors the final text.

## Sources and currency

These pages were opened on **4 November 2026**. `src/sources.py` stores the sentences this starter relies on. No rate, pack size, or diagram number is copied. The ICO Children's code page returned 403 and was not opened. The Copilot Studio cost-management page and the Microsoft Foundry cost page were not opened for this experiment. Sentences from those pages are not repeated here as verified.

| ID | Page | Last verified |
|---|---|---|
| `cfa-s36` | [Children and Families Act 2014, s.36](https://www.legislation.gov.uk/ukpga/2014/6/section/36) | 4 November 2026 |
| `cfa-s37` | [Children and Families Act 2014, s.37](https://www.legislation.gov.uk/ukpga/2014/6/section/37) | 4 November 2026 |
| `cfa-s38` | [Children and Families Act 2014, s.38](https://www.legislation.gov.uk/ukpga/2014/6/section/38) | 4 November 2026 |
| `cfa-s42` | [Children and Families Act 2014, s.42](https://www.legislation.gov.uk/ukpga/2014/6/section/42) | 4 November 2026 |
| `cfa-ss37-49` | [Children and Families Act 2014, ss.37 to 49](https://www.legislation.gov.uk/ukpga/2014/6/part/3/crossheading/education-health-and-care-plans) | 4 November 2026 |
| `send-reg-6` | [SEND Regulations 2014, reg. 6](https://www.legislation.gov.uk/uksi/2014/1530/regulation/6) | 4 November 2026 |
| `send-reg-10` | [SEND Regulations 2014, reg. 10](https://www.legislation.gov.uk/uksi/2014/1530/regulation/10) | 4 November 2026 |
| `send-reg-12` | [SEND Regulations 2014, reg. 12](https://www.legislation.gov.uk/uksi/2014/1530/regulation/12) | 4 November 2026 |
| `send-reg-13` | [SEND Regulations 2014, reg. 13](https://www.legislation.gov.uk/uksi/2014/1530/regulation/13) | 4 November 2026 |
| `send-code-2015` | [SEND code of practice: 0 to 25 years](https://www.gov.uk/government/publications/send-code-of-practice-0-to-25) | 4 November 2026 |
| `ukgdpr-art-8` | [UK GDPR, Article 8](https://www.legislation.gov.uk/eur/2016/679/article/8) | 4 November 2026 |
| `ukgdpr-art-9` | [UK GDPR, Article 9](https://www.legislation.gov.uk/eur/2016/679/article/9) | 4 November 2026 |
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 4 November 2026 |
| `cs-billing-overview` | [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) | 4 November 2026 |
| `cs-standard-licensing` | [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) | 4 November 2026 |
| `ico-childrens-code` | ICO Children's code, services covered | Not opened |

Threshold used by the tests: older than 90 days from `last_verified`. The catalogue-boundary row and the ICO row are not stale-tested.

What those pages said on that open:

- Section 36 is the EHC needs assessment. This starter does not decide whether to assess.
- Section 37(2) is what an EHC plan specifies. This starter does not decide that section 37(1) applies.
- Section 38(5) says the draft sent to the parent or young person must not name a school or other institution, or specify a type of school or other institution.
- Section 42 is the duty to secure specified special educational provision, and for the responsible commissioning body to arrange specified health care provision, where the local authority maintains a plan.
- The crossheading page includes sections 37 to 49: content, the draft, finalising, section 41 approval, the duty to secure provision, the duty to admit, reviews, ceasing to maintain, maintaining after 25, transfer, release from detention, and personal budgets. This starter does not take those steps. Section 36 was opened as its own page.
- Regulation 6(1)(a) to (e) are the required advice categories used as gaps. Paragraph (f) is discretionary. Paragraph (g) applies in or beyond year 9. Paragraph (h) is advice the parent or young person reasonably requests. This starter does not decide that a request was reasonable. Regulation 6(2) and regulation 6(1)(b)(iv) are not applied.
- Regulation 10(4)(a) to (d) sets reasons a time limit need not be met. Regulation 13(3) applies those reasons to the 20-week limit. This starter does not apply them.
- Regulation 12 sets the section letters. Regulation 13(2) is the 20-week limit, counted from the section 36(1) request or from becoming responsible under section 24. This starter only has `request_received`. It does not have a section 24 date.
- The GOV.UK publication page was last updated on 12 September 2024 and points at the January 2015 code. Paragraph 9.62 is the section list. Paragraph 9.63 is preparation for adulthood from year 9. Paragraph 9.64 says outcomes are specified in section E. This assembler does not write an outcome.
- UK GDPR Article 8 sets the age at 13 in the UK text and applies where Article 6(1)(a) consent is the basis for an information society service offered directly to a child. Article 8(4) excludes preventive or counselling services. Article 9(1) covers data concerning health. No Article 9(2) condition is asserted.
- The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to the GitHub Copilot service. The page does not mark that harness as preview. It describes skills, memory, file creation, and a sandbox. The standard harness follows the topics and rules the maker defines. Skills and memory are listed as "Not a focus" for the standard harness.
- The billing overview says that, for GitHub Copilot harness experiences, Copilot Credits are charged for large language model tokens, tools including knowledge and MCP, and the harness. The standard harness starts billing after publish. The GitHub Copilot harness charges credits from the moment you start building, including testing. A diagram of ranges was on the page. No number from it is copied.
- The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. The same page says that, with that licence, classic answers, generative answers, or Microsoft Graph tenant grounding in Copilot Chat, Teams, or SharePoint do not count against the message pack or meter. Those two sentences are not merged. No pack size and no meter rate is copied. The page says the common currency changed from messages to Copilot Credits on 1 September 2025, and that the quantity per prepaid pack and the pay-as-you-go rate did not change. The quantity itself is not stated here.

A Learn page on generative orchestration was not opened. How a tenant selects a topic is unverified. This starter does not describe topic selection as a weight on a phrase. Where generative orchestration is on, selection is by the topic description, and that behaviour was not re-checked on 4 November 2026.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. |
| Synthetic fixtures | `examples/` and `eval/synthetic_dataset.json`. No real personal data. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `permissions.yaml`, the same file as `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret, licence, and brand checks | `.github/workflows/experiment-34-tests.yml`. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |
| Honest limitations | This README and `src/assemble.py`. |

## Limitations

- The caseworker authors the final text. This file is not the final plan.
- Section headings must be checked against the local authority's own template. Paragraph 9.62 says the format is agreed locally. The code's wording follows regulation 12, which differs in places from the code of practice (for example "health care needs" and "health needs").
- Twenty weeks is counted as 140 days. That arithmetic is not in the regulations. A marker is not a finding of breach. Regulation 13(3) exceptions are not applied. This starter does not know a section 24 date.
- The 90-day window is a freshness flag. It is not a statutory expiry of advice.
- A missing advice type is a gap in this file. It is not a finding that regulation 6 was breached. Regulation 6(4), regulation 6(2), and regulation 6(1)(b)(iv) are not applied.
- Experiment 08 does not detect a name written out in words. `output_is_anonymised` stays false. The output is not anonymised.
- A negation in the same sentence can hide an instruction. A paraphrase can be missed.
- The ICO Children's code page was not opened. Whether it applies to a later portal is unverified. The data protection officer decides. This starter does not choose an Article 6 basis and does not assert an Article 9(2) condition.
- Experiment 12 and Experiment 33 are not called. A later Foundry host that assigned section tags would be deciding needs or provision. That host is not built. If tags were ever proposed they would stay untrusted, they would still have to pass the citation test, and section I would stay blank.
- The cost-management page and the Microsoft Foundry cost page were not opened for this experiment. Prompt Shields, Entra Agent ID, Conditional Access, a data loss prevention policy, Key Vault, Purview, and Application Insights were not opened. They are unverified.
- `eval/smoke_report.json` is a deterministic smoke test of 13 synthetic cases, 13 passed, agreement 100.0 on those fixtures. It is not a model score. The two cases that each place 7 quotes are not summed.
- The catalogue score for UK10 in the planning catalogue is not repeated here and it is not a measurement.
- Planning research names a public report about a council's EHCP work. That report was not re-opened for this experiment and is not cited as verified.

This is not legal advice and it is not a statement that a deployment meets UK GDPR or the SEND Code of Practice.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.

## Project structure

```
experiments/34-ehcp-draft-assembler/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── schema/
├── src/
├── skills/
├── copilot-studio/
├── docs/
├── eval/
├── examples/
└── tests/
```

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
