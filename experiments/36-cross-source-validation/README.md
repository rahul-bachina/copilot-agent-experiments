# Experiment 36: Cross-Source Validation Agent

Catalogue ID **B005**. Autonomy **A0**. The catalogue checkpoint is "Reviewer resolves every material discrepancy". The planning row records the stack as CS-GH + AZ. The task for this folder also names Microsoft Foundry. What you can run today is Python in the standard library. It does not call a model and it does not call the network.

A reviewer supplies one synthetic pack. The same fact can sit on a form, a contract, an invoice, and a register extract: a name, an address, a company number, an amount, a date, or a policy figure. The agent normalises each cited value with a fixed rule, then classifies the fact as a **match**, an **immaterial difference** (formatting or an abbreviation the rule collapses), or a **material discrepancy**. Every value carries a pinpoint: document, page, paragraph, and line. The reviewer resolves each material row. The agent does not choose which source is right, does not edit a record, and does not contact anyone.

Samples are synthetic. Northfen Supplies is fictional. Company number 88990011 and the other numbers in the fixtures were not looked up. They are not a statement that Companies House has or has not issued them. No real person and no real firm is in the pack.

## How this differs from Experiments 12, 08, and 33

**Experiment 12** inventories a batch of text files. It does not compare a field across files and it does not classify a difference. This experiment calls `intake()` so the date flag, the checksum, and the injection scan are the same ones. It does not call `record_user_confirmation` or `record_reviewer_decision`. `files_confirmed` and `purpose_confirmed` stay false. The purpose passed through is `general_records`, which Experiment 12 already lists. This folder does not add a purpose to that catalogue.

**Experiment 08** proposes redactions for UK identifiers. This experiment calls `propose()` on each field value. An unexpected identifier, including a labelled NHS number, is withheld and the value is not copied. A company number on a company-number field, and a postcode on a postcode field, are expected and are still compared. `output_is_anonymised` stays false. The prefix list and the six postcode shapes are imported from Experiment 08. They are not copied. The 2011 URI guide and the 2015 ILR annex were not re-opened on 5 November 2026.

**Experiment 33** checks that a sentence is a contiguous part of a cited line. This experiment calls `resolve_span` and the same whitespace-and-case fold. A field value that is not on the cited line is not used. This experiment does not write a case-bundle summary and does not decide an outcome.

## The problem

Regulated firms and public bodies often hold the same fact in more than one document. A difference can be a formatting choice, such as "Limited" and "Ltd", or it can be a different amount or a different date. UK GDPR Article 5(1)(d), opened on legislation.gov.uk on 5 November 2026, says personal data shall be accurate and, where necessary, kept up to date, and that every reasonable step must be taken to erase or rectify inaccurate data without delay. Data Protection Act 2018 section 205(1), opened the same day, says "inaccurate", in relation to personal data, means incorrect or misleading as to any matter of fact. This tool does not decide that a value is inaccurate, and it does not erase or rectify anything.

Companies House, opened on gov.uk the same day, says it registers company information and makes it available to the public. A document kind of `register_extract` is text the reviewer pasted. This starter does not query that register.

The ICO page "Principle (d): Accuracy" was requested on 5 November 2026 and returned HTTP 403. It was not opened and it is not quoted.

## Who it helps

**A reviewer in a regulated firm or a public body.** They see each fact, the class, and the pinpoint for every source. They resolve the material rows. The draft does not tell them which document to believe.

**A colleague preparing that list.** They can see which differences the rules treat as formatting, and which ones the rules will not collapse. Both quotes stay on the immaterial rows.

**A reviewer comparing this pattern with document intake or a case-bundle summary.** Intake does not compare fields. The case-bundle summariser does not classify a company number or an amount. This folder is the comparison.

## Non-goals

- Choosing which source is right. `agent_chose_source` stays false. `choose_source` always raises.
- Editing a record, a register, a contract, or a case system. `records_edited` stays false. `correct_value` stays null.
- Contacting a customer, a supplier, or anyone else. `parties_contacted` stays false.
- Querying Companies House or any other live register. `register_queried` stays false.
- Deciding that personal data is inaccurate under section 205, or erasing or rectifying it under Article 5(1)(d).
- Treating a match or an immaterial difference as a finding that the value is accurate.
- Confirming the intake files or the permitted purpose, or accepting the batch into a queue.
- Releasing or anonymising text. `output_is_anonymised` stays false.
- Calling Microsoft Foundry, or any model. The explanation sentences are fixed text for the class.
- Reading a PDF, an image, or a scan. The caller pastes text that is already split into pages, paragraphs, and lines.
- Autonomy A3. There is no path on which the agent resolves the discrepancy.

