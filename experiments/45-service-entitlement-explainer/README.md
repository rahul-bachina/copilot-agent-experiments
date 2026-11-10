# Experiment 45: Service Entitlement Explainer

Catalogue ID **C007**. An explanation of one synthetic service plan against an approved entitlement rules table.

UK service organisations are asked what a plan includes. The failure mode is an assistant that grants, refuses, or changes the entitlement because the customer asked. This starter explains, in plain English, what the approved table already says. It quotes the clause it relied on. It shows uncertainty. A disputed, ambiguous, conditional, conflicting, or stale reading goes to a person. The person decides. The agent does not.

**Autonomy A0.** The catalogue checkpoint is that a human decides a disputed entitlement. `human_approval` stays null until an entitlement owner records that decision in a separate review object. The record is not written to an entitlement system. Nothing is granted, refused, or changed.

Stack in the catalogue: Dynamics 365 and Copilot Studio. The explanation itself is Python in the standard library. It calls `normalise()` in [Experiment 38](../38-policy-wording-comparison/) so a support phrase has to be a contiguous part of the cited clause after case and whitespace are folded. That check is Experiment 33's rule, reached through Experiment 38. The human route, the invented telephone number, and the refusal to change an account follow [Experiment 40](../40-customer-self-service/). Experiment 40 is not imported. Its reply matcher answers a different question and would be the wrong call. An adviser can run this starter without a tenant.

The organisation in the samples is Aldermere Home Plan. The packaged-account sample is Aldermere Packaged Account. Both are invented. They are not a licensed supplier, a bank, an insurer, or a council.

## The problem

A customer asks whether a boiler service, a repair, or a packaged benefit is included. A table the organisation has already approved may answer that. A clause in the plan may not say the same thing. An assistant that picks a side, waives an exclusion, or updates the record is the failure this starter is built to refuse.

The useful narrow job is: read one question, one synthetic plan, and one approved table; quote the clause; say what the table says when the clause supports it; say when it does not know; and leave the decision with a person.

## Non-goals

