# Experiment 42: Case Routing Assistant

Catalogue ID **C003**. A routing proposal for one synthetic case.

Contact centres and public-service teams sort post, email, and web forms into queues. Some cases are ordinary: a missed bin, a leaking tap, a question about opening hours. Some must not be sorted by a script: a safeguarding or hardship indicator, a statutory clock, a request that names a protected characteristic as a reason to pick a queue. This starter reads one case and proposes a queue, a priority, and a reason. It shows a confidence band that counts matched rules. A person confirms before any reroute. The confirmation is a record. The case stays where it was.

**Autonomy A1.** The queue owner approves a material change to a routing rule. An adviser confirms a proposed route, or accepts a human queue. Confirming does not move the case. The agent has no tool that reroutes, closes, escalates, edits a rule, or sends a message.

Stack in the catalogue: Dynamics 365 and Power Platform. The proposal itself is Python in the standard library. It calls [Experiment 15](../15-vulnerability-urgency-scanner/) for indicator categories, and [Experiment 05](../05-awaabs-law-hazard-triage/) when an Awaab's Law illustration is possible. Classification names follow [Experiment 01](../01-foi-complaint-triage/). That experiment's model is not called. Experiment 15 calls [Experiment 08](../08-uk-pii-redaction-gateway/). The redacted text is not copied out.

The organisation in the samples is Northmere Borough Council. It is invented. Case ids are synthetic.

## The problem

A router that moves a case because the text says "close this" or "route by race", or that puts a mould report or a self-harm note on a routine queue, is the failure this starter is built to refuse. The useful narrow job is: read one case, match it to a rule the queue owner has already approved, say why, and stop for a person.

## Non-goals

- Rerouting a case, including after an adviser confirms the proposal.
- Closing a case, or marking it resolved.
- Escalating a case. Proposing a human queue is not an escalation the agent has carried out.
- Changing a routing rule. A queue owner's recorded approval does not edit the rule file.
- Setting a priority on a case system.
- Sending an email, an SMS, a letter, or a chat message.
- Deciding entitlement, eligibility, or a complaint outcome.
- Labelling a person as vulnerable.
- Using a protected characteristic as a feature of a rule.
- Calculating a Freedom of Information or environmental-information deadline. Section 10(6) of the Freedom of Information Act 2000 uses a UK-wide bank-holiday definition. Experiment 05's England and Wales calendar is not used for that Act.
- Stating a subject-access period. Article 12(3) points to Article 12A. Article 12A was not opened.
- Calculating a DISP timescale. DISP was not opened. Experiment 02 was not called.
- Treating a confidence band as a model probability, or letting that band move a human-mandatory case.
- Reading a live queue, a knowledge base, or a case system.
- Using a real council's cases. Northmere is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.
- Deciding that the organisation has complied with the Equality Act 2010, UK GDPR, or the Data (Use and Access) Act 2025.

## What was opened

