# Experiment 73: Control Testing Assistant

Catalogue ID **L009**. Autonomy **A1**. The assistant prepares a test plan, a seeded sample, and a draft working paper. The named tester approves that exact content before a copy is written to a synthetic staging store. The tester validates the evidence and decides the result. The agent does not pass or fail a control, close a finding, or send anything.

A tester points at one control in the pinned synthetic library, a period, and a sample seed. The population is synthetic evidence: purchase approvals, reconciliations, an access review, and change tickets, with dates and approver references. Ashcombe Borough Council is invented.

The core is Python in the standard library. It calls [Experiment 12](../12-document-intake/) so the files are not confirmed and no purpose is confirmed, [Experiment 69](../69-policy-control-mapping/) when a control has a policy clause, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. A user can run it without a tenant. Catalogue row L009 names the GitHub Copilot harness and Power Platform. This folder ships both Copilot Studio harnesses. No Power Platform connector is enabled.

## The problem

Evidence can say, in its own text, that the control passed, that the tester has already approved it, or that the reader should ignore the test steps. A date can sit outside the period, be unreadable, or be earlier than the date the item was prepared. The preparer can be the approver. A caller can paste a different control library and ask for that one to be used. Those are the failures this starter is built to separate. A real approval is a separate object, from the directory tester named on the draft, for that exact content hash.

## Non-goals

