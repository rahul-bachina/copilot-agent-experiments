# Experiment 37: Underwriting submission summary

Catalogue ID **B006**. Autonomy **A0**. The catalogue checkpoint is "Underwriter owns coverage and pricing decision". Stack in the catalogue: Copilot Studio on the GitHub Copilot harness, and Microsoft Foundry. What you can run today is Python in the standard library. It calls Experiment 12 and the number and date check in Experiment 29, in process. It does not call a model and it does not call the network.

An underwriter supplies one synthetic broker submission and an as-of date. The agent returns a draft with a closed set of fields: insured name, risk description, sums insured, locations, loss history, stated exclusions, stated warranties, and inception or period. Every stated fact is a copy of named lines, with a pinpoint citation: document id, page, paragraph, and line. A field with no usable current paragraph is **not stated**. It is not inferred. `coverage_decision`, `price_suggested`, and `terms_suggested` stay null. The agent does not contact the broker and does not write to an underwriting system.

Samples are synthetic. Northfen Wharf Ltd is fictional. It is not an insurer, a Lloyd's syndicate, an MGA, or a broker. No real person and no real submission is in the file.

## How this differs from Experiment 12, Experiment 33, Experiment 29, and Experiment 35

**Experiment 12** inventories text files. It suggests a class from a closed keyword list and calls Experiment 08 for UK identifiers. It has no underwriting purpose, and this folder does not add one. This experiment calls `intake()` with no purpose, so nothing is routed and nothing is queued. A file that was not read, is outside the date window, or has a deterministic identifier finding is not quoted. Experiment 12's own page was left as it stood.

**Experiment 33** copies a contiguous span and checks a pinpoint for a case bundle. This experiment uses that same rule: after case and whitespace are folded, the fact text has to be a contiguous part of the cited lines. A paraphrase fails. This folder does not import Experiment 33. That package lives under the module name `src`, which would collide with this one. It does not recommend a case outcome, and this experiment does not either.

**Experiment 29** can treat shared words as support. Its human gate is an evaluation owner on thresholds and a release. This experiment calls Experiment 29 only for the number and date boundary check: a number has to appear as its own digit run, and an ISO date has to appear as written. Support itself is the contiguous-span rule. There is no threshold and no release. A pass is not an underwriting decision.

**Experiment 35** is a claims evaluation harness being built separately. It was not on main when this folder was written, and this folder does not import it. `eval/evaluate.py` mirrors the approach: labelled cases, one score per case, field results kept on the case, no model judge, and no release of a pass. If a `35-*` folder is present later, `experiment_35_folders_present` lists the name. `experiment_35_imported` stays false.

## The problem

A commercial or specialty submission is a pile of proposal forms, schedules of values, loss runs, and survey reports. The underwriter still has to find the sum insured, the locations, the loss history, and what the submission actually says about exclusions or warranties. A sentence that is not tied to a line is hard to check. A sentence that fills a gap the submission left open is worse, because it looks like the broker said it.

This starter is the check. It is extractive. It copies lines. It does not write a fluent underwriting brief. Coverage and price stay with the underwriter.

The audience is a commercial or specialty insurer, an MGA, or a broker in the Lloyd's market or in UK general insurance. No Lloyd's byelaw was opened. None is applied. No syndicate is named.

## Who it helps

**The underwriter.** They see each stated fact, the document, the page, the paragraph, and the lines, and they see which fields are not stated. They decide coverage and price. The draft does not tell them to accept or decline.

**A colleague preparing that reading.** They can see a missing-information checklist without the tool contacting the broker. A gap is not an enquiry under Insurance Act 2015 section 3(4)(b). The underwriter decides whether to ask.

**A reviewer comparing this pattern with document intake, a case-bundle summary, or a groundedness score.** The differences are in the section above. This folder is the submission reading. It is not the inventory, not the case-bundle summary, and not the evaluation release.

## Non-goals

