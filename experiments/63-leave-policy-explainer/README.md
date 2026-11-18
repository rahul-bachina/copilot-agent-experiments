# Experiment 63: Leave Policy Explainer

Catalogue ID **H006**. Autonomy **A0**. The assistant explains a synthetic employer leave policy and a curated statutory baseline. It quotes the policy section, its effective date, and the statutory source. It does not decide entitlement, approve leave, book leave, record leave, or calculate pay. Lindenmere Community Trust is invented.

The core is Python in the standard library. It calls [Experiment 58](../58-employee-handbook/) for version dates, negation, markings, and masking, and for one fixed handbook question whose answer is not copied. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) for identifier counts only. It calls [Experiment 03](../03-agent-inventory-atrs-assurance/) to validate the manifest and to show that the generator will not mark a manifest approved. A user can run it without a tenant.

## The problem

A leave policy can be superseded, past review, or a draft that tells the reader to ignore the effective date. A statutory page can be only partly in force, or not opened at all. A question can ask "am I entitled" when the facts are not in the file, or it can be a disclosure that should go to a person. Those are the failures this starter is built to show rather than to paper over.

## Non-goals

- Deciding whether a person is entitled to leave, or who qualifies.
- Approving a policy version, booking leave, or recording leave.
- Calculating pay, or stating a statutory pay rate that was not copied from a GOV.UK rates page for a named tax year.
- Treating "approved", a role, or a clearance inside the question as the scope or as a seen-step.
- Trusting a self-declared role. The directory is the check.
- Coercing an unreadable date or balance to today, to zero, or to another default.
- Dropping a sensitivity marking, a retention label, or a legal hold. A SECRET cover is withheld. The higher marking wins.
- Following instructions embedded in policy text.
- Counting a denied sentence as an inclusion.
- Answering Northern Ireland employment law. The pages that were opened are marked England and Wales and Scotland, or they say the rules differ.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 18 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`. A quote is the words on the page. A figure that was not on that page is not stated. No statutory pay rate is stated.

| Source | What this starter takes from it |
| --- | --- |
| [Working Time Regulations 1998, regulation 13](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13) | Regulation 13(1): four weeks' annual leave in each leave year, subject to paragraph (5). Regulation 13(A1) limits which leave years and which workers the regulation applies to, and names regulation 15B. Regulation 15B was not opened. Extent England and Wales and Scotland. The page said there were no known outstanding effects, and also that revised legislation on the site may not be fully up to date. |
| [Regulation 13A](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13A) | 1.6 weeks in any leave year beginning on or after 1 April 2009. The aggregate of that paragraph and regulation 13(1) is subject to a maximum of 28 days. |
| [Holiday entitlement](https://www.gov.uk/holiday-entitlement-rights) | 5.6 weeks' paid holiday a year. Most workers who work a 5-day week must receive at least 28 days' paid annual leave a year. Statutory paid holiday entitlement is limited to 28 days. An employer can include bank holidays as part of statutory annual leave. Bank or public holidays do not have to be given as paid leave. An employer can choose to offer more leave than the legal minimum. This is a GOV.UK summary, not regulation 13. No holiday-pay rate was copied. |
| [Employment Rights Act 1996, section 71](https://www.legislation.gov.uk/ukpga/1996/18/section/71) | Ordinary maternity leave of at least 26 weeks, by regulations. The Maternity and Parental Leave etc. Regulations 1999 were not opened. This starter does not state 52 weeks. No statutory maternity pay rate. The page said it was up to date with changes known to be in force on or before 18 November 2026, and that there are changes that may be brought into force at a future date. |
| [Section 73](https://www.legislation.gov.uk/ukpga/1996/18/section/73) | An additional maternity leave period is a period calculated in accordance with regulations. No week count is stated. |
| [Section 75A](https://www.legislation.gov.uk/ukpga/1996/18/section/75A) | Ordinary adoption leave is calculated by regulations. No week count. No statutory adoption pay rate. |
| [Section 75E](https://www.legislation.gov.uk/ukpga/1996/18/section/75E) | A power to make regulations for shared parental leave. The week count was not on the page. This starter does not state 50 weeks. No shared parental pay rate. |
| [Section 76](https://www.legislation.gov.uk/ukpga/1996/18/section/76) | Unpaid parental leave of at least three months, without prejudice to ceasing to satisfy conditions or a transfer. Section 76(1)(a) is shown as omitted. The omitted words were not read. |
| [Section 80A](https://www.legislation.gov.uk/ukpga/1996/18/section/80A) | At least two weeks' paternity leave. Section 80A(4) still requires the leave before the end of a period of at least 56 days beginning with the child's birth. Section 80A(1)(a) is shown as omitted. The omitted words were not read. No statutory paternity pay rate. |
| [Section 80EA](https://www.legislation.gov.uk/ukpga/1996/18/section/80EA) | At least two weeks' leave in respect of the death of a child, as displayed. Wider wording, including pregnancy loss, is footnoted as in force on 6 January 2026 for specified purposes only. It is not treated as fully in force. The wider regulations were not opened. Commentary dates are not used. No parental bereavement pay rate. |
| [Section 80J](https://www.legislation.gov.uk/ukpga/1996/18/section/80J) | At least a week's carer's leave during any period of 12 months. Part 8B was inserted on 4 December 2023. Section 80K was not opened, so this starter does not say whether statutory carer's leave is unpaid. |
| [Carer's Leave Regulations 2024, regulation 5](https://www.legislation.gov.uk/uksi/2024/251/regulation/5/made) | One week of carer's leave during the relevant period, for an employee who satisfies regulation 4. Minimum half a working day. Maximum one continuous week. In force 6 April 2024. Extent England and Wales and Scotland. The definition of "relevant period" was not opened. |
| [Neonatal Care (Leave and Pay) Act 2023, Commencement No. 2](https://www.legislation.gov.uk/uksi/2025/41/made) | Section 2 and the Schedule, in so far as not already in force, come into force on 17 January 2025. The explanatory note says section 3 came into force on Royal Assent, 24 May 2023. This commencement is not itself the leave entitlement. |
| [Neonatal Care Leave and Miscellaneous Amendments Regulations 2025](https://www.legislation.gov.uk/uksi/2025/375) | In force 6 April 2025. Extent England and Wales and Scotland. They apply to children born on or after 6 April 2025. One week for each qualifying period the child has spent in neonatal care. Maximum twelve weeks. Before the end of 68 weeks beginning with the date of the child's birth. Statutory Neonatal Care Pay was not copied. |
| [Jury service](https://www.gov.uk/jury-service) | You will not be paid for doing jury service, but you can claim some money back if you lose earnings. Jury service usually lasts up to 10 working days. There are different rules in Scotland and in Northern Ireland. An employer's duty to allow time off was not on this page. No Juries Act section was opened. No loss-of-earnings rate. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. |

[Statutory sick pay](https://www.gov.uk/statutory-sick-pay) was not opened. The pin `ssp-not-opened` is unverified and has no quote and no rate. Employment Rights Act 2025 changes to statutory sick pay were not opened and are not stated as in force.

## What the result does

`explain()` reads one question, one policy set, one scope, one baseline snapshot, one directory, and one as-of date, and writes one JSON document. The same inputs and the same dates produce the same JSON. `entitlement_decision`, `pay_decision`, and `pay_rate` stay empty. `leave_booked` and `leave_recorded` stay false. `approved` stays false. `human_approval` stays null until a separate seen-step.

**The date asked about.** The version in force on that date is quoted, with its effective date. If the question omits the date, the as-of date is used and `about_date_source` says so. A date that cannot be read is not replaced with today. A version that has ended by the as-of date is still quoted for a day inside its window, and it is flagged as superseded.

**Review.** A review date before the day asked about is overdue. `may_be_relied_on` is then false. The pin is not refreshed from the web. A pin older than 90 days on the as-of date is stale. That window is a starter default.

**Negation.** "It is not true that the annual leave policy includes buying extra leave" is a denial. It is not an inclusion.

**Care.** Pregnancy, miscarriage, bereavement, domestic abuse, sickness, distress, or disability, including a paraphrase, is routed to HR or the line manager before a day count is quoted. A sentence that denies the distress is not itself a route. A question about whether a wider statutory provision is in force is not a personal disclosure.

**Entitlement.** "Am I entitled", "do I qualify", "how many days do I have", and "what will I be paid" are handed to a person. The scheme may still be quoted. It is not applied to a person. A supplied balance is not applied. An unreadable or out-of-range balance is not coerced.

**Markings.** Metadata and content are both read. A SECRET cover is caught when the metadata says OFFICIAL. The higher marking wins. Content above OFFICIAL-SENSITIVE is not copied. A legal hold and every retention label stay on the withheld row.

**People and roles.** The scope approver has to be an active HR id on the directory. "I am HR" in the question is not that check. A seen-step has to come from the deterministic approval step, name that kind of id, and carry the hash of the explanation. Seeing the explanation does not decide entitlement.

**Baseline.** The snapshot has to match the pin. A disagreement states no figure. An unverified row has no quote.

`decide_entitlement`, `book_leave`, `record_leave`, `calculate_pay`, and `approve_policy` raise `LeaveForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 03, 08, and 58 must be present beside this folder.

