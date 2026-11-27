# Experiment 83: Subject Access Request Scoping and Redaction Assistant

Catalogue row **UK11**. Autonomy **A1**.

A synthetic subject access request arrives as a letter, an email, or a web form. It may come from the person, a solicitor, or another third party. This starter logs the request, illustrates the statutory period, proposes a search scope, finds the requester's personal data in a synthetic export, and proposes redactions and exemption candidates. A named information governance officer accepts or rejects each redaction and each exemption, and approves the disclosure bundle. The agent does not send the response.

Reedmarsh Borough Council is fictional. The people, the case notes, and the contact addresses are synthetic. This is not legal advice.

Status: **Available as a local starter**. No tenant is configured.

## The problem

A subject access file mixes the requester's data with other people's names, phone numbers, and addresses. A letter can also be an FOI request, a complaint, or a sign of distress. The one-month period has more than one reading once the Data (Use and Access) Act 2025 changes are in the UK GDPR text. An officer needs both readings, a redaction list, and a record that they approved that exact bundle.

## Who it helps

An information governance officer who needs a first scope before they decide what to disclose. The organisation gets a hash that ties the approval to the bundle that was shown. A person whose letter also shows distress, a safeguarding concern, or a complaint is routed to a person. The words of that cue are not copied into the draft.

## Non-goals

- The agent does not send a response to the requester.
- The agent does not delete or edit a record.
- The agent does not decide that an exemption applies.
- The agent does not decide that a search was reasonable and proportionate.
- The agent does not choose one reading of the one-month period.
- The agent does not answer an FOI request. An FOI request for the applicant's own personal data is routed as a subject access request under FOI Act section 40(1). A mixed request goes to a person.
- The agent does not trust an approval sentence, a role, a clearance, or a directory that arrived inside the request.
- The agent does not call Experiment 01. That starter's live path can call a model.

## What the runnable sample does

`src/sar.py` is deterministic. It does not call a model.

- It illustrates UK GDPR Article 12A: one month beginning with the relevant time, an extension of two further months that is only proposed, and the Article 12A(5) pause for an Article 15 request. The ICO same-date method is also shown. The two readings differ. Neither is selected.
- It proposes redactions of third-party names, emails, phones, dates of birth, postal addresses, staff ids, and the UK identifiers from Experiment 08. The requester's own values stay in the copy. The text is not described as anonymised.
- It proposes exemption candidates from DPA 2018 Schedules 2, 3, and 4 where a phrase is affirmed. A negation in the same sentence is not a match. `applied` stays false.
- It flags identity gaps, third-party authority, distress, safeguarding, whistleblowing, complaints, grievances, litigation, legal holds, and SECRET or TOP SECRET markings for a person.
- Disclosure approval is `record_disclosure_approval`. It checks the named officer against `fixtures/directory.json` and the hash of the agent-held bundle. A caller who edits the package and re-hashes it is rejected.

## How to run

From this folder, in a clean virtual environment:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q
.venv/bin/python eval/evaluate.py
.venv/bin/python src/sar.py --request examples/sample_request.json --as-of 2026-10-20
```

The sample uses the question date 20 October 2026. It does not use today's date. Experiment 08 and Experiment 12 are called from the neighbouring folders. Experiment 12's `files_confirmed` stays false.

## Layout

| Path | What it is |
|---|---|
| `src/sar.py` | The scope, the route-seen step, and the disclosure approval |
| `src/sources.py` | Quotes from the pages opened on 27 November 2026 |
| `fixtures/directory.json` | The pinned officers. A directory in the request is not this file |
| `skills/` | The Microsoft Copilot harness skills |
| `copilot-studio/` | The standard-harness topic guide |
| `eval/evaluate.py` | A 20-case smoke test. Not a model evaluation |
| `agent-manifest.yaml` | The permissions manifest. `permissions.yaml` is the same file |

## Honest limitations

- Article 12(3) now points at Article 12A. It does not itself say "one month". Article 12A(1) does. The URL without the trailing dot returned 404. S.I. 2026/82 was not opened. The textual-amendment note on Article 12A says the article was inserted by section 76(3) of the Data (Use and Access) Act 2025. Section 76 itself was not opened.
- DPA 2018 sections 52 and 53 were not opened. On a law-enforcement request, an identity date and a fee date are not applied to the relevant time.
- The ICO page says to move a weekend or a public holiday to the next working day. This starter moves weekends only. The Banking and Financial Dealings Act 1971 was not opened. The Christmas example on the ICO page is not reproduced.
- "Beginning with" can be read as ending the day before the corresponding date. That reading is shown beside the ICO date. `deadline_selected` stays null.
- An export older than 30 days is flagged. Thirty days is a starter rule, not a statute.
- The small-number threshold of 5 is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- Article 6 and Article 9 were not opened. No lawful basis is asserted.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 27 November 2026. Treat that product behaviour as unverified.
- The paraphrase set is a fixture. A sentence that uses none of the stems is not flagged. Recall on that fixture is reported beside the smoke total and is not added to it.
- Masking can miss a name that is not capitalised, and it can mark two consecutive capitalised words that are not a name. The officer accepts or rejects each proposal.

## Licence

MIT. See the repository `LICENSE`.