- Accepting, declining, or referring a risk. `coverage_decision` stays null.
- Suggesting a price, a premium, a rate, or terms. `price_suggested` and `terms_suggested` stay null.
- Deciding that the insured made a fair presentation under Insurance Act 2015 section 3, or that section 3(4) was or was not met.
- Deciding what the insurer knows, ought to know, or is presumed to know under section 5.
- Applying a remedy under section 8. Schedule 1 was not opened.
- Deciding that a firm met the Consumer Duty or PRIN 2A, or that the firm is in retail market business.
- Contacting the broker, the insured, or a coverholder.
- Writing an underwriting system, a bordereau, Dataverse, or SharePoint. Binding cover.
- Treating the summary as the decision. `summary_accepted_as_decision` stays false. `solely_automated_decision` stays false.
- Inferring a fact that is not a contiguous copy of cited lines. The value is **not stated**.
- Reading a PDF, an image, or a scan. The caller pastes text that is already split into pages, paragraphs, and lines. Experiment 12 will not read a file whose media type is not `text/plain`.
- Calling Microsoft Foundry. That is a deployment option in the Foundry note. It is not called.
- Autonomy A3. There is no path on which the agent decides the risk.
- Releasing the smoke test as a pass or fail for a live model. `release_evaluation` always raises.

## What the summariser does

`src/summarise.py` reads one JSON submission and writes one JSON document. The same submission, the same as-of date, and the same window produce the same JSON. The label is **DRAFT FOR THE UNDERWRITER. NOT A COVERAGE OR PRICING DECISION.**

**Market label.** The caller may set `commercial_non_consumer` or `retail`. Any other string is `unrecognised`. A missing label is `not_stated`. The agent does not decide the label. `market_label_decided_by_agent` stays false. A commercial label shows the Insurance Act 2015 notes and does not apply PRIN 2A. A retail label shows the PRIN 2A note and does not apply Part 2 as if the contract had been decided to be non-consumer. Neither note is a finding.

**Intake.** Every file goes through Experiment 12. No purpose is requested. Files are not confirmed. Nothing is handed off. A file outside the window, not read, or with a deterministic identifier finding is listed in `not_used` and is not quoted. `output_is_anonymised` stays false.

**Extract.** Each stated fact is the text of one contiguous paragraph whose `fact_key` is in the closed list, from a document Experiment 12 read and whose review date is inside the window. A paragraph that contains an instruction, or wording that would accept, decline, price, contact the broker, or bind, is not copied. A refusal such as "Do not accept this risk." is not treated as that wording.

**Checker.** Every shown fact receives one verdict, in this order:

| Check | Verdict |
|---|---|
| No citation | `citation_missing` |
| Page, paragraph, or line missing | `pinpoint_incomplete` |
| Document id not in the submission | `citation_not_in_submission` |
| Page, paragraph, or line not in that document | `pinpoint_not_in_document` |
| Accept, decline, price, contact, or bind wording | `prohibited_action` |
| An instruction aimed at the summariser | `untrusted_instruction` |
| The file had an identifier finding | `withheld_identifier` |
| The file or document is stale, superseded, or was not read | `stale_or_superseded` |
| A number or an ISO date in the fact is not in the cited lines | `number_or_date_mismatch` |
| The fact is not a contiguous part of the cited lines | `span_does_not_support` |
| None of those | `supported` |

The first failure is the verdict. Later failures are `other_failures`. They are not added to `failure_count`. `verdict_total` equals `stated_fact_count`. Gaps, contradictions, and unused documents have their own counts and are not verdicts. A gap uses the words `not stated`, has no citation, and `inferred` is false.

`checker_passed` is true when no shown fact failed. It can be true while `do_not_rely` is also true, because a gap, a contradiction, a stale document, a detected instruction, or a stale pinned page is a reason not to rely on the draft as a complete picture. `checker_passed` is not a finding that the presentation was fair.

