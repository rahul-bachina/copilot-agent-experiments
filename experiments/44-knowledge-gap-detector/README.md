# Experiment 44: Knowledge Gap Detector

Catalogue ID **C005**. A draft review of one synthetic knowledge pack.

UK public-service and regulated service desks are asked for the same narrow thing: see which customer questions, case notes, and failed searches are not covered by the approved knowledge base, which articles are stale or contradict each other, and what a new article would need to say. The failure mode is the agent that publishes the article, edits the live page, or treats a screen as proof that the Consumer Duty was met. This starter reviews. It does not publish.

**Autonomy A0.** The knowledge manager confirms gaps. Recording that confirmation does not publish an article and does not edit one. The agent has no publishing tool, no Dynamics 365 write, no Fabric write, and no send.

Stack in the catalogue: Dynamics 365 and Microsoft Fabric. The review itself is Python in the standard library. It calls `propose()` in [Experiment 08](../08-uk-pii-redaction-gateway/) before a review is built. `last_reviewed` uses `is_stale()` in [Experiment 21](../21-it-service-desk/). An `it_service` pack also calls `match_articles()` there. A public-service, financial-services, energy, or telecoms pack calls `match_articles()` in [Experiment 40](../40-customer-self-service/). Those calls return ids. They do not copy article bodies, and they do not publish. A knowledge manager can run this without a tenant.

The organisation in the samples is Northmere Knowledge Service. It is invented. It is not a council, a bank, an insurer, or a supplier.

## The problem

A knowledge agent that publishes because a search returned nothing, or that picks one side of two current articles, or that pastes a customer's words into a new page, is the failure this starter is built to refuse. The useful narrow job is: read one pack, compare it with the approved articles, name the gap or the conflict with evidence links, and stop for the knowledge manager.

## Non-goals

