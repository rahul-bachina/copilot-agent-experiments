# Experiment 12: Document Intake Agent

Catalogue ID **O001**. The document-intake foundation that later catalogue rows build on: KYC evidence (B004), claims document triage (B007), subject-access scoping (UK11), and evidence-bundle summary (UK09). Those agents are not implemented here and are not called.

A person drops one synthetic batch of text files. The agent returns a draft inventory: a hash of each file, a keyword class, a completeness preview, any prompt-injection phrase hidden in the text, whether a document date is inside the window, and a redaction proposal from [Experiment 08](../08-uk-pii-redaction-gateway/) (O005, the UK identifier PII gateway). It does not ship a second redactor.

**Autonomy A1.** The user confirms the file list and the permitted purpose. An intake reviewer then accepts, returns, or rejects the routing suggestion. The agent never confirms those steps itself. It never accepts a file into a queue, never approves or rejects the underlying matter, never writes a production record, and never sends anything.

Stack in the catalogue: Copilot Studio, Azure, and Power Platform. What you can run today is Python in the standard library, plus the Experiment 08 detectors. No Azure credentials and no network. Azure Document Intelligence is not called. See [docs/foundry.md](docs/foundry.md).

Samples are synthetic. National Insurance and NHS values are the non-allocatable fixtures documented in Experiment 08. No real person, firm, or case is in the batch.

## The problem

Specialist reviews start with the same chore: what arrived, is it the file the user meant, what may it be used for, and did anyone strip UK identifiers before a model sees the text. Doing that inside each later agent duplicates the checks and makes it easy for a sentence inside a PDF, or an HTML comment, to set the purpose or to mark the file accepted.

This starter is only that front door. The specialist decision stays in the later catalogue row, with its own human checkpoint.

## Who it helps

**The person uploading the files.** They see the file ids and hashes, a suggested class, and the gaps in a checklist, and they confirm the purpose from a closed list. The document cannot confirm itself.

**An intake reviewer.** They see injection signals, stale or missing dates, checksum failures, and unread file types before they accept a routing suggestion. Accepting the suggestion still does not write a queue.

**A later build of B004, B007, UK11, or UK09.** Those rows can take a confirmed intake draft as input. This experiment does not hand the draft to them.

**A privacy reviewer.** UK identifier spans are proposed by Experiment 08. This agent does not release the redacted text and does not describe it as anonymised. Names, email addresses, and telephone numbers are still in the source text, which this draft does not copy out.

## Non-goals

- Approving or rejecting a KYC file, a claim, a subject-access disclosure, or an evidence finding.
- Deciding that a document is authentic, sufficient, or in date. A keyword and a date comparison are not those decisions.
- Accepting a file into a queue, a case, or a work tray.
- Writing a production record, including Dataverse, SharePoint, a case system, or a mailbox.
- Sending email or any other external message, including to a customer, a counterparty, the ICO, or the FCA.
- Releasing redacted text, storing a reversible token map, or claiming the text is anonymised.
- Re-implementing Experiment 08. This experiment calls `propose` and does not copy the detectors.
- OCR, or a call to Azure Document Intelligence or Azure Content Understanding.
- Reading a mailbox, a case store, or a register to check that a file is genuine.
- Setting the permitted purpose, or `files_confirmed`, from a sentence inside a document.
- Autonomy A3. There is no path on which the agent acts without the two human steps above.

## What the intake does

`src/intake.py` reads one JSON batch and writes one JSON document. The same batch and the same as-of date produce the same JSON. `files_confirmed` and `purpose_confirmed` are false. `reviewer_decision` is null. `actions_taken` is empty.

**Files.** Each file needs an id, a filename, a media type, and text. This starter reads `text/plain` only. Anything else is listed as `not_read` and is not classified and not sent to the gateway. If that file's JSON still contains a text body under the size cap, the body is scanned for instructions. It is still not treated as a reading of the file. An empty file and a file over 20,000 characters are not scanned. A supplied SHA-256 that does not match the text is a checksum failure. A repeated hash is marked as a duplicate of the earlier file id.

**Class.** A closed keyword list suggests a class, or `unclassified`, or `unresolved` when two classes tie. The suggestion is not a document-type decision.

**Purpose.** The closed list is `kyc_evidence` (B004), `claims_fnol` (B007), `sar_bundle` (UK11), `evidence_bundle` (UK09), and `general_records` (no downstream row). `intake()` never sets the purpose. A `requested_purpose` on the batch can preview the checklist. That preview is not confirmation. A purpose named inside the file text is an injection signal, not a selection.

**Checklist.** For a known purpose, the preview looks for closed-list phrases and classes. It does not extract a value, and it does not decide that the pack is sufficient. Gaps stay listed.

