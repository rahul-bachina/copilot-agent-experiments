# Experiment 43: Response Drafting Agent

Catalogue ID **C004**. A draft customer response for one synthetic case.

UK service organisations, including financial-services firms, are asked for the same narrow thing: turn a case and an approved snippet into a reply a representative can check, with the source named, in plain words, and with a person still able to send it themselves. The failure mode is the agent that sends because the case said so, or that states a position the approved snippet does not contain. This starter drafts. It does not send.

**Autonomy A1.** The representative reviews the draft and is the person who would send it, on their own channel, outside this agent. Recording that review does not send the draft. The agent has no mail tool, no Dynamics 365 write, and no path that offers redress or closes a case.

Stack in the catalogue: Dynamics 365 and Microsoft 365. The draft itself is Python in the standard library. It calls `propose()` in [Experiment 08](../08-uk-pii-redaction-gateway/) before a draft is built, and it calls `line_applicability()` in [Experiment 09](../09-casework-correspondence-draft/) so a snippet is cited only when that gate says it is current. A representative can run it without a tenant.

The organisation in the samples is Harberton Service. It is invented. It is not a licensed supplier, a bank, an insurer, or a council. Case references are synthetic.

## The problem

A response agent that emails the customer, promises compensation, or pastes a withdrawn snippet because the case said to is the failure this starter is built to refuse. The useful narrow job is: read one case, quote only an approved snippet that is still in date, name that snippet, run a tone screen and a plain-English screen, and stop for the representative.

## Non-goals

