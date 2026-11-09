# Experiment 41: Case Summary Agent

Catalogue ID **C002**. Autonomy **A0**. The catalogue checkpoint is "Service representative checks accuracy". Stack in the catalogue: Dynamics 365 and Copilot Studio. What you can run today is Python in the standard library. It does not call a model and it does not call the network. Dynamics 365 is not connected.

A service representative supplies one synthetic case history from a council, utility, housing, or financial-services contact centre, and the fact keys they want read. The agent returns a draft in which every sentence is a copy of named lines, with a pinpoint citation: event id, date, paragraph, and line. A deterministic checker fails any sentence whose cited span does not contain it, or that has no citation. Lines that [Experiment 08](../08-uk-pii-redaction-gateway/) flags are not copied. `case_outcome` stays null. `customer_contacted` and `record_changed` stay false. The agent never contacts the customer and never changes the record.

Samples are synthetic. Mereford Council Contact Centre, Mereford Water, Mereford Housing, and Mereford Mutual are fictional. They are not a council, a water company, a landlord, or an authorised firm. No real person and no real case is in the history.

## How this differs from Experiment 33, Experiment 08, and Experiment 40

**Experiment 33** drafts a reading of a legal bundle for a decision-maker. A citation is a document, a page, a paragraph, and a line. This starter drafts a reading of a contact-centre case for a service representative. A citation is an event, a paragraph, and a line. The support rule is the same: after case and whitespace are folded, the sentence has to be a contiguous part of the cited lines. A paraphrase fails. One sentence has one verdict. Later failures are listed and are not added to the failure count. The day the stale window ends is still current. This folder does not import Experiment 33. It does not recommend a case outcome either.

**Experiment 08** proposes redactions for UK identifiers. This starter calls `propose()` in-process, caller `exp-41-case-summary`. It does not copy `redacted_text`. `output_is_anonymised` stays false. `release()` is not called. A paragraph that contains a flagged line is not quoted.

**Experiment 40** answers a customer. This starter does not. It is read by a service representative before they do their own work in the organisation's system.

## The problem

A service representative opening a long case history needs to see what was recorded, what is missing, and what is too old to treat as current, without the summary becoming a message to the customer or an update to the case. A sentence without a line reference is hard to check. A sentence that cites the wrong line is worse. A sentence that repeats a National Insurance number is more than the representative asked the summary to hold.

This starter is the check. It is extractive. It copies lines. It does not write a fluent brief that a model might invent. The customer contact, if there is one, stays with a person, outside this tool.

## Who it helps

**The service representative.** They see each sentence, the event, the date, the paragraph, and the lines, and they see which sentences the checker rejected. They check accuracy. The draft does not tell them to contact the customer or to change the record.

**A colleague preparing that reading.** They can see gaps for fact keys that had no usable current span, contradictions where two current spans disagree, events left out because they are stale or superseded, and lines withheld because Experiment 08 flagged an identifier. The draft does not pick a side and does not fill a gap.

**A reviewer comparing this pattern with a legal-bundle reading or a customer self-service reply.** The difference is in the section above. This folder is the contact-centre case reading.

## Non-goals

- Contacting the customer by email, SMS, letter, or telephone. `customer_contacted` stays false.
- Changing a case record in Dynamics 365, a housing system, or any other store. `record_changed` stays false.
- Closing, upholding, or rejecting a complaint. `complaint_closed` stays false.
- Offering or paying redress. `redress_offered` stays false.
- Deciding a case outcome. `case_outcome` stays null.
- Marking the summary accurate. On the agent path, `accuracy_checked` stays false.
- Labelling a customer as vulnerable. `customer_labelled_vulnerable` stays false.
- Calculating a DISP clock, an Awaab's Law clock, or any other statutory deadline.
- Deciding eligibility, a tariff, a contract term, or a meter submission.
- Writing a production record or sending anything.
- Reading a PDF, an image, a scan, or a recording. The caller pastes text that is already split into paragraphs and lines.
- Calling Microsoft Foundry or Dynamics 365. Those are deployment notes. They are not called.
- Paraphrasing. A true sentence that is not a contiguous copy of the cited lines fails the checker.
- Resolving a contradiction or filling a gap with words that are not in the case.
- Quoting the ICO's AI accuracy guidance. The page was not opened. See Limitations.
- Autonomy A3. There is no path on which the agent contacts the customer or changes the record.
- Answering the customer. That is Experiment 40.
- Reading a criminal, asylum, or barring bundle. That is Experiment 33.

## What the summariser does

`src/summarise.py` reads one JSON case and writes one JSON document. The same case, the same as-of date, and the same window produce the same JSON. The label is **DRAFT FOR THE SERVICE REPRESENTATIVE. NOT A CUSTOMER CONTACT. NOT A RECORD CHANGE.**

**Sector.** The closed list is `council`, `utility`, `housing`, and `financial_services`. The sector note tells the reader which boundary applies. It does not change the checker and it does not select an outcome. Any other sector is refused. A case that is not marked synthetic is refused. The refusal does not echo the text.

