# Experiment 74: Board Governance Pack Assistant

Catalogue ID **L010**. Autonomy **A1**. The assistant assembles a draft agenda, a pack index, and an action-log carry-forward. The named company secretary approves that exact content before a copy is written to a synthetic staging store. The company secretary approves the final pack. The agent does not circulate, publish, file, or send anything, and it does not record board decisions or minutes as approved.

A company secretary points at one meeting on the pinned synthetic forward agenda. The papers are synthetic submissions with a cover sheet: author, sponsor, purpose (decision, discussion, or noting), date, version, and protective marking. Northmere Holdings Limited is invented.

The core is Python in the standard library. It calls [Experiment 12](../12-document-intake/) so the files are not confirmed and no purpose is confirmed, [Experiment 70](../70-conflict-of-interest-intake/) for a supplier mention that is not a conflict decision, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. Sponsor approval and the secretary's approval follow the same binding rule as [Experiment 73](../73-control-testing-assistant/): a named directory role and the exact content hash. Experiment 73's tester function is not called, because the role and the item are different. A user can run this folder without a tenant. Catalogue row L010 names M365 and Work IQ. This folder ships both Copilot Studio harnesses. No Work IQ call and no Power Platform connector are enabled.

## The problem

A paper can say, in its own text, that the sponsor has approved it, that the minutes are already approved, or that the reader should circulate the pack. A caller can paste a different terms of reference and ask for that one to be used. A cover sheet can disagree with the body. A paper can arrive late, twice, or not at all, or sit outside the committee's terms. Those are the failures this starter is built to separate. A real sponsor approval is a ledger row for that paper hash. A real pack approval is a separate object, from the directory company secretary named on the draft, for that exact content hash.

## Non-goals