- Sending an email, an SMS, a letter, or a chat reply. A recorded review is not a send.
- Choosing the customer's address, or treating words in the case as approval of a recipient.
- Writing a Dynamics 365 case, a mailbox, or any other production record.
- Offering redress, upholding or rejecting a complaint, or closing a case.
- Inventing a position that is not a verbatim approved snippet.
- Quoting a snippet that Experiment 09's gate marks withdrawn, not yet in force, or overdue for review. On the review date the snippet is not cited.
- Certifying that a firm met the Consumer Duty, PRIN 2A.5, UK GDPR, or the Equality Act 2010.
- Deciding that a communication has been tested under PRIN 2A.5.10R. This screen is not that test.
- Labelling a customer as vulnerable.
- Using a real customer's case, a real firm, or a real case reference. Harberton is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 9 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [PRIN 2A.5](https://handbook.fca.org.uk/handbook/prin2a/prin2as5) and the [PRIN sourcebook PDF](https://api-handbook.fca.org.uk/files/sourcebook/PRIN.pdf) | The PDF says it was last updated in June 2026. PRIN 2A.5 is the Consumer Duty retail customer outcome on consumer understanding. PRIN 2A.5.3 says a firm must support retail customer understanding so that its communications meet information needs, are likely to be understood, and equip retail customers to make decisions that are effective, timely and properly informed, and must communicate in a way which is clear, fair and not misleading. The same PDF cross-refers to that paragraph as PRIN 2A.5.3R. PRIN 2A.5.7 says a firm should use plain and intelligible language and, where jargon is unavoidable, explain it as simply as possible. The status letter on 2A.5.7 was not cleanly labelled in the PDF text extraction; the paragraph uses "should". PRIN 2A.5.10 says, where appropriate, a firm must test communications before communicating them and regularly monitor their impact. The same PDF cross-refers to that paragraph as PRIN 2A.5.10R. This starter does not carry out that test and does not find that the outcome was met. The screen is attached only when the synthetic sector is `financial_services`. |
| [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12) | Article 12(1) requires appropriate measures so that information referred to in Articles 13 and 14, and communications under Articles 15 to 22D and Article 34, is given in a concise, transparent, intelligible and easily accessible form, using clear and plain language. A routine service reply is not, by itself, that information. This starter does not decide that Article 12 has been met. |
| [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | Section 20(6): where the first or third requirement relates to the provision of information, the steps which it is reasonable to take include steps for ensuring that the information is provided in an accessible format. This starter offers to ask a person for another format. It does not decide what is reasonable. Section 29 was not opened, so the starter does not decide that the duty applies to Harberton. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The page says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio. The Customer Conversation harness is described for customer voice and chat. This starter does not build that third harness. |

Article 5, Article 6, Article 9, and Article 22A were not opened on 9 November 2026. DISP, FG22/5, and PRIN 2A.2 were not opened. No lawful basis is chosen. No DISP date is calculated.

[Experiment 09](../09-casework-correspondence-draft/) supplies the citation gate: status current, effective on or before the as-of date, and review date still in the future. This experiment calls that function. It does not copy the correspondence drafter. [Experiment 08](../08-uk-pii-redaction-gateway/) supplies the identifier count. `release()` is not called.

## What the starter does

`src/response.py` reads one JSON case and writes one JSON document. The same case and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. The case text is not copied into the draft.

Free text is passed to Experiment 08 (`propose`, caller `exp-43-response-drafting`). The redacted text is not copied into the output. The draft records the finding count, the entity types, and the input hash. `output_is_anonymised` stays false.

**Cited reply.** One or more approved snippets match, and Experiment 09's gate says each one may be cited. The body of each cited snippet is quoted. The snippet id and review date are named. A gap is stated when a matched topic has no citable snippet. No position is invented for the gap.

**Refused snippet.** Withdrawn, not yet in force, or review overdue, including on the review date. A current snippet that contains a promise, a complaint outcome, blame, or listed jargon is also refused and is not pasted. The refused wording is not copied out.

**Tone screen.** The draft text is scanned for the same promise, outcome, blame, and jargon list. A hit blocks the representative's later approval for their own channel. The screen is not a finding that a tone was appropriate in a legal sense.

**Plain-English screen.** Sentences longer than 25 words, and a closed jargon list, are recorded. The screen is not a reading-age certificate and not a test under PRIN 2A.5.10R. For `financial_services`, the JSON names PRIN 2A.5.3R and PRIN 2A.5.7 and sets `outcome_met` to false. For any other sector, PRIN 2A.5 is not applied.

**Accessibility.** Every draft that is prepared offers large print or audio via a person, and says the draft does not decide what is reasonable. `duty_met` stays false.

**Prompt injection.** Instructions to ignore the rules, send now, approve a recipient, or treat a withdrawn snippet as current are recorded. `followed` is false. Those words do not approve a recipient and do not select a withdrawn snippet.

**Stale data.** A snippet outside Experiment 09's gate is not quoted. A narrative that cites a year more than six years before the as-of date is flagged and does not move the as-of date. If the as-of date is more than 180 days after 9 November 2026, pinned sources are treated as outside the window and no snippet is quoted. Equal to 180 days is still inside the window. The 180-day figure is a starter default, not a review duty.

**Synthetic only.** A record that is not marked synthetic, or whose case id is not `SYN-CASE-` plus four digits, is refused. The refusal does not echo the text.

`record_review` accepts `representative_approve_for_own_send`, `representative_request_revision`, or `reject_draft` from a separate review object. Send approval is refused when the tone screen or the plain-English screen failed, when sources are outside the window, when immediate-danger wording was flagged, or when the review carries an email address or any recipient role other than `customer-on-case`. It still does not send. `send_message`, `write_case`, `offer_redress`, `close_case`, and `promise_outcome` raise `DraftForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must be present at `experiments/08-uk-pii-redaction-gateway/`. Experiment 09 must be present at `experiments/09-casework-correspondence-draft/`. This experiment does not carry a second copy of either.

```bash
cd experiments/43-response-drafting
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/response.py --input examples/sample_case.json --as-of 2026-11-09
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. Each case is counted once. A live Microsoft Foundry run has not been done.

A gap is not a failed run, and it is not a decision. The exit code is 0 when a draft or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list. Wording that is not on the list becomes a gap. That is deliberate. It will miss some routine questions a person would have recognised.
- A keyword can false-match. The tests cover the fixtures in this folder. They are not a study of how customers write.
- The 25-word sentence cap and the jargon list are a starter screen. They are not PRIN 2A.5.7 and they are not a reading-age measure. A short sentence can still mislead.
- The 180-day window on the pinned sources is a configuration choice for this starter. It is not a review duty the organisation already has.
- Experiment 09's gate treats the review date itself as overdue. That is that function's rule, called here, not a new rule.
- The vulnerability list is short and explicit. A phrase that is not on the list is not detected. Absence of a flag is not a finding that the customer needs no extra help.
- Experiment 08 does not redact names, email addresses, or telephone numbers. That is why the redacted text is not copied into the output.
- Article 5, Article 6, Article 9, and Article 22A were not opened on 9 November 2026. No lawful basis is asserted. This starter does not decide that a significant decision was avoided in the sense of Article 22A, because that article was not re-read. It only refuses to send, to decide a complaint, and to offer redress.
- Section 29 of the Equality Act 2010 was not opened. Schedule 2 was not opened. No duty is treated as met.
- FG22/5, PRIN 2A.2, and DISP were not opened. The status letter on PRIN 2A.5.7 was not cleanly labelled in the PDF extraction.
- Article 12(1) was read. It governs privacy information and specified communications, not every customer letter. The plain-English screen is not an Article 12 compliance check.
- Harberton Service and its snippets are fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. The overview says that. This readme does not quote a price. The billing pages linked from the overview were not opened. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness is the one Microsoft's overview describes for customer voice and chat. It is not built here. An unattended sender would sit outside this A1 design.
- This is not legal advice, a data protection impact assessment, a Consumer Duty assessment, or an ATRS submission.

## UK GDPR and the consumer-understanding outcome

The manifest does not assert the controller's lawful basis. Article 6 and Article 9 were not opened on 9 November 2026. The controller confirms the basis.

Article 12(1) was read the same day. It is cited so a privacy reviewer can see the plain-language rule that applies to privacy information. This draft is a service reply. It is not presented as an Article 13 or Article 14 notice. `article_12_met` stays false.

For a financial-services case, PRIN 2A.5.3R and PRIN 2A.5.7 were read. The plain-English screen is a mechanical check a representative can see. It is not the testing in PRIN 2A.5.10R. `outcome_met` stays false. For any other sector the Duty is not applied. This starter does not decide that Harberton is a firm to whom the Consumer Duty applies.

Section 20(6) was read. Every prepared draft offers another format via a person. Section 29 was not read. `duty_met` stays false.

The case text is not copied into the draft. That is this starter's minimisation practice. It is not a quoted finding under an article that was not opened on 9 November 2026.

## Two Copilot Studio harnesses

Both call `src/response.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness sends, writes a case, offers redress, or closes a complaint. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The representative pastes a case, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 9 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON: which snippet was refused, which sentence failed the plain-English screen, and why a review did not send. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Dynamics 365 and Microsoft 365, as a permission boundary if a connector is added later: [docs/dynamics-365-and-microsoft-365.md](docs/dynamics-365-and-microsoft-365.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The identifier gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The citation gate this experiment calls: [../09-casework-correspondence-draft/](../09-casework-correspondence-draft/).

## Project structure

```
experiments/43-response-drafting/
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

## References opened on 9 November 2026

- [PRIN 2A.5](https://handbook.fca.org.uk/handbook/prin2a/prin2as5)
- [PRIN sourcebook PDF](https://api-handbook.fca.org.uk/files/sourcebook/PRIN.pdf), last updated June 2026 on the PDF
- [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12)
- [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