```bash
cd experiments/63-leave-policy-explainer
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/explain.py --policies fixtures/policies.json --baseline fixtures/baseline.json --scope examples/sample_scope.json --directory fixtures/directory.json --question examples/sample_question.json --as-of 2026-11-18
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 18 passed, 0 failed, 0 errors, 18 cases.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the outcome is `refused`.

## Limitations

- Topic matching is a phrase list. A paraphrase that does not use the phrase may not select the section. The explainer does not guess a topic.
- Care routing is a phrase list, including a few paraphrases that were written into the list. A disclosure that uses none of those phrases is not routed by this starter.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL, and SECRET above that. The Government Security Classifications Policy was not re-opened for this experiment.
- The 90-day pin window is a starter default. It is not a statutory period.
- Phone numbers, email addresses, dates of birth, street addresses, and honorific names are counted on the input and checked on the output. The values are not stored. The output is not described as anonymised. A name with no honorific is not counted.
- Experiment 58 was asked one fixed question. Its answer is not copied into this result.
- Regulation 15B, the Maternity and Parental Leave etc. Regulations 1999, section 80K, the definition of "relevant period" in the Carer's Leave Regulations, the wider parental-bereavement regulations, a Juries Act section, and the GOV.UK statutory sick pay page were not opened. Those points are unverified. No statutory pay rate is stated.
- Section 80EA wider leave is marked partial because the legislation.gov.uk footnote says "for specified purposes" only. It is not treated as fully in force. An April 2027 commentary date was not used.
- Northern Ireland employment law is not stated.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Lindenmere Community Trust is fictional.
- This is not legal advice, an entitlement decision, a booking, or a pay calculation.

## Two Copilot Studio harnesses

Both call `src/explain.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness decides entitlement or books leave. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. Microsoft's harness overview, opened 18 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 18 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short note may be written from the JSON. The section, the date, the statutory pin, and the empty entitlement stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Handbook: [../58-employee-handbook/](../58-employee-handbook/).
- Manifest generator: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).
- Identifier counts: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/63-leave-policy-explainer/
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