## What the comparison does

`src/compare.py` reads one JSON pack and writes one JSON document. The same pack, the same as-of date, and the same window produce the same JSON. The label is **DRAFT FOR THE REVIEWER. NOT A CORRECTION.**

**Field types.** The closed list is `name`, `address`, `date`, `currency`, `postcode`, `company_number`, `figure`, and `reference`. Document kinds are `form`, `contract`, `invoice`, and `register_extract`. A pack that is not marked synthetic is refused. The refusal does not echo the body.

**Normaliser.** Case and whitespace alone are a match. A difference that the rule collapses, and that still looks different on the page, is immaterial. Anything else is material.

| Rule | What it collapses | What stays material |
|---|---|---|
| Name | Case, whitespace, `&` / `and`, `Ltd` / `Limited` and the other legal-form phrases in the code, a leading title only when the next token is one letter | A different word. "Dr Martens Ltd" is not "Martens Ltd". |
| Address | Case, whitespace, and a street abbreviation only when it is the last word | A different last word. A town after the street word is not removed. |
| Date | ISO, UK day-first numbers, and a month name, to one calendar day | A different day. `01/02/2026` is 1 February 2026, not 2 January. A two-digit year is not accepted. |
| Currency | `GBP`, the pound sign, thousands separators, and trailing zeros, to pence | A different number of pence. Another currency code is not converted. |
| Postcode | Case and spacing, using Experiment 08's six shapes | A different inward or outward code. `GIR 0AA` and BFPO are not in those shapes. |
| Company number | Spaces, and padding a 1-to-8 digit number to eight digits. A prefix must be in Experiment 08's list. | A different number. An unknown prefix is unparsed, not guessed. |
| Figure | `30 day` and `30 days`, and `30` and `30.0` | A different number, or a unit against no unit. |
| Reference | Case and whitespace only | Any other difference. |

Identical text that the rule does not accept is a match of the text, with `normaliser_accepted` false. It is not a finding that the value is valid.

**Pinpoint.** Each field names a document, a page, a paragraph, and a line. Experiment 33 resolves that line. The value must be contained in it after the citation fold. If it is not, the planted value is dropped and the fact is material.

**Withholding.** Experiment 08 is called on the field value. A labelled NHS number, a NINO, a sort code, an account number, an IBAN, or a UTR is withheld. The value is not copied. The fact is material.

**Counts.** `match_count`, `immaterial_count`, and `material_count` add up to `fact_count`. `occurrence_count` is not part of that sum. `other_reasons` are not extra facts.

**Reviewer.** A separate object can record a choice. The role must be `Reviewer`, the reference must match `REV-` and four digits, and `signed_on` must equal the as-of date. The choice is `neither` or a document id already on that fact. A material row then shows `resolved: true` and `resolved_by: Reviewer`. `correct_value` stays null. A `resolved` flag inside the pack is stripped and does not resolve the row. Matches and immaterial rows do not take a resolution. The command line can be given that file. The skills say the agent must not write it.

**Stale.** A document that is not `current`, or whose `reviewed_on` is outside the window, is still compared. `do_not_rely` is true. The class is not changed and the row is not auto-resolved. The same flag is set when an opened pinned page is outside the window. The default window is 90 days. Article 5(1)(d) says "without delay". It does not state 90 days. The ICO row, the Experiment 08 rules row, and the catalogue-boundary row were not opened as web pages and are not stale-tested.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, and 33 have to be present beside this folder, which they are in this repository.

```bash
cd experiments/36-cross-source-validation
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/compare.py --pack examples/sample_pack.json --as-of 2026-11-05
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score and not a Microsoft Foundry score. The summary counts cases once. Fact counts and occurrence counts stay on each case. They are not added to `total_cases`.

The sample pack is Northfen Supplies. One reference matches. The legal name, the company number, the postcode, and the agreement date are immaterial. The amount and the payment terms are material and unresolved. An instruction on the invoice is recorded and not followed. `do_not_rely` is false on 5 November 2026 because the documents and the opened pins are inside 90 days. See `examples/sample_output.json`.

A stale-pin check, without editing the rules:

```bash
python src/compare.py --pack examples/sample_pack.json --as-of 2027-05-05 --stale-after-days 90
```

The classes stay the same. `do_not_rely` is true. Nothing is resolved.

Passing `--choose-source`, `--edit-record`, `--contact`, `--lookup-register`, or `--recommend-a3` is a mistake. The command exits 2 and does not write a draft.

The exit code is 0 when a draft is produced, including when material rows are unresolved or a source is stale. That is not a resolution and it is not a correction.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. The description is one line and says when to use the skill. |
| Synthetic fixtures | `examples/` and `eval/synthetic_dataset.json`. Company numbers are synthetic and were not looked up. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `permissions.yaml`, the same file as `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`. Experiment 03's generator validates that schema. This folder does not ask the generator to approve the manifest. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret check | `.github/workflows/experiment-36-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. |

