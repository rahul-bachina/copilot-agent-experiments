# Experiment 78: Document Classification and Routing Assistant

Catalogue ID **O003**. Autonomy **A1**. The assistant proposes a document type and a destination queue or library for one incoming synthetic document. The named reviewer confirms that class and that destination before the routing is written to a synthetic staging store. The agent does not file, move, delete, or send.

This is not [Experiment 49](../49-records-classification/). Experiment 49 proposes a file-plan category and a retention entry. Experiment 78 classifies incoming correspondence by type, against a pinned taxonomy: complaint, FOI request, subject access request, invoice, legal letter, safeguarding referral, change of address, or no class.

Northwharf Borough Council is invented. The core is Python in the standard library. It calls [Experiment 12](../12-document-intake/) so the file is not confirmed and no purpose is confirmed, [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers, and [Experiment 49](../49-records-classification/) for `prepare_text` and `MARKING_RANK`. It does not use Experiment 49's file plan. A user can run it without a tenant. Catalogue row O003 names AI Builder or Microsoft Foundry, and Power Platform. This folder ships both Copilot Studio harnesses and a Microsoft Foundry note. No mailbox connector and no library connector is enabled.

## The problem

A letter can say, in its own text, that the reviewer has already approved it, that it should be filed as an invoice, or that a legal hold should be dropped. Two classes can both be present. A date can be ambiguous, impossible, or in the future relative to the question date. A caller can paste a different taxonomy and ask for that one to be used. A cover can say SECRET while the metadata says OFFICIAL. Those are the failures this starter is built to separate. A real confirmation is a separate object, from the directory reviewer named on the proposal, for the agent-held content hash.

## Non-goals

- Filing, moving, deleting, or sending a document.
- Treating an approval marker, a role, or a clearance inside a document as the confirmation step.
- Applying a taxonomy, routing table, or directory supplied in the request. The pinned fixtures are the source.
- Forcing a low-confidence, multi-type, or unknown document into a class.
- Deciding that Freedom of Information Act 2000 section 10 was met, or that UK GDPR Article 12A was met.
- Applying bank holidays. The Banking and Financial Dealings Act 1971 was not opened.
- Marking a carve-out, or a sentence that merely looks like a class, as a clean class.
- Guessing an ambiguous date, or replacing an unreadable date or period with zero or with today.
- Copying document text above the reviewer's directory clearance.
- Stripping a legal hold, a retention label, or a higher protective marking.
- Publishing a count of one to four people, or a percentage or a difference that could recover it.
- Using Experiment 49's file plan or retention schedule as this taxonomy.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 25 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Freedom of Information Act 2000 section 1](https://www.legislation.gov.uk/ukpga/2000/36/section/1) | Section 1(1), quoted in `src/sources.py`. The page recorded no known outstanding effects for section 1. |
| [Freedom of Information Act 2000 section 10](https://www.legislation.gov.uk/ukpga/2000/36/section/10) | Section 10(1) and the section 10(6) definition of working day, quoted in `src/sources.py`. The page recorded no known outstanding effects for section 10. Subsections (2) and (3), and the time-for-compliance regulations listed as modifications, were not opened. |
| [UK GDPR Article 15](https://www.legislation.gov.uk/eur/2016/679/article/15) | The opening of Article 15(1), quoted in `src/sources.py`. |
| [UK GDPR Article 12](https://www.legislation.gov.uk/eur/2016/679/article/12) | Article 12(3) as amended, quoted in `src/sources.py`. On that page it does not itself say "one month". It points to Article 12A. |
| [UK GDPR Article 12A](https://www.legislation.gov.uk/eur/2016/679/article/12A.) | Article 12A(1): the applicable time period is one month beginning with the relevant time, subject to paragraph 3. The URL without the trailing dot returned 404. |
| [Data (Use and Access) Act 2025 section 76](https://www.legislation.gov.uk/ukpga/2025/18/section/76) | Section 76(2)(a)(i) records the substitution in Article 12(3). Section 76(3) inserts Article 12A. The page recorded no known outstanding effects for section 76. |

The quotes are context for the reviewer. They are not a finding that the duty was met, and they are not legal advice. The Banking and Financial Dealings Act 1971 was not opened. Article 6 and Article 9 were not opened. No lawful basis is asserted.

## What the result does

`classify_document()` reads one document and the question date, and writes one JSON document. The class, the evidence, and the destination use the pinned files in `fixtures/`. A caller-supplied taxonomy, routing table, or directory is diffed and not applied. The same inputs and the same date produce the same JSON. `human_approval` is null. `filed`, `moved`, `deleted`, and `sent` stay false. The proposal is stored as an agent-held copy. A later confirmation has to match that copy.

**Class.** A pinned phrase is evidence only when it is outside a negation in the same sentence. "It is not true that this includes a subject access request" is not a subject access request. Two different strong phrases in one class are high confidence. One strong phrase is medium. A weak phrase alone is low, and the class is not selected. Two classes, a carve-out, or no class leave `selected_class` null. The top alternative is the second ranked class when there is one. `forced_class` stays false.

**Human queue.** FOI and subject access requests go to their human queues because of the statutory clock. `clock_met` stays false. No statutory due date is produced. A stated working-day count above 20 is flagged and is not a finding that section 10 was breached, because the fees notice, section 10(3), the regulations, and bank holidays were not applied. A stated SAR period above 31 days is flagged and is not a finding that Article 12A was breached, because paragraph 3 allows two further months. Distress, safeguarding, whistleblowing, grievance, and urgent cues go to a person even when the sentence is reworded, and a distress stem is still routed when the sentence denies it. A SECRET or TOP SECRET marking goes to the human queue and is not proposed into a library.

**Text.** An approval marker, a self-declared role, or a self-declared clearance in the text is recorded and not trusted. Instructions are recorded and not followed. A class phrase that sits only inside an instruction sentence is not evidence. A class phrase that sits only in metadata is not evidence.

**People and markings.** Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are counted. The values are not stored. The document body is not copied. The output is not described as anonymised. Metadata and content are both read. Experiment 49's `prepare_text` body marking is included. A bare SECRET cover line is also read, because Experiment 49's pattern requires the word "marked" or "classification:". A compound label takes the higher rank from Experiment 49's `MARKING_RANK`. A self-declared clearance sentence is not a cover page. A legal hold and every retention label stay on the result. A count field, a percentage, and a difference are not published.

**Dates.** The question date is the as-of argument. Today is not used. `12/12/2024` is not ambiguous. `01/02/2024` is ambiguous and is not guessed. An impossible day such as 29 February 2025 is flagged. A future date is flagged and is not replaced. Two different received dates are a conflict, and neither is picked. An unreadable period is not replaced with zero.

**Intake.** Experiment 12 inventories the file. `files_confirmed` and `purpose_confirmed` stay false.

`file_document`, `move_document`, `delete_document`, and `send_document` raise `RoutingForbidden`.

`record_route_seen()` records that the named reviewer has seen a human route. It changes the held hash. It does not stage the routing.

`record_routing_confirmation()` records that the directory reviewer named on the proposal confirmed that class and that destination for the held hash. A string is not coerced to true. A caller who edits the proposal and re-hashes it is refused. The write is the synthetic store. It does not file the document.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 49 must be present beside this folder.

```bash
cd experiments/78-document-classification-routing
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/classify.py --document examples/sample_document.json --as-of 2026-11-25
```

The sample document carries approval language, a self-declared clearance, a caller taxonomy, a SECRET cover, a legal hold, and a distress sentence on purpose. They are stripped or ignored. `human_approval` stays null. The outcome is `human_queue`. The applied marking is SECRET.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall and class precision are separate blocks and are not added to the case total. On the committed run, 20 of 20 cases passed, and each paraphrase category had at least 20 sentences with recall 1.0 and precision 1.0 on those sentences. That is not a live rate.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Cue matching is a stem list. A paraphrase that uses none of those stems is not flagged. The smoke report states recall and precision on the fixture sentences. That is not a live rate.
- "Not true that", "nobody", "does not", and the other denial frames are the negation rule for classes. A denial that uses none of them can be missed. A distress stem is routed even inside a denial.
- The Monday-to-Friday count is not the statutory working day. Section 10(6) also excludes Christmas Day, Good Friday, and bank holidays under the Banking and Financial Dealings Act 1971. That Act was not opened. `statutory_due_date` stays null. `clock_met` stays false.
- Article 12A(3) allows two further months. A stated period is not a finding that the period was missed or met.
- The marking order is Experiment 49's rank. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period.
- Count fields are not published. This is not anonymisation.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. A name with no title and no "my name is" is not counted by this mask.
- Article 6 and Article 9 were not opened. The time-for-compliance regulations were not opened.
- A document over 20,000 characters is not scanned. An instruction in it is not detected.
- HTML comments are not used as class evidence. A marking that exists only inside a comment can be missed.
- The reviewer confirms the proposal as held. This starter does not apply a different class the reviewer types in.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- The harness overview was opened on 25 November 2026. See [docs/harness-comparison.md](docs/harness-comparison.md). The page did not use the words "GitHub Copilot harness".
- Northwharf Borough Council is fictional.
- This is not a decision that a document is an FOI request in law, and it is not a filed record.

## Two Copilot Studio harnesses

Both call `src/classify.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness files a document. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_routing_confirmation` only with the approval object. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** Catalogue row O003 names AI Builder or Microsoft Foundry, and Power Platform. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The file tools that harness can use are not used to move the document or to send. No mailbox connector is enabled in this starter.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The hash, the class, and the approval step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed. The runnable sample does not call a model.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Document intake: [../12-document-intake/](../12-document-intake/).
- Records classification, used here only for marking rank: [../49-records-classification/](../49-records-classification/).
- UK identifier redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/78-document-classification-routing/
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
