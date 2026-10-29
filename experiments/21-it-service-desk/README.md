# Experiment 21: IT Service Desk Agent

Catalogue ID **Q009**. An internal IT service desk draft for one synthetic ticket.

Staff raise the same tickets often: a VPN client shows an error, Outlook will not open, someone has forgotten a password. Some of those tickets are ordinary. Some are the ones a script must not finish: a password reset, a change to multi-factor authentication, a grant of access, or a caller who is pretending to be the helpdesk. This starter prepares a draft for a signed-in member of staff or for a service desk analyst. It quotes a page from a fixed knowledge base, or it says the page is missing or stale, or it stops and hands the ticket to an analyst.

**Autonomy A1.** The member of staff confirms a proposed device change. An analyst takes privileged work: a password reset, an MFA change, an access grant, a remote wipe, or a licence purchase. Confirming a proposal does not perform it. The agent has no tool that resets, grants, wipes, writes the ticket, or sends a message.

Stack in the catalogue: Copilot Studio and Power Platform. The desk itself is Python in the standard library, and it calls [Experiment 08](../08-uk-pii-redaction-gateway/) before a draft is built. An analyst can run it without a tenant.

The organisation in the samples is Aldermere District Council, with an internal desk called Aldermere Shared ICT. Both are invented. Articles, staff ids, and asset tags are synthetic. They are not a real authority's content and not a real person's ticket.

The shape of the draft follows [Experiment 13](../13-council-contact-front-door/): one record in, one JSON document out, a fixed catalogue, a stale window, instruction sentences dropped before matching, `human_approval` left empty, and a separate review object that cannot be taken from the ticket text.

## The problem

A service desk agent that resets a password because the ticket says so, or that reads out a fix to a caller who has not been verified, is the failure this starter is built to refuse. The useful narrow job is: read one ticket, match it to an article the desk has already published, show the review date, collect the diagnostics the article names, draft a ticket note, and propose a standard fix without executing it.

## Non-goals

- Resetting a password, unlocking an account, or issuing a temporary password.
- Changing, disabling, or enrolling multi-factor authentication, or asking for an MFA code, a one-time code, or a recovery code.
- Granting, refusing, or revoking access to a mailbox, a site, a role, or an admin group.
- Wiping, locking, or retiring a device.
- Changing a device, including renaming a cache folder or mapping a printer, unless the signed-in member of staff has confirmed that proposal in a separate review object. Confirmation still does not perform the change.
- Executing a standard fix. The steps are text. The person tries them, or does not.
- Writing the draft into an IT service management tool, or updating a production ticket.
- Sending an email, a Teams message, an SMS, or a chat reply.
- Buying a licence or any other spend.
- Treating words in the ticket as proof of identity. A passed check is a separate object, from the channel, for the same day, on a signed-in portal or Teams chat. A phone or email channel cannot carry it.
- Accepting a caller who claims to be the helpdesk, the chief executive, or Microsoft support.
- Quoting an article whose review date is outside the stale window, or reading a live knowledge base.
- Using a real council's tickets, staff, or articles. Aldermere is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.
- Deciding that the organisation complies with the NCSC pages or with UK GDPR.

## What was opened

