# Experiment 18: Evidence Pack Builder

Catalogue ID **L004**. Autonomy **A1**. The catalogue checkpoint is "Exact export approval required". Stack in the catalogue: Copilot Studio GitHub Copilot harness and Microsoft 365. What you can run today is Python in the standard library. It calls [Experiment 12](../12-document-intake/) (O001, document intake), which calls [Experiment 08](../08-uk-pii-redaction-gateway/) (O005, the UK identifier PII gateway). This experiment does not ship a second inventory or a second redactor.

A named person supplies one synthetic set of items, the pack type, the scopes they are authorised to search, and a search period. The agent returns a draft manifest: each in-scope item's source, date, and SHA-256, a proposed index and page order, duplicates, and flags for possible third-party personal data and possible privileged material. `export_approved` and `redactions_approved` stay false. The export index is produced only after an **Evidence pack approver** records the exact item list and the redaction decisions. That index does not contain document bodies. The agent never sends it.

Samples are synthetic. Reedbank Borough Council is fictional. National Insurance and NHS values are the non-allocatable fixtures documented in Experiment 08. No real person, firm, or case is in the pack.

## The problem

A subject access bundle, a regulator or audit request, a complaint file that might later go to an ombudsman, or an internal investigation all start the same way. Someone has to say which items are in the authorised scope, which copy is the duplicate, which page it would sit on, and which items need a person to look at third-party data or privilege before anything leaves the building. Doing that inside a mailbox, with a sentence in a letter allowed to mark the pack approved, is how the wrong items get disclosed.

This starter is the index. The disclosure, the ombudsman referral, and the exemption decision stay with a named person.

## Who it helps

**The person assembling the pack.** They see what was inside the scopes they named, what was left out, the hash and date of each candidate, and a proposed page order. A document cannot add a scope or set the search period.

**The evidence pack approver.** They approve the exact list of item ids, and a redaction decision for any item flagged for possible privilege or possible third-party personal data. Until they do, there is no export index. After they do, the index is still not sent.

**A privacy reviewer reading a subject-access pack.** UK identifier spans come from Experiment 08, via Experiment 12. The draft does not decide that [Data Protection Act 2018, Schedule 2, paragraph 16](https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/16) or [paragraph 19](https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/19) applies. Those provisions are cited so the approver can see why the flag exists.

**A reader of Experiment 12.** That intake names UK11 and UK09 as later rows and does not call them. This folder is not those rows. It calls the intake. It still does not disclose anything.

## Non-goals

- Approving, refusing, or narrowing a subject access request, including a decision that the search was reasonable and proportionate under UK GDPR Article 15(1A).
- Applying a Schedule 2 exemption, including paragraph 16 (rights of others) and paragraph 19 (legal professional privilege).
- Deciding that information is privileged, or that another person can be identified, or that disclosure without consent would be reasonable.
- Disclosing personal data to a data subject, or sending a pack to the Financial Ombudsman Service, the Housing Ombudsman, a regulator, a complainant, or anyone else.
- Writing a production record, including Dataverse, SharePoint, a case system, or a mailbox.
- Searching a store the caller did not paste. There is no Microsoft 365 search in this starter. Scopes are a closed list checked against the pasted items.
- Releasing redacted text, storing a reversible token map, or describing the text as anonymised.
- Re-implementing Experiment 08 or Experiment 12.
- Reading a PDF, an image, or a scan. Those media types stay unread.
- Setting the pack type, the authorised scopes, or the search period from a sentence inside an item.
- Autonomy A3. There is no path on which the agent approves the export or sends it.

## What the builder does

`src/pack.py` reads one JSON request and writes one JSON document. The same request, pack type, scopes, search period, and as-of date produce the same JSON. `export_approved` and `redactions_approved` are false. `approver_name` is null. `actions_taken` is empty.