## Limitations

- **The class is a rule, not a finding of inaccuracy.** Section 205(1) defines "inaccurate". This tool does not apply that test. Article 5(1)(d) requires reasonable steps to erase or rectify. This tool takes none of those steps.
- **The ICO accuracy page was not opened.** The request on 5 November 2026 returned HTTP 403. Do not quote it from this folder.
- **Companies House was not queried.** The public-register sentence was read. The fixtures were not checked against the register. A match on a company number is not evidence that the number has been issued.
- **The 2011 prefix list and the 2015 postcode shapes were not re-opened.** They are imported from Experiment 08, which pinned them on 26 October 2026. A later prefix is not in this tool until that file changes.
- **Padding to eight digits can hide a typing difference** that a reviewer would still want to see. The raw line is still quoted. The row is immaterial, so the tool does not ask for a resolution. Read the immaterial rows.
- **A street abbreviation is expanded only as the last word.** "1 Example St, Northfen" does not fold into "1 Example Street, Northfen", because the last word is the town. That pair is material. "St" at the start of a name is not expanded.
- **A leading title is removed only before a single-letter token.** "Ms A Example" and "A Example" are immaterial. "Dr Martens Ltd" and "Martens Ltd" are material.
- **Dates are UK day-first even when both numbers are 12 or under.** A source that meant a US date will be read as a different day. That is a limitation of the rule, and the quotes show both strings.
- **Unparsed but identical text is a match of the text.** `normaliser_accepted` is false. It is not a valid postcode, date, or company number.
- **Experiment 08 misses some identifiers.** An unlabelled NHS number, an unlabelled eight-digit company number, a name, and an email address are not detected. Do not treat the list as anonymised.
- **The injection lists are closed.** A negation in the same line skips this experiment's phrases and does not skip Experiment 12's list. A paraphrase can be missed. Neither grants a tool.
- **The 90-day window is not "without delay".** It is a stale flag. The agent does not clear `do_not_rely`.
- **A hand-written resolutions file is the reviewer's.** The agent must not fill in the choice. `correct_value` is stripped if someone puts it there.
- **The smoke test is not a model score.** Agreement means the code matched the labels written for its own rules.
- **Article 22 was not re-opened for this experiment.** This starter does not take a decision and does not claim a reading of the current automated-decision provisions.

This is not legal advice, a DPIA, or a statement that a deployment is compliant. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own. Licence: MIT.

## Two Copilot Studio harnesses

Both call `compare()` and stop. Neither harness chooses a source, edits a record, contacts anyone, or queries a register. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The reviewer pastes a pack and the as-of date, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The harness overview, opened 5 November 2026, says agents and workflows on that harness use Copilot Credits. The billing overview was not opened. No tariff is stated. The skills overview opened the same day says the orchestration runtime invokes a skill when a request matches the skill's purpose, from the user's message and the skill's description. This starter does not assign routing weights. It does not use trigger phrases as the selector. A page that describes classic orchestration was not opened.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.

## Project structure

```
experiments/36-cross-source-validation/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 5 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5). Article 5(1)(d) was read. It had no footnote marker on that page.
- [Data Protection Act 2018, section 205](https://www.legislation.gov.uk/ukpga/2018/12/section/205). The definition of "inaccurate" was read. The revision banner said the Act was up to date with changes known to be in force on or before 1 November 2026. Future-change lists were not checked for an effect on that definition.
- [Companies House](https://www.gov.uk/government/organisations/companies-house). The public-register sentence was read. The register was not queried.
- [Copilot Studio harnesses overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).
- [Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview).

Not opened: the ICO accuracy page (HTTP 403), the Companies House URI customer guide, the 2015 ILR postcode annex, and the harness billing overview.