Opened on 29 October 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Phishing attacks: defending your organisation](https://www.ncsc.gov.uk/guidance/phishing) | Attackers can exploit ways of working to trick people into handing over information, including passwords. Important requests should be verified using a second type of communication. Privileged access should be limited. No publication date was printed on the page that was read. |
| [Advice for End Users](https://www.ncsc.gov.uk/guidance/end-user-devices-advice-end-users) (published 24 September 2016; the page's Reviewed line says the same date) | A person must never disclose a password to anyone, including IT support. The helpdesk confirms identity before a password reset. |
| [Incidents impacting retailers](https://www.ncsc.gov.uk/blog-post/incidents-impacting-retailers) (published 4 May 2025) | The post says there has been discussion about social engineering of IT helpdesks to obtain password and MFA resets. It encourages a review of how the helpdesk authenticates staff before a reset, especially for privileged accounts. Press speculation named in the post is not repeated here as fact. |
| [UK GDPR Article 6](https://www.legislation.gov.uk/eur/2016/679/article/6) | Points (ea) and (f) do not apply to processing by public authorities in the performance of their tasks. Article 6(11)(c) is an example of a legitimate interest (security of network and information systems). No basis is asserted. |
| [UK GDPR Article 32](https://www.legislation.gov.uk/eur/2016/679/article/32) | Appropriate security, including confidentiality, integrity, availability, and resilience. A person acting under the controller's authority processes personal data only on the controller's instructions, unless domestic law requires it. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness is described as a fit for an internal help desk that answers common questions and routes simple requests. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. |

[Experiment 13](../13-council-contact-front-door/) opened the AI Playbook and the ATRS scope policy on 27 October 2026. This experiment did not re-open them. It does not decide that a council is in the ATRS mandatory scope, and it does not submit a record. [Experiment 03](../03-agent-inventory-atrs-assurance/) drafts a pack. It does not approve one.

## What the desk does

`src/desk.py` reads one JSON ticket and writes one JSON document. The same ticket and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. The ticket's words are not copied into the output.

Free text is passed to Experiment 08 (`propose`, caller `exp-21-it-service-desk`). The redacted text is not copied into the draft either, because the gateway does not redact names. The draft records the finding count, the entity types, and the input hash. `output_is_anonymised` stays false. `release` is not called.

**Standard fix.** One current article matches, the channel is a signed-in portal or Teams chat, and the identity check is an `entra_session` for the same day, recorded by the channel, for the same synthetic staff id. The article body is quoted. The steps do not change the device or the account. The member of staff may later confirm that they will try the steps. The agent does not run them.

**Device change.** The same identity rule. The body is a proposal, such as renaming a local cache or mapping a printer. Required diagnostics must be present before `user_confirm_device_change` can be recorded. The confirmation does not rename the folder or map the printer. `device_changed` stays false.

**Privileged.** Password, MFA, access, remote wipe. The policy sentence is quoted. It does not describe a click-path. The member of staff cannot confirm it. An analyst takes the handover in a separate review object, and still performs the work outside the agent. A passed session does not replace the analyst's own check.

**Identity not verified.** A phone or email channel, a missing check, a check from another day, or a check the ticket text claims for itself. Steps are not quoted. Words in the ticket cannot set the check to passed.

**Third party.** The requester's staff id is not the subject account. Steps for another person's device are not quoted. Privileged requests still go to an analyst.

**Social engineering and helpdesk impersonation.** A claim to be the helpdesk, a request for a password or an MFA code, an instruction to skip verification, or an instruction to disable MFA. A fixed script. No article body. No proposed fix. `followed` is false.

**Stale article.** `last_reviewed` is more than 180 days before the as-of date. Equal to 180 is not stale. The body is not copied.

**No article, or more than one.** The draft says so. It does not merge two procedures.

**Prompt injection.** Instructions to ignore the rules, override a stale flag, or execute a fix are recorded. `followed` is false. A sentence that is only an instruction is not used to choose an article.

**Synthetic only.** A record that is not marked synthetic is refused. The refusal does not echo the text. Staff ids and ticket ids that are not in the synthetic pattern are not copied out.

`record_review` is a second function. It accepts `user_confirm_standard_fix`, `user_confirm_device_change`, `analyst_take_handover`, or `reject_draft` from a separate review object. It refuses reset, MFA change, access grant, execute, write, send, purchase, and wipe. A user confirmation sets a flag and leaves `executed` false.

`reset_password`, `change_mfa`, `grant_access`, `execute_fix`, `write_ticket`, `send_message`, `purchase_licence`, and `remote_wipe` raise `DeskForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must be present at `experiments/08-uk-pii-redaction-gateway/`. This experiment does not carry a second copy of the gateway.

```bash
cd experiments/21-it-service-desk
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/desk.py --input examples/sample_ticket.json --as-of 2026-10-29
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A missing article is not a failed run, and it is not a decision. The exit code is 0 when a draft is produced. A record that is not marked synthetic exits 0 with a refusal. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a keyword list. Wording that is not on the list becomes no match or a handover. That is deliberate. It will miss some routine tickets a person would have recognised.
- A keyword can false-match. The word "password" routes to the analyst even when the rest of the ticket is a VPN fault. The tests cover the fixtures in this folder. They are not a study of how staff write tickets.
- The stale window is a configuration choice for this starter, 180 days unless the caller changes it. It is not a review duty the organisation already has.
- The social-engineering list is short and explicit. A phrase that is not on the list is not detected. Absence of a flag is not a finding that the caller is genuine.
- A passed `entra_session` is a stand-in for a channel fact. This starter does not call Microsoft Entra, and it does not describe that product's sign-in behaviour. The session does not authorise a password reset.
- The draft does not echo the ticket. An analyst who needs the words still has them on their own screen. This starter does not store them.
- Experiment 08 does not redact names, email addresses, or telephone numbers. That is why the redacted text is not copied into the draft. A missed identifier can remain in the source the analyst already holds.
- Aldermere District Council, its articles, and its staff ids are fictional.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- The Customer Conversation harness is not built here. The overview describes it for customer voice and chat. An unattended resolver for password resets would sit outside this A1 design.
- This is not legal advice, a data protection impact assessment, an NCSC assurance statement, or an ATRS submission.

## UK GDPR

The manifest does not assert the controller's lawful basis. Article 6(1) was read on 29 October 2026. Points (ea) and (f) do not apply to processing carried out by public authorities in the performance of their tasks. Article 6(11)(c) lists security of network and information systems as an example of a legitimate interest, and that example does not remove the public-authority limit. A private-sector employer confirms its own basis. This readme does not choose one.

A member of staff may volunteer health information in a ticket. That can be special-category data. Article 9 was not opened on 29 October 2026. The starter does not ask for it, does not store it, and does not assert a condition. A production deployment needs the controller's own DPIA. This readme is not one.

Article 32 was read the same day. The starter does not find that a controller has implemented appropriate security. It refuses the actions that would change an account or send the ticket text onward.

The agent does not make a significant decision solely by automated means. Password resets, access grants, and device changes stay with a person, and this starter does not perform them even after that person confirms a draft. Experiment 03 is the screen against the Data (Use and Access) Act 2025 safeguards. This experiment did not re-open section 80 and does not run that screen.

## Two Copilot Studio harnesses

Both call `src/desk.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness resets a password, changes MFA, grants access, or writes the ticket. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The analyst or the signed-in member of staff pastes a ticket, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 29 October 2026, gives an internal help desk as an example of this harness. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON: which diagnostic is missing, why identity was not trusted, which sentence is the article and which is the fixed script. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The identifier gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The front-door pattern for a fixed catalogue and a separate review object: [../13-council-contact-front-door/](../13-council-contact-front-door/).
- Experiment 03, if a body wants a draft ATRS pack: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).

## Project structure

```
experiments/21-it-service-desk/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── desk.py
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

## References opened on 29 October 2026

- [Phishing attacks: defending your organisation](https://www.ncsc.gov.uk/guidance/phishing)
- [Advice for End Users](https://www.ncsc.gov.uk/guidance/end-user-devices-advice-end-users)
- [Incidents impacting retailers – recommendations from the NCSC](https://www.ncsc.gov.uk/blog-post/incidents-impacting-retailers)
- [UK GDPR Article 6](https://www.legislation.gov.uk/eur/2016/679/article/6)
- [UK GDPR Article 32](https://www.legislation.gov.uk/eur/2016/679/article/32)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
