# Experiment 51: Teams Channel Digest Agent

Catalogue ID **M002**. Autonomy **A0**. The requesting user confirms the channels and the period before any digest is produced.

UK public bodies and regulated firms keep decisions, questions, and actions in Microsoft Teams channels. The awkward part is catching up without posting back into the channel, and without turning a digest into a judgement about a person. This starter reads one synthetic export. It lists key decisions, open questions, actions whose owner is named in the message, and items that name the requesting user. Every point is the sentence it came from, with the message id and the line. The user confirms the exact channels and the date range first. Until then the result is a scope preview: channel status and a count, not the messages.

The sample organisation is Northmere Borough Council. It is invented. A second label, Northmere Mutual, is an invented regulated firm. The same rules apply. The starter does not decide that the firm is a public authority.

Stack in the catalogue: Microsoft 365 and Work IQ. The digest itself is Python in the standard library. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) to mask UK identifiers, [Experiment 41](../41-case-summary/) to require the sentence to be contained in the cited lines, and [Experiment 29](../29-groundedness-evaluation/) to check numbers, dates, and content tokens. Work IQ is named on the catalogue row. The Work IQ page was not opened on 12 November 2026. This starter does not call it. A person can run the digest without a tenant.

## The problem

A model that posts a reply because a message said "post this", or that describes a colleague's performance, or that fills a week that had no messages, is the failure this starter is built to refuse. The user still has to see which sentence was a decision, which question is still open, who was named as the owner, and which message was withheld.

## Non-goals