**PII.** Each `text/plain` file that is within the size cap is passed to Experiment 08 `propose()`, with caller `exp-12-document-intake`. The intake JSON keeps the entity types, the hash, and the gateway flags. It does not keep the source text, the redacted text, or the raw identifiers. `output_is_anonymised` and `agent_may_release` stay false. Model suggestions are not applied. `reversible` is not requested.

**Stale data.** A document date more than `stale_after_days` before the as-of date is stale. The default window is 90 days. A date exactly 90 days earlier is not stale. A future date, a missing date, and an unparseable date are not treated as current. The purpose catalogue is pinned on 27 October 2026. The same window applies to that pin. A sentence in the file that says the document is current does not clear the flag. Passing an earlier `rules_as_of` warns that Experiment 08's rules may be stale. Detection still uses the pinned rules.

**Prompt injection.** The file text is untrusted. Phrases in the body, in an HTML comment, after a form feed, after three or more blank lines, or split by zero-width characters are recorded. `followed` is false. The phrases do not confirm files, set the purpose, release text, or send anything.

**Human steps, outside `intake()`.** `record_user_confirmation` accepts only the role "Intake user", and only when the file ids match the draft in order and no checksum has failed. `record_reviewer_decision` accepts only the role "Intake reviewer", and only after that confirmation. Neither function writes a queue. `commit_to_queue`, `send_external`, `write_production_record`, `approve_underlying_matter`, `reject_underlying_matter`, and `release_redacted` raise `IntakeForbidden`. The skills say the agent must not call the recording functions.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must sit beside this folder, which it does in this repository.

```bash
cd experiments/12-document-intake
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/intake.py --input examples/sample_batch.json --as-of 2026-10-27
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score and it is not a live recall rate. A live Microsoft Foundry run has not been done.

A batch that is not marked synthetic is refused. The exit code is 0 when a draft is produced, including when files are stale, unreadable, or carrying an injection phrase. Those are findings, not a failed run, and they are not an acceptance.

## Limitations

- **Text only.** PDF, images, and scans are not read. The [Document Intelligence overview](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0), retrieved 27 October 2026, describes Read and Layout models that extract text, and prebuilt models for bank statements, invoices, receipts, and identity documents. This starter does not call them. A file of another media type is `not_read`, which is a gap, not a clean bill of health.
- **A file over 20,000 characters is not scanned.** An instruction in that file is not detected. The cap is there so the draft does not silently drop the end of a file and still claim it was read.
- **Keywords misclassify.** "Sort code" suggests a bank statement even when the line is a fixture. Two single hits tie as `unresolved`. A real proof of address that does not use the listed words is `unclassified`.
- **The checklist is not sufficiency.** A phrase such as "policy number" can be present and still be the wrong policy. No value is extracted or checked against a system.
- **Experiment 08's misses are inherited.** Names, email addresses, telephone numbers, an unlabelled continuous NHS number, and the other gaps in that experiment's README are not redacted. The intake draft does not repeat the source text. It also does not claim the text was cleaned.
- **The 90-day window is not a retention rule.** It is a stale flag for this starter. No statute was encoded as a document-age limit.
- **The catalogue pin can go stale.** After the window, `catalogue_stale` is true and the reviewer function will not record `accept_routing` until the caller passes `acknowledge_stale`. That acknowledgement is a person's argument to the function. It still does not write a queue, and the agent is not given a tool that passes it.
- **Recording a decision is not an action.** The two record functions exist so a test can show the role check. They are not tools of the agent. `commit_to_queue` still raises after both have been called.
- **Downstream rows are names.** B004, B007, UK11, and UK09 are not in this repository as agents this code can call. A routing id is a label.
- **The smoke test is not a model score.**

This is not legal advice, a DPIA, or a statement that a deployment is compliant. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `intake()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness confirms files, accepts a routing suggestion, writes a record, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The user pastes a batch, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the draft explained. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft bills that harness in Copilot Credits. Prices were not copied. The harness overview, retrieved 27 October 2026, did not mark the harness itself as preview.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry, and the document services that were read and not called: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The redaction gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/12-document-intake/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── catalogue.py
│   ├── injection.py
│   └── intake.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 27 October 2026

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), page last updated 22 October 2026
- [Azure Document Intelligence in Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0), v4.0 (2024-11-30) marked GA on that page
- [Choose the right Azure AI tool for document processing](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/choosing-right-ai-tool), which marks API version `2026-06-01-preview` as public preview and says the article is based on the Content Understanding `2025-11-01` API
- Experiment 08's pinned identifier rules, which this code calls and does not re-derive. Those sources are listed in that experiment's README.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