- Passing or failing a control.
- Closing a finding.
- Sending the working paper, or writing it to a GRC system.
- Treating an approval marker, a role, or a clearance inside evidence text as the approval step.
- Applying a control library, population, directory, or criteria object supplied in the request. The pinned fixtures are the source.
- Marking a carve-out, or a sentence that merely looks acceptable, as acceptable.
- Applying a biased or leading criterion.
- Guessing an ambiguous date, or replacing an unreadable date, seed, or amount with zero or with today.
- Copying evidence text above the tester's directory clearance.
- Stripping a legal hold or a retention label.
- Publishing a count of one to four people.
- Deciding that UK Corporate Governance Code 2024 Provision 29 was met, or that FCA SYSC 4.1.1R was met.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 23 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| Company-hosted PDF of the UK Corporate Governance Code, January 2024, at `https://corporate.unitedutilities.com/globalassets/documents/corporate-documents/uk_corporate_governance_code_2024_.pdf` | Provision 29, quoted in `src/sources.py`. The PDF is marked as copyright The Financial Reporting Council Limited 2024. A footnote marker after the last word was not copied into the quote. |
| [FRC library page for the Code](https://www.frc.org.uk/library/standards-codes-policy/corporate-governance/uk-corporate-governance-code/) | The page says the 2024 Code has applied since 1 January 2025, with Provision 29 becoming applicable from 1 January 2026. The full provision text was not on that HTML page. The FRC media PDF was not opened. A byte-for-byte match to the FRC file is unverified. |
| [FCA Handbook SYSC 4](https://handbook.fca.org.uk/handbook/sysc4) | The page said it was showing the chapter as of 23/11/2026, last updated on 26/06/2026. The application table lists General requirements as SYSC 4.1.1R. Paragraph (1) under General requirements is quoted in `src/sources.py`. The converted page did not print the characters SYSC 4.1.1R on the line immediately above that sentence. |

Neither text was opened on legislation.gov.uk. Their currency on legislation.gov.uk is unverified. The quotes are context for the tester. They are not a finding that the provision or the rule was met.

## What the result does

`prepare_test()` reads one request and the question date, and writes one JSON document. The plan, the checks, and the sample use the pinned files in `fixtures/`. A caller-supplied library, population, directory, or criteria object is diffed and not applied. The same inputs and the same date produce the same JSON. `human_approval` is null. `control_passed` and `control_failed` stay null. `finding_closed` and `sent` stay false.

**Sample.** Evidence ids for the control are ordered. The size is the larger of the pinned minimum and the integer square root of the population, rounded up, and it is not larger than the population. The method is seeded systematic sampling. The start index is the seed modulo the population. The step is integer division of the population by the size. An unreadable seed or minimum is flagged and is not replaced with zero. The sample is not a conclusion that the control operated. ISA (UK) 530 was not opened.

**Checks.** Each evidence item for that control is checked, not only the sample. Dates are compared with the period on the request, not with today. An approver must be on the pinned directory and hold an approval role from the pinned criteria. The preparer and the approver must not be the same reference. An approver who reports to the preparer is a segregation exception. Those two rules are starter rules, not a statute. A hash that does not match the recorded hash, or an `altered` flag that is the boolean true, is an altered item. A string is not coerced to true. Missing required fields, unreadable dates, and ambiguous slash dates are exceptions. Exceptions cite the evidence id.

**Text.** An approval marker, a self-declared role, or a self-declared clearance in the text is recorded and not trusted. "It is not true that …" is not an inclusion. A distress, grievance, or safeguarding stem is routed even when the sentence denies it. The cue text is not copied. A carve-out after an independence sentence is not marked acceptable. A biased criterion in a caller object is flagged and not applied.

**People and markings.** Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are counted. The values are not stored. The body is not copied. The output is not described as anonymised. A count of people below 5 is not published. Five is this starter's threshold. A statistics authority page was not opened for it. Metadata and content are both read. A SECRET cover is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**Intake and mapping.** Experiment 12 inventories up to 12 evidence files. `files_confirmed` and `purpose_confirmed` stay false. Checks still run on the whole population when intake is capped. Experiment 69 maps a policy clause when the control has one. That mapping is not a test result. `control_met` from that call is ignored.

`pass_control`, `fail_control`, `close_finding`, and `send` raise `TestingForbidden`.

`record_tester_approval()` records that the directory tester named on the draft approved one item. The content hash has to match the draft now in the result. A string is not coerced to true. The record does not pass the control. `record_tester_result()` stores that tester's own words on the staged row and does not interpret them.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 69 must be present beside this folder.

```bash
cd experiments/73-control-testing-assistant
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/testing.py --request examples/sample_request.json --as-of 2026-11-14
```

The sample request carries approval language, a self-declared role, a self-declared clearance, and a caller library on purpose. They are stripped or ignored. `human_approval` stays null. The population for that control includes a distress sentence, so the outcome is `route_to_human`.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total. On the committed run, 20 of 20 cases passed, and each paraphrase category had at least 20 sentences with recall 1.0 and precision 1.0 on those sentences. That is not a live rate.

The exit code is 0 when a result is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Cue matching is a stem list. A paraphrase that uses none of those stems is not flagged. The smoke report states recall and precision on the fixture sentences. That is not a live rate.
- "Not true that", "nobody", "does not", and the other denial frames are the negation rule. A denial that uses none of them can be missed. A distress stem is routed even inside a denial.
- The sample size and the segregation rule are starter rules. ISA (UK) 530 was not opened. A manager approving a colleague's work is not, by itself, an exception in this starter. An approver who reports to the preparer is.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A review-due date on the question date is not relied on. That is this starter's rule. It is not a statutory period. Experiment 12's window is that experiment's rule.
- Counts of people below 5 are not published. Five is this starter's threshold. A statistics authority page was not opened.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- Provision 29 was not read from the FRC media file. SYSC 4.1.1R was not opened on legislation.gov.uk. Both are unverified against legislation.gov.uk.
- Experiment 12 inventories at most 12 files. A larger population is still checked. The intake flag says when the batch was capped.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- The harness overview was not re-opened for this experiment. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Ashcombe Borough Council is fictional. Contact addresses on ashcombe.example.gov.uk are placeholders.
- This is not a finding that a control operated, and it is not a board declaration.

## Two Copilot Studio harnesses

Both call `src/testing.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness passes a control. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_tester_approval` only with the approval object. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** Catalogue row L009 names this harness first, with Power Platform. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The file tools that harness can use are not used to edit evidence or to send. No Power Platform connector is enabled in this starter.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The hashes, the exceptions, and the approval step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Document intake: [../12-document-intake/](../12-document-intake/).
- Policy control mapping: [../69-policy-control-mapping/](../69-policy-control-mapping/).

## Project structure

```
experiments/73-control-testing-assistant/
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