A caller may pass `proposed_facts` to check a draft that did not come from the extractor. The command-line tool does not take proposed facts. It only extracts.

**Human step, outside `summarise()`.** `record_underwriter_review` accepts only the role "Underwriter". Every shown fact and every gap must be in the review. It can set `reading_acknowledged`. It cannot set coverage, price, or terms, and it cannot contact the broker. The skills say the agent must not call this function. The command line does not expose it. `accept_risk`, `decline_risk`, `suggest_price`, `suggest_terms`, `contact_broker`, `write_underwriting_system`, `bind_cover`, and `release_evaluation` raise `SummaryForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 12, Experiment 08, and Experiment 29 need to be beside this folder, which they are in this repository.

```bash
cd experiments/37-underwriting-submission-summary
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/summarise.py --submission examples/sample_submission.json --as-of 2026-11-05
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score, not an LLM-as-judge, not a Foundry score, and not a coverage decision. The summary counts 12 cases once. Fact counts stay on each case. On the as-of date 5 November 2026 the agreement with the labelled expectations is 100.0, which means the checker matched its own rules. The two Northfen cases each have 7 stated facts. Those figures are not added together. 14 is not a summary total.

The sample is Northfen Wharf Ltd, which is fictional, labelled `commercial_non_consumer` by the caller. Seven facts are supported. Stated warranties are not stated. An old survey is not used. `checker_passed` is true. `do_not_rely` is true. `coverage_decision` is null. See `examples/sample_output.json`.

A stale-pin check, without editing the checker:

```bash
python src/summarise.py --submission examples/sample_submission.json --as-of 2027-02-10 --stale-after-days 90
```

Passing `--accept`, `--decline`, `--suggest-price`, `--suggest-terms`, `--contact-broker`, `--write-system`, or `--bind` is a mistake. The command exits and does not write a file.

The exit code is 0 when a draft is produced, including when the checker fails a fact or a source is stale. That is not acceptance and it is not a price.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. The description is one line and says when to use the skill. |
| Synthetic fixtures | `examples/`, `eval/synthetic_dataset.json`, and the tests. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `permissions.yaml`, the same file as `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`. Experiment 03's generator is not called. The schema is the same one that generator validates. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret check | `.github/workflows/experiment-37-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library and the sibling experiments. |

## Limitations

- **The checker is extractive.** A true paraphrase fails. A sentence that copies its lines can still mislead by what it leaves out. Residual risk R3 is High. `checker_passed` does not mean the submission is a fair presentation, or that the risk should be written.
- **The field list is closed.** A fact the caller cares about that is not one of the eight fields is invisible, unless it is one of those fields. That is a limit of this starter, not evidence that the submission is silent.
- **Text that is already split into lines.** PDFs, images, and scans are not read. A line boundary the caller drew is trusted. A bad split produces a bad citation.
- **The starter does not search a broker portal.** Items that were never pasted are invisible.
- **Stale files are left out of the extract.** The window, default 90 days, is not a statutory period and not a Lloyd's deadline. The day the window ends is still current. The next day is stale. A Lloyd's byelaw was not opened.
- **The injection list is closed.** A phrase that is not on it is not detected. A refusal sentence is not treated as an instruction.
- **Contradictions are not resolved.** Two different current facts with the same field are both shown. `chosen_value` stays null.
- **Section 3 is the insured's duty, not a score.** The section was read on 5 November 2026. Section 3(4)(b), the notice to make further enquiries, is not applied. The agent does not enquire. Section 5 was read. The agent does not decide what the insurer knows. Section 8 was read. Schedule 1 was not opened, and no remedy is applied.
- **Consumer insurance is outside Part 2.** Section 2(1) and section 1 were read. The Consumer Insurance (Disclosure and Representations) Act 2012 was not opened, so its duty of reasonable care is not quoted.
- **PRIN 2A was read on 5 November 2026.** PRIN 2A.1 says the Consumer Duty applies to a firm's retail market business. PRIN 2A.2 states three cross-cutting obligations and says they exhaust Principle 12. The handbook page did not show a rule number beside each of those three sentences, so the numbers are not repeated. PRIN 3 and FG22/5 were not opened. This starter does not decide that a firm met the Duty.
- **Article 22 is not the current text.** On 5 November 2026, UK GDPR Article 22 was shown as omitted, substituted by Chapter 3 Section 4A from 5 February 2026. Article 22A(1) was read. A decision is based solely on automated processing if there is no meaningful human involvement. This starter does not certify that involvement. It only refuses to take the decision. Article 5 was read, including data minimisation and accuracy.
- **No Lloyd's rule is applied.** The market is named as an audience. A byelaw page was not opened.
- **The caller organisation label is not a cited fact.** If it does not appear inside the cited insured-name line, `caller_label_differs_from_cited_name` is true. The label is not copied into the insured-name field.
- **A hand-edited JSON is not a control.** `record_underwriter_review` trusts the verdicts already on the draft. It does not re-read the submission. The agent cannot call it.
- **The smoke test is not a model score.** Agreement 100.0 means the checker matched the expectations written for its own rules. An FCA publication about an LLM-as-judge for claims summaries was not opened for this experiment. That expectation is unverified here.