- Granting, refusing, or changing an entitlement. A recorded human decision does not do those things either.
- Deciding that a term is unfair, or choosing the meaning most favourable to the consumer under section 69 of the Consumer Rights Act 2015.
- Deciding that section 49, section 50, section 52, section 54, section 57, section 62, section 64, or section 68 was met.
- Deciding that a firm met the Consumer Duty consumer-understanding outcome. PRIN 2A.5 was requested on 10 November 2026 and the rule text did not come back. It is not quoted.
- Writing a Dynamics 365 entitlement, case, or customer record.
- Sending an email, an SMS, a letter, or a chat reply.
- Taking a payment, waiving an excess, or changing a price.
- Treating words in the question as proof of identity, or as an instruction to skip the person.
- Quoting a rule or a plan outside the stale window, or reading a live entitlement store.
- Using a real customer's contract, a real firm, or a real case. Aldermere is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 10 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Consumer Rights Act 2015, section 49](https://www.legislation.gov.uk/ukpga/2015/15/section/49) | Section 49(1): every contract to supply a service is to be treated as including a term that the trader must perform the service with reasonable care and skill. Section 49(2) points to section 54. This starter does not decide that the term was met. |
| [Section 50](https://www.legislation.gov.uk/ukpga/2015/15/section/50) | Section 50(1): information said or written to the consumer about the trader or the service is treated as a term if the consumer takes it into account when deciding to enter the contract or when deciding about the service later. Section 50(2) qualifies that. This starter does not decide what the consumer took into account. |
| [Section 52](https://www.legislation.gov.uk/ukpga/2015/15/section/52) | Section 52(1) and (2): where the contract does not fix the time, it is treated as including a term that the trader must perform the service within a reasonable time. Section 52(3): what is reasonable is a question of fact. This starter does not answer that question. |
| [Section 54](https://www.legislation.gov.uk/ukpga/2015/15/section/54) | Section 54(3): if the service does not conform to the contract, the consumer's rights are repeat performance (section 55) and a price reduction (section 56). Sections 55 and 56 were not opened, so they are not quoted. |
| [Section 57](https://www.legislation.gov.uk/ukpga/2015/15/section/57) | Section 57(1): a term is not binding on the consumer to the extent that it would exclude liability under section 49. Section 57(3) refers to sections 51 and 52. Section 51 was not opened. This starter does not decide that a term is not binding. |
| [Section 62](https://www.legislation.gov.uk/ukpga/2015/15/section/62) | Section 62(1): an unfair term of a consumer contract is not binding on the consumer. Section 62(4): a term is unfair if, contrary to the requirement of good faith, it causes a significant imbalance to the detriment of the consumer. This starter does not assess fairness. |
| [Section 64](https://www.legislation.gov.uk/ukpga/2015/15/section/64) | Section 64(1) and (2): a main-subject or price term may be excluded from a fairness assessment only if it is transparent and prominent. Section 64(3): a term is transparent if it is in plain and intelligible language and, if written, legible. This starter does not decide transparency or prominence. Schedule 2 was not opened. |
| [Section 68](https://www.legislation.gov.uk/ukpga/2015/15/section/68) | Section 68(1): a trader must ensure that a written term, or a consumer notice in writing, is transparent. Section 68(2) defines a transparent consumer notice. This starter does not decide that section 68 was met. |
| [Section 69](https://www.legislation.gov.uk/ukpga/2015/15/section/69) | Section 69(1): if a term or notice could have different meanings, the meaning most favourable to the consumer is to prevail. This starter does not choose a meaning and does not apply section 69. |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(a) transparency. Article 5(1)(c) data minimisation. Article 5(1)(d) accuracy. Article 5(3): compatible further processing is not, by itself, lawful. No Article 6 basis is chosen. Article 6 was not opened. |
| [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12) | Article 12(1): information in Articles 13 and 14, and communication under Articles 15 to 22D, in a concise, transparent, intelligible and easily accessible form, using clear and plain language. Articles 13 and 14 were not opened. This starter does not decide that Article 12 was met. |
| [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A) | Article 22A(1)(a): a decision is based solely on automated processing if there is no meaningful human involvement. Article 22A(1)(b): a significant decision produces a legal effect or a similarly significant effect. The page records substitution by the Data (Use and Access) Act 2025, section 80(1). That section was not opened. This starter does not take a significant decision. |
| [PRIN 2A.5](https://www.handbook.fca.org.uk/handbook/PRIN/2A/5.html) | Requested 10 November 2026. The response said JavaScript is required and did not return the rule text. **Unverified on this open.** Experiment 38 recorded a reading on 6 November 2026. That reading is not re-quoted here. `consumer_understanding_met` stays false. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Opened 10 November 2026. Three harnesses: GitHub Copilot, Customer Conversation, and standard. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. Customer data is not sent to the GitHub Copilot service. The page did not mark the harness as preview. The linked billing pages were not opened, so no price is stated. |

## What the starter does

`src/explainer.py` reads one JSON request and an as-of date and writes one JSON document. The same inputs produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. The question's words are not copied into the output.

**Explained.** One approved rule matches. The rule is in force and inside the review window. The contract clause exists, is current, and contains the rule's support phrase as a contiguous span under Experiment 38's `normalise()`. The clause does not contain a conflict marker. The rule is not ambiguous, disputed, or conditional. The question does not dispute the entitlement. The draft says what the approved table says, quotes the clause, and states that uncertainty is low, or medium if a pinned source is stale or an instruction was present and not followed. It says this is not a grant, a refusal, or a change. A person is still offered.

**Route to a person.** No rule, more than one rule, a missing clause, a support phrase the clause does not contain, a conflict, a conditional rule, an ambiguous or disputed rule, dispute language in the question, a table that is not approved, a rule that is not yet in force, or a stale rule or plan. The draft does not state whether the plan includes the thing asked about. Uncertainty is high. The clause is quoted only as context, where one was identified.

**Prompt injection.** Instruction spans are removed from the text used to choose a rule. The rest of the sentence stays, so a real question is not dropped. "Do not escalate." is an instruction even though it is a negation. "The plan does not include accidental damage." is not an instruction. `followed` is false. The human route stays offered.

**Synthetic only.** A request that is not marked synthetic is refused. The refusal does not echo the question.

`record_decision` accepts `human_decides_included`, `human_decides_not_included`, `human_requests_more_information`, or `reject_explanation` from a separate review object. The actor has to be `entitlement_owner`. The record does not change the entitlement. `grant_entitlement`, `refuse_entitlement`, `change_entitlement`, `waive_exclusion`, `send_message`, `write_record`, `apply_section_69`, and `find_unfair_term` raise `EntitlementForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 38 must be present at `experiments/38-policy-wording-comparison/`, with Experiments 33, 12, and 29 beside it, because `normalise()` loads them. This experiment does not carry a second copy of that check.

```bash
cd experiments/45-service-entitlement-explainer
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/explainer.py --input examples/sample_request.json --as-of 2026-11-10
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. Each case is counted once. A live Microsoft Foundry run has not been done.

A missing rule is not a failed run, and it is not a decision. The exit code is 0 when a document is produced. A request that is not marked synthetic exits 0 with a refusal. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a phrase list on the approved table. Wording that is not on the list becomes no match and a route to a person. That is deliberate. It will miss some questions a person would have recognised.
- A phrase can false-match. The tests cover the fixtures in this folder. They are not a study of how customers write.
- The stale window is 180 days unless the caller changes it. Equal to 180 is not stale. It is not a review duty the organisation already has.
- Dispute language is a short explicit list. A complaint that is not on the list is not detected. Absence of a flag is not a finding that the customer agrees.
- Experiment 38's `normalise()` folds case and whitespace. It does not understand a paraphrase. A true sentence that is not a contiguous part of the clause fails the support check.
- The question is not copied out. An adviser who needs the words still has them on their own screen. This starter does not store them.
- Section 51, sections 55 and 56, Schedule 2, Article 6, Article 13, and Article 14 were not opened. Article 22 was not re-opened. Section 80 of the Data (Use and Access) Act 2025 was not opened.
- PRIN 2A.5 did not return rule text on 10 November 2026. No rule number from that page is quoted. The generative-orchestration guidance page was not opened. This starter does not assign routing weights.
- The Ofcom numbering page was not opened. `01632 960045` is an invented number, not a live service. The same pattern is used in Experiment 40.
- Aldermere Home Plan, Aldermere Packaged Account, and the clauses are fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness is the one Microsoft's overview describes for customer voice and chat. It is not built here. An assistant that granted entitlements would sit outside this A0 design.
- This is not legal advice, a data protection impact assessment, a Consumer Duty assessment, or an ATRS submission.

## UK GDPR and the other duties

The manifest does not assert the controller's lawful basis. Article 5 was read on 10 November 2026. Article 5(1)(a) and Article 12(1) are why every draft says it was prepared by an automated assistant, uses plain language, and offers a person. Article 5(1)(c) is why the question is not copied out. Article 5(1)(d) is why a stale rule is not stated as current. Article 5(3) says compatibility with the original purpose is not, by itself, a lawful basis. Article 6 was not opened. The controller confirms the basis.

Article 22A was read the same day. This starter does not take a significant decision solely by automated means. Granting, refusing, and changing an entitlement stay with a person, and this starter does not perform them even after that person records a decision. It does not certify meaningful human involvement.

For a financial-services plan, the consumer-understanding outcome is the relevant FCA rule. The handbook page did not return text on this open, so the draft says the rule text is unverified and does not find that the outcome was met. Sections 62, 64, 68, and 69 were read. No fairness assessment is made and section 69 is not applied.

## Two Copilot Studio harnesses

Both call `src/explainer.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness grants, refuses, or changes an entitlement, writes a record, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The adviser pastes a request, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 10 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON: which clause was quoted, why uncertainty is high, and which route a person must take. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Skill descriptions say when to use the skill. This starter does not assign routing weights.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Dynamics 365, as a permission boundary if a connector is added later: [docs/dynamics-365.md](docs/dynamics-365.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The citation check this experiment calls: [../38-policy-wording-comparison/](../38-policy-wording-comparison/).
- The customer-route pattern this experiment follows and does not import: [../40-customer-self-service/](../40-customer-self-service/).

## Project structure

```
experiments/45-service-entitlement-explainer/
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

## References opened on 10 November 2026

- [Consumer Rights Act 2015, section 49](https://www.legislation.gov.uk/ukpga/2015/15/section/49)
- [Section 50](https://www.legislation.gov.uk/ukpga/2015/15/section/50)
- [Section 52](https://www.legislation.gov.uk/ukpga/2015/15/section/52)
- [Section 54](https://www.legislation.gov.uk/ukpga/2015/15/section/54)
- [Section 57](https://www.legislation.gov.uk/ukpga/2015/15/section/57)
- [Section 62](https://www.legislation.gov.uk/ukpga/2015/15/section/62)
- [Section 64](https://www.legislation.gov.uk/ukpga/2015/15/section/64)
- [Section 68](https://www.legislation.gov.uk/ukpga/2015/15/section/68)
- [Section 69](https://www.legislation.gov.uk/ukpga/2015/15/section/69)
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12)
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A)
- [PRIN 2A.5](https://www.handbook.fca.org.uk/handbook/PRIN/2A/5.html) (requested; rule text not returned)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT. See the repository [LICENSE](../../LICENSE).