**Extract.** Unless the caller supplies `expected_fact_keys`, the keys are `what_happened`, `customer_ask`, `action_taken`, and `next_step`. `vulnerability_note` is extracted only when the caller names it. Each sentence is the text of one contiguous run of lines in one paragraph, with a citation covering those lines. Order is event date, then event id, then paragraph and line. An event that is superseded, whose date is after the as-of date, or whose date is outside the window is listed in `not_used` and is not quoted. A paragraph that contains an instruction, a prohibited action, or a line Experiment 08 flagged is not copied. A refusal such as "Do not contact the customer." is not treated as that action.

**Checker.** Every shown sentence receives one verdict, in this order:

| Check | Verdict |
|---|---|
| No citation | `citation_missing` |
| Event, paragraph, or line missing | `pinpoint_incomplete` |
| Event id not in the case | `citation_not_in_case` |
| Paragraph or line not in that event | `pinpoint_not_in_event` |
| Contact, record change, closure, redress, outcome, or a vulnerability label | `prohibited_action` |
| An instruction aimed at the summariser | `untrusted_instruction` |
| Cited lines include an identifier, or the sentence itself does | `identifier_withheld` |
| Cited event stale or superseded | `stale_or_superseded` |
| Sentence is not a contiguous part of the cited lines | `span_does_not_support` |
| None of those | `supported` |

The first failure is the verdict. Later failures are `other_failures`. They are not added to `failure_count`. `verdict_total` equals `sentence_count`. Gaps, contradictions, unused events, and withheld lines have their own counts and are not verdicts. A sentence that fails `identifier_withheld` is replaced with a fixed placeholder. The identifier is not copied.

`checker_passed` is true when no shown sentence failed. It can be true while `do_not_rely` is also true, because a gap, a contradiction, a stale event left out of the draft, a detected instruction, a withheld line, a stale pinned page, or an empty reading is a reason not to rely on the draft. `checker_passed` is not a finding that the reading is complete, and it is not a finding that UK GDPR Article 5(1)(d) has been met.

A caller may pass `proposed_sentences` to check a draft that did not come from the extractor. The harness skill that does this still cannot accept the result. The command-line tool does not take proposed sentences. It only extracts.

**Human step, outside `summarise()`.** `record_accuracy_check` accepts only the role "Service representative", and only with a name the caller passes in that call. The name must not be the agent. Every shown sentence must be in the review. A supported sentence is marked `read`. A failed sentence is marked `noted_failure`. `accuracy_checked` can become true only for a complete, supported, current reading with no gap, no contradiction, no withheld line, and no stale pin. The returned flags for contact, record change, closure, redress, and outcome stay false. The skills say the agent must not call this function. The command line does not expose it. `contact_customer`, `write_case_record`, `close_complaint`, `offer_redress`, `decide_outcome`, `send_external`, and `accept_summary` raise `CaseSummaryForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must be present at `experiments/08-uk-pii-redaction-gateway/`. This experiment does not carry a second copy of it.

```bash
cd experiments/41-case-summary
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/summarise.py --case examples/sample_case.json --as-of 2026-11-09
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score, not a Foundry score, and not a customer contact. The summary counts 26 cases once. Each case is `passed`, `failed`, or `error`, and those three add up to 26. Sentence counts stay on each case. On the as-of date 9 November 2026 the agreement with the labelled expectations is 100.0, which means the checker matched its own rules. Those figures are not added together.

The sample case is a fictional housing repair. Four sentences are supported. A stale note, a superseded note, and an instruction note are not used. `checker_passed` is true. `do_not_rely` is true. `case_outcome` is null. `customer_contacted` is false. See `examples/sample_output.json`.

A stale-pin check, without editing the checker:

```bash
python src/summarise.py --case examples/sample_case.json --as-of 2027-03-01
```

That date also marks the sample events stale, so the extract is empty and `do_not_rely` is true. The evaluation set has a separate case with fresh events and stale pins. Passing `--contact-customer`, `--write-record`, `--close-complaint`, `--offer-redress`, `--decide-outcome`, `--send`, or `--accept-summary` is a mistake. The command exits 2 and does not write a file.

The exit code is 0 when a draft is produced, including when the checker fails a sentence or a source is stale. That is not acceptance and it is not a customer contact. The exit code is 2 when the input cannot be read, or when a prohibited flag is passed.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. The description is one line and says when to use the skill. |
| Synthetic fixtures | `examples/`, and `eval/synthetic_dataset.json`. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`. Experiment 03's generator is not called. The schema is the same one that generator validates. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret check | `.github/workflows/experiment-41-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library and Experiment 08. |

## Limitations