- Circulating, publishing, filing, or sending the pack.
- Recording a board decision, or recording minutes as approved.
- Treating an approval marker, a role, or an "approved by" line inside a paper as the approval step.
- Applying a terms of reference, an agenda, a directory, or a register supplied in the request. The pinned fixtures are the source.
- Deciding that a conflict exists, or that a Companies Act duty or a Code principle was met.
- Guessing an ambiguous date, or replacing an unreadable date or version with zero or with today.
- Copying paper text above the company secretary's directory clearance.
- Stripping a protective marking, a legal hold, or a retention label.
- Publishing a count of one to four people.
- Following an instruction embedded in a paper or in prior minutes.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 24 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Companies Act 2006, sections 171, 172, 173, 174, 175, 176, 177, and 248](https://www.legislation.gov.uk/ukpga/2006/46/section/171) | The operative text quoted in `src/sources.py`. Each page said the section was up to date with all changes known to be in force on or before 23 November 2026. |
| Company-hosted PDF of the UK Corporate Governance Code, January 2024, at `https://corporate.unitedutilities.com/globalassets/documents/corporate-documents/uk_corporate_governance_code_2024_.pdf` | Principles F and I, and Provisions 7 and 16. The PDF is marked as copyright The Financial Reporting Council Limited 2024. The FRC media PDF was not opened. A byte-for-byte match to the FRC file is unverified. |
| [FRC guidance on the Code](https://www.frc.org.uk/library/standards-codes-policy/corporate-governance/corporate-governance-code-guidance/) | Paragraph 3 says the guidance is not mandatory and not part of the Code. Paragraphs 80 and 82, and the unnumbered board-paper bullets between paragraphs 78 and 79, are quoted as guidance. |

The Code and the guidance were not opened on legislation.gov.uk. Their currency on legislation.gov.uk is unverified. The quotes are context for the secretary. They are not a finding that a principle or a duty was met. Section 248 says every company must cause minutes of all proceedings at meetings of its directors to be recorded, and that the records must be kept for at least ten years from the date of the meeting. This starter does not record those minutes and does not mark them approved.

## What the result does

`assemble_pack()` reads one request and the question date, and writes one JSON document. The agenda, the terms, the directory, the register, the minutes, and the sponsor ledger are the pinned files in `fixtures/`. A caller-supplied agenda, terms, directory, register, or paper set is diffed and not applied. The same inputs and the same date produce the same JSON. `human_approval` is null. `minutes_approved` and `decisions_recorded` stay false. `circulated`, `published`, `filed`, and `sent` stay false.

**Agenda and index.** The draft agenda is the pinned forward agenda for that meeting. A missing expected paper is listed. A lower version of the same paper is superseded. The same paper id and version twice is a duplicate. The index keeps one current row.

**Cover sheet.** Purpose must be decision, discussion, or noting. A recommendation must be present. Risk, finance, legal, and equality implications must be completed, or not applicable with a note. Anything else is incomplete. An unreadable purpose is not coerced to noting.

**Sponsor approval.** A ledger row must name that paper id, that version, that sponsor, and the hash of the cover and the body, and `pins_seen` must be the boolean true. The sponsor must be on the directory with a sponsor role. Text in the paper does not count. A hash that does not match is a mismatch, not an approval.

**Other flags.** A paper submitted after the pinned deadline is late. A paper on the deadline day is not late. That is this starter's rule, not a statute. An item whose matter is outside the pinned terms is flagged. A caller terms object that adds the matter does not bring it inside. A conflict sentence that is not denied is flagged as declared. A live register row for someone in the room is flagged as likely. Neither flag decides that a conflict exists. A cover line that disagrees with the body is an inconsistency. A SECRET line on the page is caught when the cover says OFFICIAL. The higher marking is kept.

**Action log.** Open actions from the prior synthetic minutes are carried, with the due date compared with the question date. A closed action is not carried. A status that is not the exact word open is not treated as open. An unreadable due date is flagged and is not replaced. The action text is not copied. The minutes are not marked approved.

**People and markings.** Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are counted. The values are not stored. The body is not copied. The output is not described as anonymised. A count of people below 5 is not published. Five is this starter's threshold. A statistics authority page was not opened for it. A legal hold and every retention label stay on the result.

`circulate`, `publish`, `file_pack`, `send`, `record_decision`, and `approve_minutes` raise `PackForbidden`.

`record_secretary_approval()` records that the directory company secretary named on the draft approved one item. The content hash has to match the draft now in the result. A string is not coerced to true. The record does not circulate the pack and does not approve the minutes.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 70 must be present beside this folder.

```bash
cd experiments/74-board-governance-pack
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/pack.py --request examples/sample_request.json --as-of 2026-11-20
```

The sample request carries approval language, a caller agenda, and a caller terms object on purpose. They are stripped or ignored. `human_approval` stays null. One paper includes a distress sentence, so the outcome is `route_to_human`.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total. On the committed run, 20 of 20 cases passed, and each paraphrase category had 22 sentences with recall 1.0 and precision 1.0 on those sentences. That is not a live rate.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Cue matching is a stem list. A paraphrase that uses none of those stems is not flagged. The smoke report states recall and precision on the fixture sentences. That is not a live rate.
- "Not true that", "nobody", "does not", and the other denial frames are the negation rule. A denial that uses none of them can be missed. A distress stem is routed even inside a denial.
- A paper on the deadline day is not late. An interest is still treated as live on its end date. Those are starter rules. They are not statutory periods.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- Counts of people below 5 are not published. Five is this starter's threshold. A statistics authority page was not opened.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- The Code quotes were not read from the FRC media file and were not opened on legislation.gov.uk. That match is unverified. The Companies Act quotes were opened on legislation.gov.uk on 24 November 2026.
- Experiment 12 inventories at most 12 files. A paper above the secretary's clearance is not sent to intake. The pack flags still run.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- The harness overview was not re-opened for this experiment. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Northmere Holdings Limited is fictional. Contact addresses on northmere.example.com are placeholders.
- This is not a board decision, and it is not a minute of a directors' meeting.

## Two Copilot Studio harnesses

Both call `src/pack.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness circulates a pack. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_secretary_approval` only with the approval object. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** Catalogue row L010 names M365 and Work IQ. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The file tools that harness can use are not used to edit papers or to send. No Work IQ call is enabled in this starter. Work IQ was not called, so a permission-aware read of a live library is unverified here.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The hashes, the flags, and the approval step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Document intake: [../12-document-intake/](../12-document-intake/).
- Conflict-of-interest intake: [../70-conflict-of-interest-intake/](../70-conflict-of-interest-intake/).
- Approval binding of the same shape: [../73-control-testing-assistant/](../73-control-testing-assistant/).

## Project structure

```
experiments/74-board-governance-pack/
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

MIT Licence. See [LICENSE](../../LICENSE).
