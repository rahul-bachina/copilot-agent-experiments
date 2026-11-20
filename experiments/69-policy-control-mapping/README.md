# Experiment 69: Policy Control Mapping

Catalogue ID **L003**. Autonomy **A0**. The assistant proposes mappings from policy statements to internal controls. The control owner approves each mapping. The agent does not mark a control as met, close a gap, edit a policy, or write to a GRC system.

A control owner points at a synthetic policy set and the pinned synthetic control library. Each proposed mapping keeps the exact quoted sentence, the clause reference, the control id, a rationale, and a confidence band (`high`, `medium`, or `low`). A control with no supporting sentence is `no evidence found`. A sentence that matches no control is listed as unmapped. Two policies that do not say the same thing are both quoted. Neither is chosen. Ashcombe Borough Council is invented.

The core is Python in the standard library. It calls [Experiment 12](../12-document-intake/) so the files are not confirmed and no purpose is confirmed, [Experiment 36](../36-cross-source-validation/) when two policies state different obligation tokens, [Experiment 03](../03-agent-inventory-atrs-assurance/) for an injection check and a DUAA screen that does not clear this agent, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. A user can run it without a tenant. Catalogue row L003 names the GitHub Copilot harness and Microsoft 365 first. This folder still ships both Copilot Studio harnesses. No SharePoint connector is enabled.

## The problem

A policy can say, in its own text, that the control owner has approved it and that a control should be marked met. It can say "should" where the control expects "must". It can add "except where…" after an otherwise clear obligation. It can require an incident report in one document and forbid that report in another. Those are the failures this starter is built to separate. A real approval is a separate object, from the directory control owner, for that exact content hash and that exact proposal hash.

## Non-goals