Opened on 9 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80) | Section 80(1) substitutes Articles 22A to 22D for Article 22. Article 22A(1)(a): a decision is based solely on automated processing if there is no meaningful human involvement in taking it. Article 22A(1)(b): a significant decision produces a legal effect or a similarly significant effect. Article 22C(2) lists information, representations, human intervention, and a way to contest. The page says section 80 is in force at 5 February 2026, in so far as not already in force, by S.I. 2026/82, regulation 2(j). That instrument was not opened. |
| [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22) | The article text is omitted. A footnote records the substitution by section 80(1). |
| [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12) | Article 12(3) requires information on action taken without undue delay and before the end of the applicable time period, and it points to Article 12A. Article 12A was not opened. No number of days is stated. |
| [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19) | Indirect discrimination is a provision, criterion or practice that puts people who share a relevant protected characteristic at a particular disadvantage, unless it is a proportionate means of achieving a legitimate aim. Section 19(3) includes marriage and civil partnership. This starter does not apply that test. |
| [Equality Act 2010, section 29](https://www.legislation.gov.uk/ukpga/2010/15/section/29) | A service-provider must not discriminate in providing the service, as to terms, by terminating it, or by any other detriment. Section 29(7) applies a reasonable-adjustment duty. Section 20 was not opened. |
| [Equality Act 2010, section 149](https://www.legislation.gov.uk/ukpga/2010/15/section/149) | A public authority must have due regard to eliminating discrimination, advancing equality of opportunity, and fostering good relations. Section 149(7) does not list marriage and civil partnership. This starter does not carry out the due-regard assessment. |
| [Freedom of Information Act 2000, section 10](https://www.legislation.gov.uk/ukpga/2000/36/section/10) | Section 10(1), subject to subsections (2) and (3), is the twentieth working day. The day is not calculated. |
| [Environmental Information Regulations 2004, regulation 5](https://www.legislation.gov.uk/uksi/2004/3391/regulation/5) | Regulation 5(2) is 20 working days after receipt. Regulation 2 was not opened. The day is not calculated. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. The Customer Conversation harness is described for contact-centre voice and chat. |

Not opened on 9 November 2026, and not quoted as if they had been: UK GDPR Articles 6, 9, 12A, and regulations under Article 22D; S.I. 2026/82; Equality Act 2010 sections 4, 13, and 20; Environmental Information Regulations 2004 regulation 2; DISP; the Housing Ombudsman Complaint Handling Code; the AI Playbook; the ATRS scope policy. [Experiment 13](../13-council-contact-front-door/) opened the Playbook and the scope policy on 27 October 2026. This experiment did not re-open them.

## What the assistant does

`src/routing.py` reads one JSON case and writes one JSON document. The same case and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. `rerouted` is false. The case text is not copied into the output.

Free text goes through Experiment 15 `scan()`, which calls Experiment 08 before any model. This assistant does not pass a model. It keeps the category ids and the finding count. It does not keep the phrases or the redacted text. `output_is_anonymised` stays false.

**One current approved rule.** A missed bin, a leaking tap, a council-tax payment method, or opening hours. The queue and the reason name the rule id. Confidence is `high` when one rule matches and `medium` when several current rules name the same queue. The adviser may later confirm the proposal. The case is not moved.

**Vulnerability.** Experiment 15 returns a safeguarding, self-harm, or hardship category. The queue is `q-human-vulnerability`. Safeguarding and self-harm are `urgent-human`. Hardship alone is `priority`, and it is still a human queue. The person is not labelled. The confidence band is `not_used`. A sentence that says the person is not vulnerable does not clear the queue.

**Statutory clock.** A freedom-of-information request, an environmental-information request, a subject-access request, a damp or mould report, a DISP kind supplied on the case, or an Experiment 15 deadline phrase. The queue is `q-human-statutory`. If both a vulnerability category and a clock are present, the vulnerability queue is proposed and the clock is still recorded. An Awaab's Law illustration is asked of Experiment 05 only when structured fields are present. Officer-approval flags in the payload are not passed on. No deadline comes back operative. The illustration is not a route.

**Fairness.** An instruction to route by a protected characteristic, or a proposed rule whose feature is one, is not applied. The queue is `q-human-fairness`. The lists used are section 19(3) and section 149(7). Section 4 was not opened. Marriage and civil partnership is refused because it is in section 19(3). No duty is treated as met, and the due-regard assessment is not carried out.

**Adjustment.** A wheelchair, a disability, a reasonable adjustment, British Sign Language, or an interpreter is not used as a feature. The queue is a human review. Section 29(7) is cited. Section 20 is not quoted.

**Entitlement and complaints.** An entitlement question is not answered. A complaint is not placed on a routine queue. DISP is not applied.

**Stale or unapproved.** A rule older than 180 days is not proposed. Equal to 180 days is still current. A draft rule, such as the parking rule in this folder, is not applied. A sentence that says the rule was reviewed today does not clear the stale flag.

**Conflict or no rule.** Neither queue is chosen. Confidence is `low`. A person takes it.

**Prompt injection.** Instructions to ignore the rules, close the case, or route to a bot are recorded. `followed` is false. A sentence that is only an instruction is not used to choose a service rule. It cannot clear a human queue.

**Rule change.** A proposed change is recorded as pending, or refused if the feature is a protected characteristic. It is not used for the case. `queue_owner_approve_rule_change` records the owner's approval and does not edit `src/rules.py`.

**Synthetic only.** A record that is not marked synthetic is refused. The refusal does not echo the text.

`reroute_case`, `close_case`, `escalate_case`, `change_routing_rules`, `set_priority`, `send_message`, `decide_entitlement`, and `label_person_vulnerable` raise `RoutingForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 15, 08, and 05 must be present beside this folder. This experiment does not carry a second copy of them.

```bash
cd experiments/42-case-routing-assistant
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/routing.py --input examples/sample_case.json --as-of 2026-11-09
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once.

The sample is a missed bin. The exit code is 0 when a proposal is produced. A record that is not marked synthetic exits 0 with a refusal. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list. Wording that is not on the list becomes no match or a human review. That is deliberate.
- A keyword can false-match. The tests cover the fixtures in this folder. They are not a study of how residents write.
- The 180-day window is a starter default, not a review duty the organisation already has.
- Experiment 15 is built for recall. Ordinary sentences will flag. Absence of a flag is not a finding that nobody needs extra help.
- The Freedom of Information day, the environmental-information day, and any subject-access period are not calculated. Article 12A, regulation 2, and S.I. 2026/82 were not opened.
- DISP and the Housing Ombudsman Code were not opened. A complaint is held for a person. No timescale is stated.
- Experiment 05 is called only for an Awaab illustration, and never with officer approval. A phase or a date in that module is that module's result. This readme does not restate it as a new finding.
- Experiment 01's model, prompts, and mock responses are not called. Only the classification names are reused.
- Experiment 08 does not redact names. The redacted text is not copied out. A missed identifier can remain in the source the adviser already holds.
- The confidence band is a count of rules. It is not a probability and it has not been calibrated.
- Northmere Borough Council is fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness is not built here. An unattended router on that harness would sit outside this A1 design.
- This is not legal advice, a data protection impact assessment, an equality impact assessment, or an ATRS submission.

## UK GDPR and automated decisions

The manifest does not assert a lawful basis. Article 6 was not opened on 9 November 2026.

A case may include health information. That can be special-category data. Article 9 was not opened. No condition is asserted.

Section 80 and Articles 22A to 22C were read on 9 November 2026. This starter does not take a decision. It does not move a queue. A confirmation record is not meaningful human involvement in a decision the agent then takes, because the agent takes none. A later deployment that writes a queue would have to be assessed by the controller against Article 22A(1). This readme does not make that assessment. Regulations under Article 22D were not opened.

## Two Copilot Studio harnesses

Both call `src/routing.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness reroutes a case or edits a rule. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The adviser pastes a case, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 9 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. The queue in the JSON is the Python rule match. It is not produced by a topic description.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON: which rule matched, why the band was not used, which sentence is a citation. It is not the GitHub Copilot service. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The vulnerability scanner this experiment calls: [../15-vulnerability-urgency-scanner/](../15-vulnerability-urgency-scanner/).
- The statutory clock this experiment calls for an Awaab illustration: [../05-awaabs-law-hazard-triage/](../05-awaabs-law-hazard-triage/).
- The classification names, without the model: [../01-foi-complaint-triage/](../01-foi-complaint-triage/).

## Project structure

```
experiments/42-case-routing-assistant/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 9 November 2026

- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80)
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22)
- [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12)
- [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19)
- [Equality Act 2010, section 29](https://www.legislation.gov.uk/ukpga/2010/15/section/29)
- [Equality Act 2010, section 149](https://www.legislation.gov.uk/ukpga/2010/15/section/149)
- [Freedom of Information Act 2000, section 10](https://www.legislation.gov.uk/ukpga/2000/36/section/10)
- [Environmental Information Regulations 2004, regulation 5](https://www.legislation.gov.uk/uksi/2004/3391/regulation/5)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
