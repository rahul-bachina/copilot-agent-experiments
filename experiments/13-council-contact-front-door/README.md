# Experiment 13: Council contact-centre front door

Catalogue ID **V006**. Public Enquiry Agent for a UK local authority: a contact-centre front door with a warm handover.

Residents ask the same questions often: which day the bins go out, when the library is open, how to pay council tax. Staff also take the questions that must not be answered by a script: eligibility, a person's account, a safeguarding worry, an emergency. This starter prepares a draft for a contact-centre adviser. It quotes a page from a fixed catalogue, or it says the catalogue does not contain the answer, or it stops and hands the conversation to a person.

**Autonomy A1.** The adviser decides whether a published sentence may be read out. The agent does not decide eligibility, does not open or change a case, and does not send anything. Accepting a draft does not do those things either. There is no tool for them.

Stack in the catalogue: Copilot Studio and Microsoft 365. The front door itself is Python in the standard library, so an adviser can run it without a tenant.

The council in the samples is Northmarsh Borough Council. It is invented. Pages, wards, and tariffs in the catalogue are synthetic. They are not a real authority's content.

## The problem

A front door that invents a bin day, or that tells someone they qualify for housing or a council tax reduction, is worse than a queue. A front door that keeps going when a resident describes an emergency, or that is the only way to get help, excludes people and misses harm.

The useful narrow job is: read one enquiry, match it to a page the council has already published, show the review date, and stop when the page is missing, stale, statutory, or unsafe to answer.

## Non-goals

- Deciding eligibility or entitlement for housing, homelessness assistance, council tax reduction, a Blue Badge, a school place, social care, or any other service.
- Looking up a resident's account, balance, rent, or case.
- Creating, updating, or closing a case, a service request, or any other production record.
- Sending an email, an SMS, a letter, or a chat message. The starter returns JSON to the adviser.
- Booking an appointment.
- Taking, refunding, or promising a payment.
- Issuing, cancelling, or waiving a penalty charge or any other enforcement step.
- Giving legal, medical, benefits, or safeguarding advice.
- Replacing 999, or continuing with a service answer after an emergency or vulnerability phrase.
- Being the only way to contact the council. Phone and face-to-face routes stay.
- Publishing an Algorithmic Transparency Recording Standard (ATRS) record, or deciding that a council is in the mandatory scope.
- Reading a live council website at run time. The catalogue is a file.
- Using a real council's pages, residents, or staff. Northmarsh is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.
- Quoting a page whose review date is outside the stale window.
- Treating an instruction inside the enquiry as an instruction to the agent.

## What was opened