- Marking a control as met, or deciding that a CAF objective is achieved.
- Closing a gap.
- Editing a policy, including by a file tool the harness would otherwise allow.
- Writing to a GRC system, SharePoint, or any other store.
- Treating approval text inside a policy as approval.
- Applying a control library, guide, or register supplied in the request. The pinned fixture is the library.
- Applying a biased or leading criterion.
- Guessing a sentence that is not in the text.
- Reproducing ISO/IEC 27001 control text. Identifiers only.
- Copying NCSC CAF indicator wording. The PDF was not opened.
- Stripping a legal hold or a retention label.
- Trusting a self-declared role, guest status, or clearance in a policy.
- Coercing an unreadable date, clause reference, or strength to zero or to a default.
- Choosing which of two conflicting policies is right.
- Publishing a count of one to four named people.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 20 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [NCSC Cyber Assessment Framework collection](https://www.ncsc.gov.uk/collection/cyber-assessment-framework) | The page stated Version 4.0, Published 18 April 2024, and Reviewed 30 October 2026. It also showed a blog title dated 6 August 2025, "Cyber Assessment Framework v4.0 released". Those dates are not reconciled. The four objective titles on the HTML page are optional context on a control. The PDF linked from the page was not opened. Principle pages were not opened. Indicator wording is unverified and is not copied. Achievement is not decided. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox. The page says agents on that harness use Copilot Credits. It states no price. Pricing pages were not opened. It does not use the words GitHub Copilot harness. It does not say that this harness is not the GitHub Copilot service. |

ISO/IEC 27001 was not opened. Annex identifiers in the fixture were not checked against a licensed copy. Control text from that standard is not in this repository.

## What the result does

`map_controls()` reads one request, the caller library if one was passed, one directory, and one question date, and writes one JSON document. Mappings use the pinned library in `fixtures/library.json`, not the caller copy. The same inputs and the same date produce the same JSON. `human_approval` is null. `control_met`, `gap_closed`, `policy_edited`, and `grc_written` stay false.

**Role and clearance.** The directory supplies both. "My role is Control owner" and "my clearance is TOP SECRET" are recorded and ignored. A guest on the directory stays a guest and does not receive quotes. An unreadable clearance is not replaced with OFFICIAL. A caller who is not in the directory does not receive quotes.

**Quotes.** A quote is the policy sentence, or the exact words `no evidence found`. It is not a paraphrase. Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are masked in the quote. The result says which categories were masked. It does not say the quote was anonymised. A count of named people below 5 is not published. Five is this starter's threshold. A statistics authority page was not opened for it. The policy body is not copied.

**Strength.** `must` or `shall` is not `should`. `should` is a medium band when the control expects `must`. `may` is a low band. `except`, `unless`, and the other carve-out stems weaken the sentence: the band is low, and the sentence is not an unqualified mapping. "It is not true that the policy includes …" is not an inclusion.

**Contradictions.** A `must` sentence and a `must not` sentence for the same control are both quoted. Experiment 36 compares the obligation tokens. This starter does not choose a source. The control is not given a mapping and is not called a gap.

**Library.** A caller-supplied library is diffed against the pinned file. Differences are flagged and not applied. An expected strength outside the closed list is not coerced to `must`. A biased or leading criterion is flagged for a person and is not applied.

**People.** A distress, vulnerability, safeguarding, grievance, or disclosure cue, including a paraphrase, is a route to a person. The cue is not copied. The comparison is not a routine proposal.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**Dates.** The date on the question is the date used. Today is not used. A review-due date on the question date is stale. That is this starter's rule, not a statute. A policy whose effective date is after the question date is not yet in force and is not used. An unreadable date is flagged and is not replaced.

**Intake and assurance.** Experiment 12 inventories the text. `files_confirmed` and `purpose_confirmed` stay false. Experiment 03 records injection findings and a DUAA screen. `screen_clears_agent` stays false. No ATRS record is produced.

`mark_control_met`, `close_gap`, `edit_policy`, and `write_grc` raise `MappingForbidden`.

`record_owner_approval()` records that the directory control owner approved one item. The content hash and the proposal hash have to match the text now in the result. A string is not coerced to true. The record does not mark a control as met.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 03, 08, 12, and 36 must be present beside this folder.

```bash
cd experiments/69-policy-control-mapping
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/map_controls.py --request examples/sample_request.json --library fixtures/library.json --directory fixtures/directory.json --as-of 2026-11-14
```

The sample request carries approval language, a self-declared role, and a self-declared clearance on purpose. They are stripped or ignored. `human_approval` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total. On the committed run, 20 of 20 cases passed, and each paraphrase category was at least 20 sentences with recall 1.0 on those sentences. That is not a live rate.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Signal matching is the pinned library's stem list. A wording that uses none of those stems is unmapped or `no evidence found`. It is not reclassified by guesswork.
- Cue, qualification, and instruction matching is a stem list. A paraphrase that uses none of the stems is not flagged. The smoke report states recall on the fixture sentences. That is not a live rate.
- "Not true that", "does not include", "must not", and the other denial frames are the negation rule. A denial that uses none of them can be missed.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period. Experiment 12's 90-day window is that experiment's rule.
- Counts of named people below 5 are not published. Five is this starter's threshold. A statistics authority page was not opened.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- The NCSC CAF PDF and the principle pages were not opened. Indicator wording is unverified. The page's published date and the blog title date were not reconciled. ISO/IEC 27001 was not opened. Annex identifiers were not checked against a licensed copy.
- Experiment 36 has no policy document kind. A contradiction pack uses `register_extract`. That is a label in Experiment 36's closed list, not a finding that the policy is a register extract.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- The harness overview states no price. This readme does not quote one. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional. Contact addresses on ashcombe.example.gov.uk are placeholders.
- This is not a finding that a control is met, and it is not an edit of a policy.

## Two Copilot Studio harnesses

Both call `src/map_controls.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness marks a control as met. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_owner_approval` only with the approval object. The overview opened on 20 November 2026 describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** Catalogue row L003 names this harness first, with Microsoft 365. The overview opened on 20 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and it says that harness uses Copilot Credits. It does not use the words GitHub Copilot harness. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The file tools that harness can use are not used to edit a policy. No SharePoint connector is enabled in this starter.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The quotes, the hashes, and the approval step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Document intake: [../12-document-intake/](../12-document-intake/).
- Cross-source validation: [../36-cross-source-validation/](../36-cross-source-validation/).
- Assurance patterns: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).

## Project structure

```
experiments/69-policy-control-mapping/
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