- [Working Time Regulations 1998, regulation 13](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13)
- [Working Time Regulations 1998, regulation 13A](https://www.legislation.gov.uk/uksi/1998/1833/regulation/13A)
- [Holiday entitlement](https://www.gov.uk/holiday-entitlement-rights)
- [Employment Rights Act 1996, section 71](https://www.legislation.gov.uk/ukpga/1996/18/section/71)
- [Employment Rights Act 1996, section 73](https://www.legislation.gov.uk/ukpga/1996/18/section/73)
- [Employment Rights Act 1996, section 75A](https://www.legislation.gov.uk/ukpga/1996/18/section/75A)
- [Employment Rights Act 1996, section 75E](https://www.legislation.gov.uk/ukpga/1996/18/section/75E)
- [Employment Rights Act 1996, section 76](https://www.legislation.gov.uk/ukpga/1996/18/section/76)
- [Employment Rights Act 1996, section 80A](https://www.legislation.gov.uk/ukpga/1996/18/section/80A)
- [Employment Rights Act 1996, section 80EA](https://www.legislation.gov.uk/ukpga/1996/18/section/80EA)
- [Employment Rights Act 1996, section 80J](https://www.legislation.gov.uk/ukpga/1996/18/section/80J)
- [Carer's Leave Regulations 2024, regulation 5](https://www.legislation.gov.uk/uksi/2024/251/regulation/5/made)
- [Carer's Leave Act 2023, commencement](https://www.legislation.gov.uk/uksi/2023/1283/made)
- [Neonatal Care Leave and Miscellaneous Amendments Regulations 2025](https://www.legislation.gov.uk/uksi/2025/375)
- [Neonatal Care (Leave and Pay) Act 2023, Commencement No. 2](https://www.legislation.gov.uk/uksi/2025/41/made)
- [Jury service](https://www.gov.uk/jury-service)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