- Publishing, editing, or deleting a knowledge article. A recorded confirmation is not a publish.
- Writing a Dynamics 365 record, a Fabric table, or any other production record.
- Sending an email, an SMS, a letter, or a chat message.
- Choosing which of two conflicting articles is right.
- Treating a stale, withdrawn, or not-yet-in-force article as coverage. On the review date the article is not citable.
- Copying a query, a case note, a search string, or an article body into the output.
- Certifying that a firm met the Consumer Duty, PRIN 2A.5, UK GDPR Article 5(1)(c), or the Equality Act 2010.
- Deciding that a communication has been tested under PRIN 2A.5.10. This screen is not that test.
- Using a real customer's words, a real firm, or a real case reference. Northmere is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 10 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [PRIN 2A.5](https://handbook.fca.org.uk/handbook/prin2a/prin2as5) and the [PRIN sourcebook PDF](https://api-handbook.fca.org.uk/files/sourcebook/PRIN.pdf) | The handbook HTML page did not return the rule text that day. It returned the FCA head-office address. The PDF was opened. The PDF text says the sourcebook was last updated in June 2026. The file metadata modification time was 27 August 2026. That metadata is not a handbook sentence, so this starter does not treat 27 August 2026 as the sourcebook update date. PRIN 2A.5.3 says a firm must support retail customer understanding so that its communications meet information needs, are likely to be understood, and equip retail customers to make decisions that are effective, timely and properly informed, and must communicate in a way which is clear, fair and not misleading. PRIN 2A.5.4 cross-refers to that paragraph as PRIN 2A.5.3R. PRIN 2A.5.7 says a firm should use plain and intelligible language and, where jargon is unavoidable, explain it as simply as possible. The status letter on 2A.5.7 was not cleanly attached in the PDF text extraction. PRIN 2A.5.10 says, where appropriate, a firm must test communications and regularly monitor their impact. Paragraph (2) cross-refers to PRIN 2A.5.10R. This starter does not carry out that test and does not find that the outcome was met. The screen is attached only when the synthetic sector is `financial_services`. |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(c): personal data shall be adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed ('data minimisation'). The textual amendments listed on the page did not change paragraph (1)(c). Article 5(3) was listed as inserted. This starter does not rely on it. This starter does not decide that Article 5(1)(c) has been met. |
| [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | The page said section 20 was up to date with all changes known to be in force on or before 07 November 2026. It was opened on 10 November 2026. Section 20(6): where the first or third requirement relates to the provision of information, the steps which it is reasonable for A to have to take include steps for ensuring that the information is provided in an accessible format. The pending changes listed on the page were to other sections. This starter flags an article that does not mention another format. It does not decide what is reasonable. Section 29 and Schedule 2 were not opened. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The page says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio. The Customer Conversation harness is described for customer voice and chat. This starter does not build that third harness. |

Article 6, Article 9, and Article 22A were not opened on 10 November 2026. DISP, FG22/5, and PRIN 2A.2 were not opened. No lawful basis is chosen. Dynamics 365 and Microsoft Fabric product pages were not opened. **Unverified:** click-paths for knowledge-article publishing and for Fabric.

[Experiment 21](../21-it-service-desk/) supplies `is_stale()` and, for an IT pack, `match_articles()`. [Experiment 40](../40-customer-self-service/) supplies `match_articles()` for the service sectors it already knows. [Experiment 08](../08-uk-pii-redaction-gateway/) supplies the identifier count. `release()` is not called.

## What the starter does

`src/gaps.py` reads one JSON pack and writes one JSON document. The same pack and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. `published` is false. The pack text is not copied into the review.

Free text is passed to Experiment 08 (`propose`, caller `exp-44-knowledge-gap-detector`). The redacted text is not copied into the output. The review records the finding count, the entity types, and the input hash. `output_is_anonymised` stays false.

**Content gap.** A query, note, or search miss whose topic is not covered by a current article in the approved base. A query and a miss on the same topic are one gap, with two evidence links. The count of gaps is the number of topics, not the number of links.

**Retrieval miss.** The search log says zero results, and a current approved article matches. That is not a second content gap.

**Stale, withdrawn, or not yet in force.** The article is listed by id. Its body is not copied. On the review date the article is not citable. That date rule is this starter's. `last_reviewed` uses Experiment 21's `is_stale()`, which treats a review older than 180 days, or a future review date, as stale. Exactly 180 days is still inside that function's window.

**Conflict.** Two current articles on the same topic and the same claim, one affirming and one denying. Both ids are listed. `winner_chosen` stays false.

**Related catalogues.** For `it_service`, Experiment 21 ids are attached as evidence. For `public_service`, `financial_services`, `energy_retail`, and `telecoms`, Experiment 40 ids are attached. A related page does not close a gap in the approved base. Bodies are not copied.

**Plain-English and accessibility screens.** A current article is screened for sentences longer than 25 words, a closed jargon list, and whether it mentions another format. For `financial_services`, the JSON names PRIN 2A.5.3, PRIN 2A.5.7, and PRIN 2A.5.10 and sets `outcome_met` to false. For any other sector, PRIN 2A.5 is not applied. `duty_met` stays false.

**Outlines.** A draft outline names fixed sections and evidence links. It does not copy the query. `published` and `edited` stay false. When pinned sources are outside the window, outlines are omitted.

**Prompt injection.** Instructions to ignore the rules, publish now, or pretend to be the knowledge manager are recorded. `followed` is false. Only the matched phrase is removed, so "Do not escalate. The bin was not collected." still matches the bin topic. "Do not park on the yellow lines." is not an instruction. "Do not escalate." on its own is an instruction and does not become a gap.

**Stale sources.** If the as-of date is more than 180 days after 10 November 2026, pinned sources are outside the window, outlines are omitted, and `confirm_gap` is refused. Equal to 180 days is still inside the window. The 180-day figure is a starter default, not a review duty.

**Synthetic only.** A record that is not marked synthetic, or whose ids do not match the starter patterns, is refused. The refusal does not echo the text.

`record_confirmation` accepts `confirm_gap`, `reject_gap`, or `defer` from a separate object. The actor must be a knowledge manager. Confirming a gap sets `human_approval` and does not publish. `publish_article`, `edit_article`, `delete_article`, and `send_message` raise `GapForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must be present at `experiments/08-uk-pii-redaction-gateway/`. Experiment 21 must be present at `experiments/21-it-service-desk/`. Experiment 40 must be present at `experiments/40-customer-self-service/`. This experiment does not carry a second copy of any of them.

```bash
cd experiments/44-knowledge-gap-detector
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/gaps.py --input examples/sample_pack.json --as-of 2026-11-10
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. Each case is counted once. A live Microsoft Foundry run has not been done.

A gap is not a failed run, and it is not a decision. The exit code is 0 when a review or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list. Wording that is not on the list becomes a gap, or an unmatched topic tied to the item id. That is deliberate. It will miss some questions a person would have recognised.
- A keyword can false-match. The tests cover the fixtures in this folder. They are not a study of how customers write.
- The 25-word sentence cap and the jargon list are a starter screen. They are not PRIN 2A.5.7 and they are not a reading-age measure. A short sentence can still mislead.
- The 180-day window on the pinned sources is a configuration choice for this starter. It is not a review duty the organisation already has.
- Experiment 21's `is_stale()` treats the 180th day as still current and a future `last_reviewed` as stale. That is that function's rule, called here, not a new rule. The review-due rule, including on the review date itself, is this starter's.
- A page in Experiment 21 or Experiment 40 is evidence. It does not by itself mean the approved base is complete.
- Experiment 08 does not redact names, email addresses, or telephone numbers. That is why the redacted text is not copied into the output.
- Article 6, Article 9, and Article 22A were not opened on 10 November 2026. No lawful basis is asserted. This starter does not decide that a significant decision was avoided in the sense of Article 22A, because that article was not re-read. It only refuses to publish, to edit, and to send.
- Section 29 of the Equality Act 2010 was not opened. Schedule 2 was not opened. No duty is treated as met. The section 20 page was stated as up to date to 07 November 2026 and was opened on 10 November 2026.
- The handbook HTML page did not return PRIN 2A.5. The PDF did. The status letter on PRIN 2A.5.7 was not cleanly labelled. FG22/5, PRIN 2A.2, and DISP were not opened.
- Article 5(1)(c) was read. The practice of not copying the pack text is not a finding that the article was met.
- Northmere Knowledge Service and its articles are fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. The overview says that. This readme does not quote a price. The billing pages linked from the overview were not opened. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness is the one Microsoft's overview describes for customer voice and chat. It is not built here. An unattended publisher would sit outside this A0 design.
- Dynamics 365 and Microsoft Fabric product pages were not opened. Anything said about those click-paths is unverified.
- This is not legal advice, a data protection impact assessment, a Consumer Duty assessment, or an ATRS submission.

## UK GDPR and the consumer-understanding outcome

The manifest does not assert the controller's lawful basis. Article 6 and Article 9 were not opened on 10 November 2026. The controller confirms the basis.

Article 5(1)(c) was read the same day. The review stores ids, hashes, and counts. It does not store the query. `data_minimisation_met` stays false.

For a financial-services pack, PRIN 2A.5.3, PRIN 2A.5.7, and PRIN 2A.5.10 were read from the PDF. The plain-English screen is a mechanical check a knowledge manager can see. It is not the testing in PRIN 2A.5.10. `outcome_met` stays false. For any other sector the Duty is not applied. This starter does not decide that Northmere is a firm to whom the Consumer Duty applies.

Section 20(6) was read. Outlines include a section on another format. Section 29 was not read. `duty_met` stays false.

## Two Copilot Studio harnesses

Both call `src/gaps.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness publishes, edits, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The knowledge manager pastes a pack, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 10 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON: which article was stale, which pair conflicts, and why a confirmation did not publish. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Dynamics 365 and Microsoft Fabric, as a permission boundary if a connector is added later: [docs/dynamics-365-and-fabric.md](docs/dynamics-365-and-fabric.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The identifier gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The IT catalogue this experiment calls: [../21-it-service-desk/](../21-it-service-desk/).
- The self-service catalogue this experiment calls: [../40-customer-self-service/](../40-customer-self-service/).

## Project structure

```
experiments/44-knowledge-gap-detector/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── schema/
├── fixtures/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 10 November 2026

- [PRIN 2A.5](https://handbook.fca.org.uk/handbook/prin2a/prin2as5) — HTML page did not return the rules
- [PRIN sourcebook PDF](https://api-handbook.fca.org.uk/files/sourcebook/PRIN.pdf), PDF text says last updated June 2026
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