Opened on 27 October 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [AI Playbook for the UK Government](https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government/artificial-intelligence-playbook-for-the-uk-government-html) (published 10 February 2025) | Principle 4: meaningful human control, including where a chatbot cannot be reviewed in real time. Principle 7: be open about automated responses. The playbook's example is that a chatbot response should say it was written by an automated AI chatbot. ATRS is required for in-scope central government and arm's length bodies. It is not yet a requirement for every other public-sector institution. The playbook encourages its use. |
| [ATRS mandatory scope and exemptions policy](https://www.gov.uk/government/publications/algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy/algorithmic-transparency-recording-standard-atrs-mandatory-scope-and-exemptions-policy) (published 17 December 2024) | Mandatory scope is central government. The standard remains recommended for the broader public sector. A tool is in the described class if it has a significant influence on a decision with public effect, or if it directly interacts with the public. This starter does not decide that a council is in mandatory scope. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses. This experiment ships the standard harness and the GitHub Copilot harness. The Customer Conversation harness is the one Microsoft describes for customer voice and chat. It is not implemented here. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. |
| [SI 2018/952](https://www.legislation.gov.uk/uksi/2018/952), the Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018 | A public-sector website or mobile application must meet the accessibility requirement (perceivable, operable, understandable, and robust) and publish an accessibility statement. This command-line starter is not that website. |

Microsoft customer stories about Westminster and Manchester contact-centre agents were not re-opened on 27 October 2026. Figures from those stories are not repeated here.

[Data (Use and Access) Act 2025 section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80) was not re-opened for this experiment. Experiment 03 screens Articles 22A to 22D. This agent does not run that screen and does not record a significant decision.

## What the front door does

`src/front_door.py` reads one JSON enquiry and writes one JSON document. The same enquiry and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. The resident's words are not copied into the output.

**Published answer.** One current, non-statutory page matches. `answer.text` is that page's body, unchanged. The adviser has not yet accepted it.

**No page.** The catalogue does not contain the fact. The draft says so. It does not guess a day, a balance, or a tariff.

**Stale page.** `last_reviewed` is more than the threshold before the as-of date. The default threshold is 180 days. Equal to 180 is not stale. The body is not copied into the answer.

**Statutory contact.** Housing, council tax reduction, and a Blue Badge have a "how to contact the team" page. The draft cites it when it is current and says a person decides. It does not say that anyone qualifies.

**Emergency and vulnerability.** Fixed scripts only. Call 999 if someone is in immediate danger. A person takes the conversation. No service page is quoted, even if a bin day is also in the text.

**Eligibility, account, payment, enforcement.** The matching flags stay false: nothing is decided, nothing is looked up, nothing is taken, nothing is issued. A separate review call cannot turn those flags on.

**Prompt injection.** Instructions to ignore the rules, mark someone eligible, create a case, or send a message are recorded. `followed` is false. A sentence that is only an instruction is not used to choose a page.

**Synthetic only.** A record that is not marked synthetic is refused. The refusal does not echo the text.

`record_adviser_review` is a second function. It accepts `accept_draft`, `reject_draft`, or `take_handover` from a separate review object. It refuses any other decision, including send, case write, and eligibility. `accept_draft` is only recorded for a current published answer. It sets `adviser_accepted_published_text`. It leaves `released_to_resident` false. The agent still has not sent anything.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/13-council-contact-front-door
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/front_door.py --input examples/sample_enquiry.json --as-of 2026-10-27
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A missing catalogue page is not a failed run, and it is not a decision. The exit code is 0 when a draft is produced. A record that is not marked synthetic exits 0 with a refusal. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list. Wording that is not on the list becomes a handover. That is deliberate. It will miss some routine questions a person would have recognised.
- "Example Ward" is the only ward with a bin day. Any other ward is a handover. The page does not invent a day.
- A keyword can false-match. The tests cover the fixtures in this folder. They are not a resident-language study.
- The stale window is a configuration choice for this starter, 180 days unless the caller changes it. It is not a statutory review period.
- The emergency and vulnerability lists are short and explicit. A phrase that is not on the list is not detected. Absence of a flag is not a finding that the resident is safe.
- The draft does not echo the enquiry. An adviser who needs the words still has them on their own screen. This starter does not store them.
- Northmarsh Borough Council, its pages, and its tariff are fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness, which Microsoft describes for resident voice and chat, is not built here. Shipping it as an unattended resolver would sit outside this A1 design.
- This is not legal advice, a data protection impact assessment, or an ATRS submission.

## UK GDPR

The manifest does not assert the council's lawful basis. A candidate for the data protection officer to confirm, before any production use, is Article 6(1)(e), public task, because answering enquiries is part of a council's functions. Do not copy the legal-obligation basis from Experiment 02.

A resident may volunteer health, disability, or safeguarding information. That can be special-category data. The starter does not ask for it, does not store it, and does not assert an Article 9 condition. A production deployment that might receive that text needs the council's own DPIA. This readme is not one.

The agent does not make a significant decision solely by automated means. Eligibility, awards, enforcement, and case outcomes stay with a person. Experiment 03 is the screen against the Data (Use and Access) Act 2025 safeguards. This experiment does not run it.

## ATRS

The scope policy opened on 27 October 2026 puts the mandatory duty on central government. Councils are in the broader public sector, where the standard is recommended, not mandated by that policy. A tool that directly interacts with the public is in the class the policy describes. This starter is an adviser-side draft. It does not itself talk to residents, and it does not submit a record.

If a council later puts a chat in front of residents, Principle 7 of the playbook asks for a clear automated-response line, and the recommended ATRS route is the one to discuss. Experiment 03 drafts a pack. It does not approve or submit one. The mapping in `agent-manifest.yaml` is a pointer for that conversation, not a completed record.

## Two Copilot Studio harnesses

Both call `src/front_door.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness decides, writes a case, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The adviser pastes an enquiry, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- Experiment 03, if a council wants a draft ATRS pack: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).
- Experiment 09, for a drafted reply rather than a front-door answer: [../09-casework-correspondence-draft/](../09-casework-correspondence-draft/).

## Project structure

```
experiments/13-council-contact-front-door/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── front_door.py
│   ├── catalogue.py
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

## References opened on 27 October 2026

- [AI Playbook for the UK Government](https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government/artificial-intelligence-playbook-for-the-uk-government-html)
- [ATRS mandatory scope and exemptions policy](https://www.gov.uk/government/publications/algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy/algorithmic-transparency-recording-standard-atrs-mandatory-scope-and-exemptions-policy)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018](https://www.legislation.gov.uk/uksi/2018/952)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