- **The checker is extractive.** A true paraphrase fails. A sentence that copies its lines can still mislead by what it leaves out. Residual risk R3 is High. `checker_passed` does not mean the reading is fair, complete, or accurate in the sense of Article 5(1)(d).
- **Only the caller's fact keys are quoted** when a list is supplied. The default list is four keys. A key the caller forgot is invisible. That is a gap in the request, not evidence that the case is silent.
- **Text that is already split into lines.** PDFs, images, scans, and recordings are not read. A line boundary the caller drew is trusted.
- **The starter does not search a case system.** Items that were never pasted are invisible. Dynamics 365 is not queried.
- **Stale and superseded events are left out of the extract.** A later proposal that quotes them exactly still fails. The window, default 90 days, is not a statutory retention period and not a complaint time limit. The day the window ends is still current. The next day is stale. Pinned pages use the same 90-day figure, measured from 9 November 2026, and that window does not follow the caller's case window.
- **The injection list is closed.** A phrase that is not on it is not detected. A refusal sentence is not treated as an instruction when the refusal word comes first and the action is not stated again. An instruction that also states a prohibited action fails the checker if someone proposes it.
- **Contradictions are not resolved.** Two different current sentences with the same fact key are both shown. The draft does not say which note to believe.
- **Experiment 08 does not redact names, email addresses, or telephone numbers.** That is why a flagged line is withheld rather than "cleaned", and why `output_is_anonymised` stays false. An identifier that the gateway does not detect can still be copied if it sits in a line the extractor quotes.
- **Article 22 is not the current safeguard.** On 9 November 2026, UK GDPR Article 22 was shown as omitted, substituted by Articles 22A to 22D. This starter does not claim meaningful human involvement under Article 22A. It only refuses to take the decision. Article 22D regulations were not opened. S.I. 2026/82 was named on the legislation pages and was not opened.
- **The ICO page was not read.** "What do we need to know about accuracy and statistical accuracy?" was requested on 9 November 2026 and returned HTTP 403. No sentence from it is quoted. A search result listed the URL. A search snippet is not the page. Unverified.
- **Article 6 and Article 9 were not opened.** No lawful basis and no special-category condition is asserted. Article 5(3), which was read, says compatibility with the original purpose is not, by itself, lawful.
- **DISP, PRIN 2A, the Ofgem AI blog, and the Awaab's Law guidance were not opened for this experiment.** Sector notes point at Experiments 02, 05, and 40. This folder does not call them and does not calculate their clocks.
- **The smoke test is not a model score.** Agreement 100.0 means the checker matched the expectations written for its own rules.

This is not legal advice, a DPIA, a complaint outcome, or a statement that a deployment is compliant. Summarising a case can omit the line that changes the reading. A person has to read the sources. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## UK GDPR, in short

Article 5(1)(c) is why the summary quotes only the requested fact keys and does not copy a flagged identifier. Article 5(1)(d) is why a stale event is left out of the extract. Leaving a stale event out of a draft is not the erasure or rectification the article describes, and this starter does not do that erasure. Article 5(1)(a) is why the label says the draft was produced for a representative and is not a customer contact. Article 22A(1) is why the draft does not take a significant decision. Article 22C(2) describes safeguards for a controller who does take one. This starter does not decide that those safeguards are met.

## Two Copilot Studio harnesses

Both call `summarise()` and stop. Neither harness contacts the customer, changes the record, closes a complaint, offers redress, records an accuracy check, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The representative pastes a case and the as-of date, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a representative who wants the draft explained in steps. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, opened 9 November 2026, says agents and workflows on that harness use Copilot Credits. The comparison table on that page points the billing cell at a separate overview. That page was not opened. Prices were not copied. The overview did not mark the harness itself as preview. These skills do not list trigger phrases and do not assign routing weights. A separate page on generative orchestration was not opened on 9 November 2026. How a tenant selects a skill is unverified.

The Customer Conversation harness is the one the same overview describes for customer voice and chat. It is not built here. An unattended agent that contacted the customer would sit outside this A0 design.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The identifier gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The citation pattern this experiment reimplements for events rather than document pages: [../33-case-bundle-summariser/](../33-case-bundle-summariser/).

## Project structure

```
experiments/41-case-summary/
├── README.md
├── agent-manifest.yaml
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

## References opened on 9 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5). Paragraphs 1(a), 1(c), 1(d), 2, and 3 were read.
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22). Shown as omitted.
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A). Paragraphs 1 and 2 were read.
- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80). Subsection (1) substitutes Articles 22A to 22D, and that substituted text, including Articles 22B, 22C, and 22D, was read on this page. Separate article pages for 22B, 22C, and 22D were not opened. Subsection (3) substitutes Data Protection Act 2018 sections 50A to 50D. This starter does not apply that regime.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The ICO page [What do we need to know about accuracy and statistical accuracy?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/what-do-we-need-to-know-about-accuracy-and-statistical-accuracy/) was requested the same day and returned HTTP 403. It was not read. S.I. 2026/82 was not opened. Linked harness billing pages were not opened. A Foundry product page was not opened for this experiment.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