**Scopes.** The closed list is `case_file`, `correspondence`, `complaints_log`, `repairs_log`, `audit_workpapers`, and `investigation_notes`. Only `authorised_scopes` passed to `build_pack` is used. The same fields on the JSON, and any sentence in an item, are ignored and listed. An item whose `source_scope` is outside that argument is `out_of_scope`. It is not passed to Experiment 12, it is not hashed into the candidate manifest, and its body is not copied. An empty scope list excludes every item.

**Search period.** `search_from` and `search_to` are arguments, inclusive. If either is missing, nothing is proposed for export. A date after the as-of date is `future` and is not proposed. A date outside the period is `outside_period`. The period is not a finding that the search was reasonable and proportionate.

**Intake.** In-scope items are passed to Experiment 12 `intake()`, with a purpose preview of `sar_bundle` or `evidence_bundle` according to the pack type. The preview is not confirmation. This draft keeps the hash, the read status, the keyword class, the intake date status, and the Experiment 08 entity types. It does not keep the body, the redacted text, or the raw identifiers.

**Duplicates.** A repeated SHA-256 is `duplicate_of` the earlier item id. The duplicate is not given its own proposed page.

**Privilege and third parties.** Closed phrases flag `possible_privilege`. Experiment 08 entity types, and a separate closed phrase list, flag `possible_third_party_personal_data`. Both mean a person should look. `exemption_applied` stays false. An identifier is not proof that it relates to another individual. Paragraph 16(3) is not scored.

**Index.** Proposed pages are the in-scope, read, in-period, non-duplicate items that are not flagged and do not carry an injection phrase. Order is document date, then item id. Page numbers start at 1. Flagged items sit on `held_for_review` with no page until a person includes them.

**Prompt injection.** Item text is untrusted. Phrases in the body, in an HTML comment, after a form feed, after three or more blank lines, or split by zero-width characters are recorded. `followed` is false. An item that carries one is not eligible for the approved list. Experiment 12's own phrase list is merged for items that were passed to it.

**Human steps, outside `build_pack()`.** `record_export_approval` accepts only the role "Evidence pack approver", and only with a name the caller passes in that call. The approved ids must each be eligible. A held item may be included only with the decision `include_after_review`. A checksum mismatch, an unread file, an out-of-scope item, a duplicate, an injection hit, or a date outside the period cannot be included. Stale sources or an intake date older than Experiment 12's 90-day window must be acknowledged. The acknowledgement does not clear the flag. `produce_export` then returns an index of those ids, in the order the approver passed, with no bodies. `send_external`, `disclose_to_requester`, `write_production_record`, `apply_exemption`, and `release_redacted` raise `PackForbidden`. The skills say the agent must not call the recording or export functions.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08 and 12 must sit beside this folder, which they do in this repository.