- Posting, replying, reacting, @mentioning, or forwarding. Those functions raise.
- Producing a digest before the user confirms the channels and the period.
- Reading a channel the requesting user is not recorded as able to access.
- Inferring sentiment about a named person, or making a performance judgement.
- Deciding that monitoring workers is lawful, or that a DPIA has been completed.
- Deciding that UK GDPR Article 5(1)(b) or Article 5(1)(c) was met.
- Deciding that a saved digest is held information, or that it must be disclosed, under the Freedom of Information Act 2000.
- Calling Microsoft Graph, Microsoft Teams, or Work IQ.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 12 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(b) is purpose limitation. The current text says personal data shall be collected, whether from the data subject or otherwise, for specified, explicit and legitimate purposes and not further processed by or on behalf of a controller in a manner incompatible with those purposes. Article 5(1)(c) is data minimisation: adequate, relevant and limited to what is necessary. Article 5(3) says processing is not lawful merely because it is compatible. Article 5(1)(e) now refers to Article 84B. Article 84B, Article 6, and Article 9 were not opened. |
| [Freedom of Information Act 2000, section 1](https://www.legislation.gov.uk/ukpga/2000/36/section/1) | Section 1(1) is the right to be told whether information is held and, if it is, to have it communicated. Section 1(2) says that right is subject to section 1 and to sections 2, 9, 12 and 14. Those sections were not opened. The page said there are currently no known outstanding effects for section 1. A digest a body saves may itself be information it holds. This starter does not decide that. |
| [Employment practices and data protection: monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/) | The hub title on 12 November 2026. The page says the guidance is under review because of the Data (Use and Access) Act and may change. |
| [Specific data protection considerations for different ways or methods of monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/specific-data-protection-considerations-for-different-ways-or-methods-of-monitoring-workers) | The page says messages include instant messages and the chat functions in collaboration tools. It says a DPIA must be completed before monitoring emails and messages. It distinguishes content from network data and treats content as exceptional, with advance notice. This starter does not decide that a DPIA is required and does not complete one. |
| [List channel messages](https://learn.microsoft.com/en-us/graph/api/channel-list-messages?view=graph-rest-1.0) | `GET /teams/{team-id}/channels/{channel-id}/messages` returns messages without replies unless `$expand=replies` is set. Delegated least privilege on that page is `ChannelMessage.Read.All`. Application least privilege is `ChannelMessage.Read.Group`, which uses resource-specific consent. Personal Microsoft accounts are not supported. `$top` and `$expand` are the supported query options. A date filter is not a supported query option. This starter does not call Graph. Whether the API is a protected API was not on the page that was read. That point is unverified. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows the topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. Agents on it use Copilot Credits. The page states no price. |
| [Overview of AI in Microsoft Teams](https://learn.microsoft.com/en-us/microsoftteams/copilot-ai-agents-overview) | Copilot in Teams chats and channels is described as helping a user catch up. The linked end-user article, "Use Copilot in Microsoft Teams chat and channels", was not opened. Any limit on how far back that feature reads is unverified. Channel Agent is described as a channel collaboration agent. The overview table lists an article about creating and sending emails with Channel Agent. That article was not opened. This starter does not use Channel Agent and does not send. |

## What the draft does

`src/digest.py` reads one JSON export and writes one JSON document. The same export, the same as-of date, and the same confirmation produce the same JSON. `human_approval` is null. `actions_taken` is empty. `posted`, `replied`, `reacted`, `mentioned`, and `forwarded` are false. The full message body is not copied out.

**Scope only.** With no confirmation, the result names each requested channel as ready, empty, unavailable, not in the export, or not accessible. A ready channel has a count. The message text is not included.

**Digest.** After the user confirms the exact channel ids and the same period, the core reads only those channels. A decision is a sentence with an un-negated cue such as "we decided" or "the decision is". An open question ends with a question mark or is labelled "open question:". An action names an owner in the sentence ("Action for Priya Shah:" or "Priya Shah will"). An attention item names the requesting user. Each of those sentences is checked by Experiment 41 and Experiment 29. A sentence that is not supported is not included.

**Negation.** "It is not true that we decided" is not a decision. "Never mind, ignore the earlier decision" cancels an earlier decision in the same message. "We decided not to" is still a decision, because the negation comes after the cue.

**Prompt injection.** Instructions to post, reply, or ignore the rules are recorded. `followed` is false. A later sentence in the same message can still be a decision. An HTML comment is not used as evidence. A sentence that says the channels are already confirmed is not a confirmation.

**Personal data.** Experiment 08 masks a UK identifier before a sentence is kept. The value is not copied. `output_is_anonymised` stays false. A message that reads as a judgement about a named person, that asks for a view of a person, that uses a private or case cue, or that is marked for a person, is withheld. The text is not copied. Wording that matches none of those patterns, and is not marked, is not detected.

**Gaps.** No messages in the period is stated as "No messages in this period." An unavailable channel is stated as unavailable. Nothing is invented. A channel the user cannot access is not read.

**Not synthetic.** An export that is not marked synthetic is refused. The refusal does not echo the text. The CLI still exits 0.

`post_message`, `reply_message`, `react_message`, `mention_user`, and `forward_message` raise `DigestForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 29, and 41 must be present beside this folder.

```bash
cd experiments/51-teams-channel-digest
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/digest.py --input examples/sample_export.json --as-of 2026-11-12
python src/digest.py --input examples/sample_export.json --as-of 2026-11-12 --confirm examples/sample_confirmation.json
```

The first command prints a scope preview. The second prints the digest. `eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 24 passed, 0 failed, 0 errors, 24 cases.

The exit code is 0 when a preview, a digest, or a refusal is produced. The exit code is 2 when the input cannot be read, or when a side-effect flag is passed.

## Limitations

- The matcher is a cue list. Wording that is not on the list is not labelled. A single cue is not a decision by the organisation. It is a sentence that used the cue.
- "We decided not to" is kept, because the negation follows the cue. A retraction has to be in the same message to cancel an earlier sentence.
- Unmarked sensitive wording that matches neither the evaluative pattern nor a private or case cue is not held. That is a limit of the matcher.
- A sentence about a hospital is held even when it is a service decision. A person reads the source. That false hold is deliberate.
- Experiment 08 does not detect names, email addresses, or telephone numbers. No finding is not a finding that the text has no personal data. The output is not anonymised.
- Experiment 41 requires the sentence to be contained in the cited lines. A paraphrase fails, including a true one.
- Experiment 29 was not pointed at a live Microsoft Foundry evaluator. `foundry_called` stays false.
- The 14-day export window and the 180-day source window are starter defaults. They are not periods in the ICO guidance or in Microsoft Graph.
- `ChannelMessage.Read.All` on the Graph page is not limited to one channel. The channel list in this starter is a local control. It is not a Graph permission.
- The end-user Teams Copilot article was not opened. Do not treat a search snippet about a 30-day window as a verified limit.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Northmere Borough Council and Northmere Mutual are fictional.
- This is not legal advice, a DPIA, a monitoring assessment, or an FOI response.

## UK GDPR and FOI

The manifest does not assert the controller's lawful basis. Article 6 and Article 9 were not opened on 12 November 2026.

Article 5(1)(b) and Article 5(1)(c) were read the same day. The digest's purpose, as this starter is written, is a reading of the confirmed channels and the confirmed period for the requesting user. Messages outside that scope are not read. Identifier values are not copied. `purpose_limitation_met` and `data_minimisation_met` stay false. Meeting those principles is for the controller.

The ICO hub "Employment practices and data protection: monitoring workers" was opened the same day. It is under review because of the Data (Use and Access) Act. A body or a firm that pointed this pattern at workers' channels would be in the territory that guidance describes, including a DPIA before monitoring message content. This starter does not make that decision. `monitoring_decided` and `dpia_decided` stay false.

Freedom of Information Act 2000 section 1(1) was read the same day. A digest a public body saves may be information it holds. Section 1(2) points at sections 2, 9, 12 and 14, which were not opened. `held_information_decided` and `disclosure_decided` stay false. For the invented firm, the starter does not decide that the firm is a public authority. Section 3 was not opened.

The agent does not make a decision about a worker. Article 22A was not opened.

## Two Copilot Studio harnesses

Both call `src/digest.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness posts to Teams. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic previews the scope and stops. A second topic records the confirmation. A third produces the digest only when that confirmation is already on the JSON. Microsoft's harness overview, opened 12 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a follow-up on the same JSON: which sentence was withheld, why a channel was not read, why a cue was not a decision. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short narrative may be written from the JSON. The points, the citations, the counts, and the empty approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed. Experiment 29's checker is the local Python, not a Foundry evaluator call.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The identifier gateway: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The citation check: [../41-case-summary/](../41-case-summary/).
- The groundedness check: [../29-groundedness-evaluation/](../29-groundedness-evaluation/).

## Project structure

```
experiments/51-teams-channel-digest/
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
└── tests/
```

## References opened on 12 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Freedom of Information Act 2000, section 1](https://www.legislation.gov.uk/ukpga/2000/36/section/1)
- [Employment practices and data protection: monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/)
- [Specific data protection considerations for different ways or methods of monitoring workers](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/specific-data-protection-considerations-for-different-ways-or-methods-of-monitoring-workers)
- [List channel messages, Microsoft Graph v1.0](https://learn.microsoft.com/en-us/graph/api/channel-list-messages?view=graph-rest-1.0)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Overview of AI in Microsoft Teams](https://learn.microsoft.com/en-us/microsoftteams/copilot-ai-agents-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