This is not legal advice, a DPIA, a coverage opinion, or a statement that a deployment is compliant. Summarising a submission can omit the line that changes the risk. The underwriter has to read the sources. The manifest does not assert an Article 6 basis. The adopting firm confirms its own.

## Two Copilot Studio harnesses

Both call `summarise()` and stop. Neither harness accepts or declines, suggests a price or terms, contacts the broker, writes a system, or binds. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The underwriter pastes a submission and the as-of date, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for an underwriter who wants the draft explained in steps. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, opened 5 November 2026, says agents and workflows on that harness use Copilot Credits. The billing page linked from that overview was not opened. Prices were not copied. The overview did not mark the harness itself as preview. The generative-orchestration guidance opened the same day says the planner can invoke a topic when its described purpose matches the need, and also by trigger phrases, and that tool names carry more weight than descriptions. These skills do not list trigger phrases and do not assign routing weights. Whether that planner is the GitHub Copilot harness selector was not stated on the harness overview. That link is unverified.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.

## Project structure

```
experiments/37-underwriting-submission-summary/
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

- [Insurance Act 2015, section 1](https://www.legislation.gov.uk/ukpga/2015/4/section/1). Non-consumer insurance contract is defined by exclusion of a consumer insurance contract. The 2012 Act was not opened.
- [Insurance Act 2015, section 2](https://www.legislation.gov.uk/ukpga/2015/4/section/2). Section 2(1): this Part applies to non-consumer insurance contracts only.
- [Insurance Act 2015, section 3](https://www.legislation.gov.uk/ukpga/2015/4/section/3). The duty of fair presentation, including section 3(4) and section 3(5).
- [Insurance Act 2015, section 5](https://www.legislation.gov.uk/ukpga/2015/4/section/5). Knowledge of the insurer, for section 3(5)(b) to (d).
- [Insurance Act 2015, section 8](https://www.legislation.gov.uk/ukpga/2015/4/section/8). Remedies for breach. Schedule 1 was not opened.
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5). Principles, including data minimisation and accuracy.
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22). Shown as omitted. Substituted by Chapter 3 Section 4A.
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A). Paragraph 1 was read.
- [FCA Handbook, PRIN 2A.1](https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html). Application and purpose. PRIN 3 was not opened.
- [FCA Handbook, PRIN 2A.2](https://www.handbook.fca.org.uk/handbook/PRIN/2A/2.html). Cross-cutting obligations.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).
- [Generative orchestration guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration).

A Foundry product page was not opened for this experiment. Billing pages linked from the harness overview were not opened. FG22/5 was named on the PRIN 2A.1 page and was not opened.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