```bash
cd experiments/18-evidence-pack-builder
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/pack.py --input examples/sample_request.json --as-of 2026-10-28 \
  --pack-type sar_bundle --scopes case_file,correspondence \
  --search-from 2026-01-01 --search-to 2026-10-28
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score and it is not a live recall rate. A live Microsoft Foundry run has not been done.

A request that is not marked synthetic is refused. The exit code is 0 when a draft is produced, including when items are out of scope, held, or carrying an injection phrase. Those are findings, not a failed run, and they are not an approval.

## Limitations

- **Text only.** PDF, images, and scans are not read. Experiment 12 records the same gap. `not_read` is not a clean result.
- **A file over 20,000 characters is not scanned.** An instruction in that file is not detected. The cap is Experiment 12's, so this draft does not silently drop the end of a file and still claim it was read.
- **The starter does not search Microsoft 365.** The caller pastes the items. A scope is a check on that paste, not a Graph or SharePoint query. Items that were never pasted are invisible, which is a gap in the pack, not evidence that they do not exist.
- **Article 15(1A) is not implemented as a test.** The article, as read on 28 October 2026, entitles the data subject only to what the controller is able to provide based on a reasonable and proportionate search. This code does not decide that the caller's dates meet that test.
- **Exemptions are not applied.** A phrase such as "solicitor's advice" is not a finding that a claim to legal professional privilege could be maintained. A UK identifier is not a finding that paragraph 16 applies, or that disclosure would be reasonable. The ICO's right-of-access guidance says an exemption is considered case by case and is not applied in a blanket way. This draft does not take that decision.
- **Experiment 08's misses are inherited.** Names, email addresses, telephone numbers, an unlabelled continuous NHS number, and the other gaps in that experiment's README are not flagged as identifiers. The pack draft does not repeat the source text. It also does not claim the text was cleaned. The US spelling "neighbor" is not on the third-party phrase list.
- **Over-flagging is expected.** The data subject's own National Insurance number raises `possible_third_party_personal_data`, because the code cannot tell whose identifier it is. A person decides.
- **The 90-day window is not a retention rule and not a statutory response period.** It is Experiment 12's stale flag, and the same window on this experiment's source pin of 28 October 2026. UK GDPR Article 15, as read that day, does not state a 90-day period. Article 12 was not opened for this starter, so no response deadline is encoded.
- **Ombudsman rules were not opened.** The Financial Ombudsman Service and Housing Ombudsman pack types are labels. Nothing is sent to either body. Their evidence requirements are unverified here.
- **Titles and source labels are stored as supplied.** Do not put an identifier in them. The body is not stored. The title is.
- **Recording an approval is not a send.** The record and export functions exist so a test can show the role check. They are not tools of the agent. `send_external` still raises after both have been called. The export index does not contain the documents.
- **The smoke test is not a model score.**

This is not legal advice, a DPIA, or a statement that a deployment is compliant. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own. Schedule 2 paragraph 17 (the reasonableness assumption for certain health, social work, and education workers) was seen in the schedule and is not applied.

## Two Copilot Studio harnesses

Both call `build_pack()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness approves the list, produces the export, writes a record, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The user pastes a request and types the scopes and the search period, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the draft explained. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, retrieved 28 October 2026, says agents and workflows on that harness use Copilot Credits. Prices were not copied. The overview did not mark the harness itself as preview.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The intake this experiment calls: [../12-document-intake/](../12-document-intake/).
- The redaction gateway that intake calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/18-evidence-pack-builder/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── catalogue.py
│   ├── injection.py
│   └── pack.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 28 October 2026

- [UK GDPR Article 15](https://www.legislation.gov.uk/eur/2016/679/article/15) (legislation.gov.uk). Article 15(1), 15(1A), 15(3), and 15(4) were read. Article 15(1A) and the words added to Article 15(3) are marked as inserted by the Data (Use and Access) Act 2025, retrospective to 1 January 2024. Article 15(1)(ea) and the substituted wording of Article 15(1)(f) are also on that page. This starter does not restate a pre-amendment text.
- [Data Protection Act 2018, Schedule 2, paragraph 16](https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/16), including sub-paragraphs (1) to (4).
- [Data Protection Act 2018, Schedule 2, paragraph 18](https://www.legislation.gov.uk/ukpga/2018/12/schedule/2) defines the listed UK GDPR provisions for Part 4, including Article 15(1) to (3).
- [Data Protection Act 2018, Schedule 2, paragraph 19](https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/19).
- [ICO, What exemptions are relevant for SARs?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/right-of-access/what-exemptions-are-relevant-for-sars/) The page's latest-update line says 8 December 2025.
- [ICO, When can an exemption apply to information about other people in a SAR?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/right-of-access/when-can-an-exemption-apply-to-information-about-other-people-in-a-sar/)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- Experiment 12 and Experiment 08, which this code calls and does not re-derive. Their sources are listed in those READMEs.

Paragraph 5 of Schedule 2 (information required to be disclosed by law, and disclosure in connection with legal proceedings) was visible on the schedule. It is a different provision from paragraph 19. It is not encoded. Paragraph 17 was seen and is not applied. Article 12 was not opened.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
