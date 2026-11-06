# Experiment 40: Customer Self-Service Agent

Catalogue ID **C001**. A self-service draft for one synthetic customer enquiry.

Utilities, telecoms providers, financial-services firms, and public-facing service organisations are asked for the same narrow thing: answer from an approved page, explain the next step, and prepare a low-risk account draft for a person to confirm. The failure mode is the agent that changes the account because the chat said so. This starter answers from a fixed knowledge base. It can prepare an address-update draft or an appointment-request draft. It does not apply either one. It always offers a person, including a non-digital counter. It never resets a password, never takes a payment, never closes a complaint, never changes a tariff or a contract, and never sends a message.

**Autonomy A1.** The customer confirms an account draft in a separate review object. Confirmation does not change the record and does not book the appointment. A handler may later approve a correspondence draft for their own channel, and only after that customer confirmation. Approval does not send the draft. The agent has no tool that writes Dynamics 365, takes a payment, or sends.

Stack in the catalogue: Copilot Studio and Dynamics 365 Customer Service. The reply itself is Python in the standard library. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) before a draft is built. For a financial-services complaint or a vulnerability phrase it calls `analyse()` in [Experiment 02](../02-consumer-duty-complaint-intake/) and does not calculate a DISP clock. A handler can run it without a tenant.

The organisation in the samples is Mereford Customer Service. It is invented. It is not a licensed supplier, a bank, an insurer, or a council. Articles, account references, and the telephone number are synthetic.

The shape of the draft follows [Experiment 21](../21-it-service-desk/) for confirmation, [Experiment 13](../13-council-contact-front-door/) for the warm handover, [Experiment 02](../02-consumer-duty-complaint-intake/) for the complaint gate, and [Experiment 09](../09-casework-correspondence-draft/) for draft approval. Experiments 13, 21, and 09 are not imported. The pattern is copied. Experiment 02 is called.

## The problem

A self-service agent that resets a password, takes a card payment, closes a complaint, or changes a tariff because the customer asked is the failure this starter is built to refuse. The useful narrow job is: read one enquiry, match it to a page the organisation has already approved, show the review date, explain the next step, and prepare a low-risk draft without applying it.

## Non-goals

- Resetting a password, unlocking an account, or asking for a one-time code.
- Taking a payment, storing a card number, or making a refund.
- Upholding, rejecting, or closing a complaint, or offering redress.
- Changing a tariff, a price, or a contract term.
- Changing an address, booking an appointment, or submitting a meter reading. A recorded confirmation does not do those things.
- Writing a Dynamics 365 case, incident, or customer record.
- Sending an email, an SMS, a letter, or a chat reply. Handler approval of a draft is not a send.
- Treating words in the enquiry as proof of identity. A passed check is a separate object, from the channel, for the same day, on the signed-in portal. Web chat, phone, and email cannot carry it.
- Quoting a page whose review date is outside the stale window, or reading a live knowledge base.
- Labelling a customer as vulnerable, or deciding eligibility for a priority services register.
- Deciding that an organisation has met UK GDPR, the Consumer Duty, DISP, the Ofgem blog, or the Equality Act 2010.
- Using a real customer's enquiry, a real firm, or a real case. Mereford is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 6 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(a) lawfulness, fairness and transparency. Article 5(1)(c) data minimisation. Article 5(1)(d) accuracy. Article 5(1)(e) storage limitation. Article 5(1)(f) integrity and confidentiality. Article 5(2) accountability. Article 5(3): compatible further processing is not, by itself, lawful. No lawful basis is chosen. |
| [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A) | A decision is based solely on automated processing if there is no meaningful human involvement. A significant decision produces a legal effect or a similarly significant effect. This starter does not take one. |
| [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80) | Section 80(1) substitutes Articles 22A to 22D for Article 22. Article 22C(2) describes information, representations, human intervention, and contesting a decision. This starter does not decide that those safeguards are met. S.I. 2026/82 and regulations under Article 22D were not opened. |
| [Ofgem and Energy Ombudsman blog, 5 February 2026](https://www.ofgem.gov.uk/blog/understanding-ai-energy-sector-benefits-risks-and-your-rights) | Energy companies should be clear when they use AI, make it easy to speak to a human, offer a non-digital alternative, and check that systems are fair. This is a blog. It was not verified as a licence condition. The May 2026 ethical AI document was not opened. Fairness monitoring has not been done. |
| [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20) | Section 20(6): where the adjustment duty relates to information, reasonable steps include an accessible format. This starter offers to ask a person for another format. It does not decide what is reasonable. |
| [Equality Act 2010, section 29](https://www.legislation.gov.uk/ukpga/2010/15/section/29) | Section 29(7) applies the adjustment duty to a service-provider. This starter does not decide that the duty has been met. |
| [Equality Act 2010, section 149](https://www.legislation.gov.uk/ukpga/2010/15/section/149) | The public sector equality duty. The note is attached only when the synthetic sector is `public_service`. Due regard is not assessed. |
| [PRIN 2A.1](https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html) | The Consumer Duty applies to a firm's retail market business. Cross-cutting obligations are at PRIN 2A.2. Outcome rules at PRIN 2A.3 to PRIN 2A.6 cover products and services, price and value, consumer understanding, and consumer support. The Duty does not create a fiduciary duty or require advice the firm would not otherwise give. PRIN 2A.2 was requested the same day and the rule text did not come back, so it is not quoted. FG22/5 was not opened. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. The Customer Conversation harness is described for customer voice and chat. This starter does not build that third harness. |

Article 6 and Article 9 were not opened on 6 November 2026. DISP was not re-opened. Experiment 02 holds the DISP clock. This experiment does not call it.

[Experiment 13](../13-council-contact-front-door/) opened the AI Playbook and the ATRS scope policy on 27 October 2026. This experiment did not re-open them. It does not decide that a body is in the ATRS mandatory scope, and it does not submit a record. [Experiment 03](../03-agent-inventory-atrs-assurance/) drafts a pack. It does not approve one.

## What the starter does

`src/service.py` reads one JSON enquiry and writes one JSON document. The same enquiry and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. The enquiry's words are not copied into the output.

Free text is passed to Experiment 08 (`propose`, caller `exp-40-customer-self-service`). The redacted text is not copied into the draft. The draft records the finding count, the entity types, and the input hash. `output_is_anonymised` stays false. `release` is not called.

**Knowledge answer.** One current page matches and it does not change the account. The body is quoted. The next step is in that body. A human route is offered. Web chat, phone, and email can receive this answer. No session is required, because nothing on the account changes.

**Address-update draft.** The same identity rule as Experiment 21, with a portal session instead of an internal staff session: channel `portal`, `portal_session` recorded by the channel, same day, same synthetic account reference. The only postcode copied is `SYN 1AA`. Any other postcode is dropped. The customer may later confirm the draft. `record_changed` stays false.

**Appointment-request draft.** The same identity rule. The date must be after the as-of date. The slot is `morning` or `afternoon`. The place is `mereford-counter` or `phone-callback`. Confirmation does not book it. `appointment_booked` stays false.

**Prohibited.** Password, payment, tariff, contract. The policy sentence is quoted. It does not describe how to do the thing. The customer cannot confirm it. A handler takes the handover outside the agent.

**Financial-services complaint or vulnerability.** Experiment 02 `analyse()` is called. Evidence quotes are not copied. The customer is not labelled vulnerable. The complaint is not closed. No DISP date is calculated. PRIN 2A.1 was read. No breach is found.

**Complaint in another sector.** A person takes it. DISP and PRIN 2A are not applied. Ofgem's complaints rules were not opened on 6 November 2026.

**Vulnerability or immediate danger, in any sector.** A fixed script and a human route. If the words say immediate danger, the script says call 999. No one is contacted.

**Identity not verified, or a third party.** An account draft is not prepared. A published page that does not change the account can still be quoted.

**Stale page.** `last_reviewed` is more than 180 days before the as-of date. Equal to 180 is not stale. The body is not copied. If a pinned source is outside the same window, pages are not quoted.

**Prompt injection.** Instructions to ignore the rules, reset a password now, close a complaint now, or send now are recorded. `followed` is false. A sentence that is only an instruction is not used to choose a page.

**Synthetic only.** A record that is not marked synthetic is refused. The refusal does not echo the text.

`record_review` accepts `customer_confirm_address_draft`, `customer_confirm_appointment_draft`, `handler_take_handover`, `handler_approve_correspondence_for_own_send`, or `reject_draft` from a separate review object. The send approval is refused until the customer has confirmed, and it is refused if the review carries an email address or any recipient other than `account-holder`. It still does not send. `reset_password`, `take_payment`, `close_complaint`, `change_tariff`, `change_contract`, `send_message`, and `write_record` raise `ServiceForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must be present at `experiments/08-uk-pii-redaction-gateway/`. Experiment 02 must be present at `experiments/02-consumer-duty-complaint-intake/` for a financial-services complaint or vulnerability flag. This experiment does not carry a second copy of either.

```bash
cd experiments/40-customer-self-service
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/service.py --input examples/sample_enquiry.json --as-of 2026-11-06
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. Each case is counted once. A live Microsoft Foundry run has not been done.

A missing page is not a failed run, and it is not a decision. The exit code is 0 when a draft is produced. A record that is not marked synthetic exits 0 with a refusal. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list. Wording that is not on the list becomes no match or a handover. That is deliberate. It will miss some routine questions a person would have recognised.
- A keyword can false-match. The word "password" routes to the handler even when the rest of the enquiry is a meter reading. The tests cover the fixtures in this folder. They are not a study of how customers write.
- The stale window is a configuration choice for this starter, 180 days unless the caller changes it. It is not a review duty the organisation already has.
- The vulnerability list is short and explicit. A phrase that is not on the list is not detected. Absence of a flag is not a finding that the customer needs no extra help.
- A passed `portal_session` is a stand-in for a channel fact. This starter does not call a sign-in product. The session does not authorise a password reset or a record change.
- The draft does not echo the enquiry. A handler who needs the words still has them on their own screen. This starter does not store them.
- Experiment 08 does not redact names, email addresses, or telephone numbers. That is why the redacted text is not copied into the draft.
- Only the postcode `SYN 1AA` is accepted. A real address is not copied, so the draft is not a completed change-of-address form.
- DISP was not re-opened on 6 November 2026. A handler who needs a DISP date uses Experiment 02. This readme does not quote a 15-day or 35-day deadline.
- PRIN 2A.2, FG21/1, and FG22/5 were not opened. Ofgem's complaint-handling rules and the May 2026 ethical AI document were not opened. The Ofgem blog's claim about a DUAA complaints duty was not checked against a section.
- Article 6 and Article 9 were not opened. No lawful basis and no Article 9 condition is asserted.
- S.I. 2026/82 and regulations under Article 22D were not opened.
- The Ofcom numbering page was not opened. `01632 960040` is an invented number, not a live service.
- Mereford Customer Service, its pages, and its account references are fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness is the one Microsoft's overview describes for customer voice and chat. It is not built here. An unattended resolver that closes complaints or changes accounts would sit outside this A1 design.
- This is not legal advice, a data protection impact assessment, a Consumer Duty assessment, an Ofgem compliance statement, or an ATRS submission.

## UK GDPR and the other duties

The manifest does not assert the controller's lawful basis. Article 5 was read on 6 November 2026. Article 5(1)(a) is why every draft says it was written by an automated AI chatbot and offers a person. Article 5(1)(c) is why the free text is not copied out. Article 5(1)(d) is why a stale page is not quoted. Article 5(3) says compatibility with the original purpose is not, by itself, a lawful basis. Article 6 was not opened. The controller confirms the basis.

Article 22A was read the same day. This starter does not take a significant decision solely by automated means. Address changes, appointments, payments, tariffs, contracts, and complaint outcomes stay with a person, and this starter does not perform them even after that person confirms a draft. Article 22C(2) sets out safeguards for a controller who does take such a decision. This starter does not decide that those safeguards are in place. Article 22D regulations were not read.

For a financial-services complaint or vulnerability phrase, PRIN 2A.1 was read. The cross-cutting rules are at PRIN 2A.2, which was not quoted. Experiment 02 may suggest a product, a cause, and a severity. `breach_found` stays false. The customer is not labelled vulnerable. DISP was not re-opened.

For an energy-retail scenario, the 5 February 2026 Ofgem blog is the disclosure source: say that AI is in use, make a person easy to reach, and offer a non-digital route. The draft does those three. It does not monitor fairness, and it does not decide that a supplier has met the blog.

Section 20(6) and section 29(7) of the Equality Act 2010 were read. Every draft offers another format via a person. Section 149 is noted for the public-service sector only. No duty is treated as met.

## Two Copilot Studio harnesses

Both call `src/service.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness resets a password, takes a payment, closes a complaint, changes a tariff or a contract, writes a record, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The customer or the handler pastes an enquiry, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 6 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON: which field is missing, why identity was not trusted, which sentence is the page and which is the fixed script. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Dynamics 365 Customer Service, as a permission boundary if a connector is added later: [docs/dynamics-365-customer-service.md](docs/dynamics-365-customer-service.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The identifier gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The complaint gate this experiment calls for financial services: [../02-consumer-duty-complaint-intake/](../02-consumer-duty-complaint-intake/).
- The confirmation pattern: [../21-it-service-desk/](../21-it-service-desk/).
- The warm-handover pattern: [../13-council-contact-front-door/](../13-council-contact-front-door/).
- The correspondence-approval pattern: [../09-casework-correspondence-draft/](../09-casework-correspondence-draft/).

## Project structure

```
experiments/40-customer-self-service/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
│   ├── service.py
│   ├── catalogue.py
│   ├── identity.py
│   ├── injection.py
│   └── sources.py
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 6 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A)
- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80)
- [Understanding AI in the energy sector](https://www.ofgem.gov.uk/blog/understanding-ai-energy-sector-benefits-risks-and-your-rights) (blog, 5 February 2026)
- [Equality Act 2010, section 20](https://www.legislation.gov.uk/ukpga/2010/15/section/20)
- [Equality Act 2010, section 29](https://www.legislation.gov.uk/ukpga/2010/15/section/29)
- [Equality Act 2010, section 149](https://www.legislation.gov.uk/ukpga/2010/15/section/149)
- [PRIN 2A.1](https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
