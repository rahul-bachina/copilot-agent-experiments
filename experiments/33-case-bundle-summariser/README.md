# Experiment 33: Evidence and case-bundle summariser

Catalogue ID **UK09**. Autonomy **A0**. The catalogue checkpoint is "Decision-maker reviews every cited sentence". Stack in the catalogue: Microsoft Foundry, Azure, and Copilot Studio. What you can run today is Python in the standard library. It does not call a model and it does not call the network.

A decision-maker supplies one synthetic case bundle and the fact keys they want read. The agent returns a draft in which every sentence is a copy of named lines, with a pinpoint citation: document id, page, paragraph, and line. A deterministic checker fails any sentence whose cited span does not contain it, or that has no citation. `case_outcome`, `disclosure_decision`, and `credibility_finding` stay null. The agent never makes those decisions.

Samples are synthetic. Reedfen Constabulary, Northfen Casework Unit, and Example Barring Desk are fictional. They are not a police force, the Home Office, or the Disclosure and Barring Service. No real person and no real case is in the bundle.

## How this differs from Experiment 18 and Experiment 29

**Experiment 18** builds an index of items in an authorised scope. It records a hash, a date, a proposed page order, and flags for possible privilege or third-party data. It does not write a sentence about what a document says, and it does not attach a page, paragraph, and line to such a sentence. It calls Experiment 12. This experiment does not decide scope, does not build an export index, and does not call Experiment 12 or Experiment 18.

**Experiment 29** scores claims in a question-and-answer bundle against passages an agent was shown. A shared word can be enough for its supported verdict. Its human gate is an evaluation owner on thresholds and a release. This experiment drafts a case-bundle reading. Support means the sentence, after case and whitespace are folded, is a contiguous part of the cited lines. A paraphrase fails. There is no threshold and no release. The human gate is that the decision-maker reviews every cited sentence.

The approaches reused from those experiments are the ones that fit a checker: one verdict per sentence, with later failures listed and not added to the total; a closed injection list that includes HTML comments, form feeds, trailing blank lines, and zero-width characters, with `followed` always false; output-shaped keys stripped so their values are not echoed; a date window in which the last day is still current; and a smoke test that counts cases once. The legal questions are not reused. Neither of those experiments decides a case, and this one does not either.

Experiment 12 still describes UK09 as a later row and does not call this folder. This folder does not call Experiment 12. That page was left as it stood.

## The problem

Someone working through a bundle has to be able to point at the line a sentence came from. The Home Office evaluation of the Asylum Case Summarisation pilot, opened on 4 November 2026, said some users saw little time saved because the summary did not provide source references, and that the pilot deliberately did not point at the place in the transcript. Nine percent of summaries were removed as inaccurate or incomplete. A sentence without a line reference is hard to check. A sentence that cites the wrong line is worse, because it looks checked.

This starter is the check. It is extractive. It copies lines. It does not write a fluent brief that a model might invent. The decision, if there is one, stays with a person.

## Who it helps

**The decision-maker.** They see each sentence, the document, the page, the paragraph, and the lines, and they see which sentences the checker rejected. They review every cited sentence. The draft does not tell them what to decide.

**A colleague preparing that reading.** They can see gaps for fact keys that had no usable current span, and contradictions where two current spans disagree. The draft does not pick a side.

**A reviewer comparing this pattern with an evidence-pack index or a groundedness score.** The difference is in the paragraph above. This folder is the case-bundle reading. It is not the index and it is not the evaluation harness.

## Non-goals

- Recommending an outcome: charge, no further action, grant, refuse, bar, or not bar. `case_outcome` stays null.
- Making a disclosure decision under the Criminal Procedure and Investigations Act 1996, section 3, or under any other rule. `disclosure_decision` stays null. Nothing is disclosed.
- Making a credibility finding about a witness, an applicant, or a referee. `credibility_finding` stays null.
- Accepting the summary as a decision. On the agent path, `summary_accepted_as_reading_aid` stays false.
- Deciding that material might reasonably be considered capable of undermining the prosecution case or of assisting the accused.
- Writing a production record, including a case system, Dataverse, or SharePoint.
- Sending the draft to a party, a prosecutor, a court, or anyone else.
- Reading a PDF, an image, a scan, or an audio file. The caller pastes text that is already split into pages, paragraphs, and lines.
- Calling Microsoft Foundry, Document Intelligence, or Azure AI Search. Those are deployment options described in the Foundry note. They are not called.
- Paraphrasing. A true sentence that is not a contiguous copy of the cited lines fails the checker.
- Resolving a contradiction or filling a gap with words that are not in the bundle.
- Autonomy A3. There is no path on which the agent decides the case.
- Scoring another agent's answers against passages. That is Experiment 29.
- Building an export index. That is Experiment 18.

## What the summariser does

`src/summarise.py` reads one JSON bundle and writes one JSON document. The same bundle, the same as-of date, and the same window produce the same JSON. The label is **DRAFT FOR THE DECISION-MAKER. NOT A DECISION.**

**Matter type.** The closed list is `disclosure_reading`, `asylum_case_reading`, and `barring_referral_reading`. The label tells the reader which boundary applies. It does not change the checker and it does not select an outcome. Any other label is refused. A bundle that is not marked synthetic is refused.

**Extract.** When the caller supplies `expected_fact_keys`, only those keys become sentences. Each sentence is the text of one contiguous paragraph, with a citation covering its lines. Order is document date, then document id, then page, paragraph, and line. A document that is superseded, that names a successor, or whose review date is outside the window is listed in `not_used` and is not quoted. A paragraph that contains an instruction, or wording that would be an outcome, a disclosure decision, or a credibility finding, is not copied. A refusal such as "Do not recommend a charge." is not treated as that wording.

**Checker.** Every shown sentence receives one verdict, in this order:

| Check | Verdict |
|---|---|
| No citation | `citation_missing` |
| Page, paragraph, or line missing | `pinpoint_incomplete` |
| Document id not in the bundle | `citation_not_in_bundle` |
| Page, paragraph, or line not in that document | `pinpoint_not_in_document` |
| Outcome, disclosure decision, or credibility wording | `prohibited_action` |
| An instruction aimed at the summariser | `untrusted_instruction` |
| Cited document stale or superseded | `stale_or_superseded` |
| Sentence is not a contiguous part of the cited lines | `span_does_not_support` |
| None of those | `supported` |

The first failure is the verdict. Later failures are `other_failures`. They are not added to `failure_count`. `verdict_total` equals `sentence_count`. Gaps, contradictions, and unused documents have their own counts and are not verdicts.

`checker_passed` is true when no shown sentence failed. It can be true while `do_not_rely` is also true, because a gap, a contradiction, a stale document left out of the draft, a detected instruction, a stale pinned page, or an empty reading is a reason not to rely on the draft. `checker_passed` is not a finding that the reading is complete.

A caller may pass `proposed_sentences` to check a draft that did not come from the extractor. The harness skill that does this still cannot accept the result. The command-line tool does not take proposed sentences. It only extracts.

**Human step, outside `summarise()`.** `record_sentence_review` accepts only the role "Decision-maker", and only with a name the caller passes in that call. Every shown sentence must be in the review. A supported sentence is marked `read`. A failed sentence is marked `noted_failure`. The returned flags for outcome, disclosure, and credibility stay null. `summary_accepted_as_reading_aid` can become true only for a complete, supported, current reading with no contradiction and no stale pin. An acknowledgement of an instruction or of a stale document does not clear the flag. The skills say the agent must not call this function. The command line does not expose it. `recommend_outcome`, `decide_disclosure`, `find_credibility`, `accept_summary`, `send_external`, and `write_production_record` raise `SummaryForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/33-case-bundle-summariser
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/summarise.py --bundle examples/sample_bundle.json --as-of 2026-11-04
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score, not a Foundry score, and not a case outcome. The summary counts 26 cases once. Sentence counts stay on each case. On the as-of date 4 November 2026 the agreement with the labelled expectations is 100.0, which means the checker matched its own rules. The 26 cases contain 29 sentences in total. Those figures are not added together.

The sample bundle is a fictional disclosure reading. Two sentences are supported. A superseded note, a stale note, and an instruction note are not used. `checker_passed` is true. `do_not_rely` is true. `case_outcome` is null. See `examples/sample_output.json`.

A stale-pin check, without editing the checker:

```bash
python src/summarise.py --bundle examples/sample_bundle.json --as-of 2027-03-01 --stale-after-days 90
```

That date also marks the sample documents stale, so the extract is empty and `do_not_rely` is true. The evaluation set has a separate case with a fresh document and stale pins. Passing `--recommend-outcome`, `--decide-disclosure`, `--find-credible`, `--accept-summary`, `--send`, or `--write-record` is a mistake. The command exits and does not write a file.

The exit code is 0 when a draft is produced, including when the checker fails a sentence or a source is stale. That is not acceptance and it is not a decision.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. The description is one line and says when to use the skill. |
| Synthetic fixtures | `fixtures/library.json`, `examples/`, and `eval/synthetic_dataset.json`. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `agent-manifest.yaml`, the repository manifest format, validated against `schemas/agent-manifest.schema.json`. Experiment 03's generator is not called. The schema is the same one that generator validates. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret check | `.github/workflows/experiment-33-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |

## Limitations

- **The checker is extractive.** A true paraphrase fails. A sentence that copies its lines can still mislead by what it leaves out. Residual risk R3 is High. `checker_passed` does not mean the reading is fair, complete, or safe to rely on.
- **Only the caller's fact keys are quoted** when a list is supplied. A key the caller forgot is invisible. That is a gap in the request, not evidence that the bundle is silent.
- **Text that is already split into lines.** PDFs, images, scans, and audio are not read. A line boundary the caller drew is trusted. A bad split produces a bad citation.
- **The starter does not search a case system.** Items that were never pasted are invisible.
- **Stale and superseded documents are left out of the extract.** A later proposal that quotes them exactly still fails. The window, default 90 days, is not a statutory retention period and not a disclosure time limit. The day the window ends is still current. The next day is stale.
- **The injection list is closed.** A phrase that is not on it is not detected. A refusal sentence is not treated as an instruction. An instruction that also states an outcome is a prohibited sentence if someone proposes it.
- **Contradictions are not resolved.** Two different current sentences with the same fact key are both shown. The draft does not say which witness to believe.
- **Article 22 and section 14 are not the current safeguards.** On 4 November 2026, UK GDPR Article 22 was shown as omitted, substituted by Articles 22A to 22D. Data Protection Act 2018 section 14 was shown as omitted from 5 February 2026. This starter does not claim meaningful human involvement under Article 22A. It only refuses to take the decision. Law-enforcement processing is a different regime: Data Protection Act 2018 sections 50A to 50D, as substituted by the Data (Use and Access) Act 2025, section 80(3). Whether a live criminal bundle is Part 3 processing was not decided here.
- **CPIA section 3 is the prosecutor's duty.** The section was read. The test in section 3(1) is not applied. The Code of Practice under Part II was not opened. Police disclosure duties under that code are unverified here.
- **The Home Office figures are theirs.** Twenty-three minutes, 32 percent, 9 percent removed, and 23 percent not fully confident are from the evaluation published on 29 April 2025, opened on 4 November 2026. They are not a result of this starter. The evaluation says the pilots were small and not representative of every decision-making unit.
- **The PoliceAI announcement is not this pilot.** The 14 July 2026 news page describes a future pilot of summaries of digital material. This folder does not connect to it.
- **The DBS record is not this tool.** The register entry opened on 4 November 2026 lists a Barring Referral AI Summary Tool, published 14 October 2026, phase Public Beta. The record says caseworkers decide and the output cannot be the sole basis for a barring decision. This starter is a separate, local checker on synthetic text.
- **ATRS scope is not decided here.** The scope policy opened on 4 November 2026 says the standard was mandated for government departments on 6 February 2024, for tools in Beta, Pilot, or Production that significantly influence a decision with public effect or that interact with the public. It is recommended more widely. This repository does not publish an ATRS record and does not decide that an adopting body is in scope.
- **A hand-edited JSON is not a control.** `record_sentence_review` trusts the verdicts already on the draft. It does not re-read the bundle. The agent cannot call it.
- **The smoke test is not a model score.** Agreement 100.0 means the checker matched the expectations written for its own rules.

This is not legal advice, a DPIA, a disclosure schedule, or a statement that a deployment is compliant. Summarising a case bundle can omit the line that changes the reading. In a criminal, asylum, or safeguarding context that omission can affect a person's liberty, status, or safety. A person has to read the sources. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `summarise()` and stop. Neither harness recommends an outcome, decides disclosure, finds credibility, records a review, writes a record, or sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The user pastes a bundle and the as-of date, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the draft explained in steps. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, opened 4 November 2026, says agents and workflows on that harness use Copilot Credits. The comparison table on that page points the billing cell at a separate overview. Prices were not copied. The overview did not mark the harness itself as preview. Generative orchestration selects by description. These skills do not use classic-orchestration trigger phrases or routing weights.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/33-case-bundle-summariser/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── fixtures/
├── schema/
└── tests/
```

## References opened on 4 November 2026

- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22). Shown as omitted. Substituted by Chapter 3 Section 4A.
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A). Paragraphs 1 and 2 were read.
- [Data Protection Act 2018, section 14](https://www.legislation.gov.uk/ukpga/2018/12/section/14). Shown as omitted on 5 February 2026 by the Data (Use and Access) Act 2025, Schedule 6, paragraph 11, and S.I. 2026/82. The page said the section is up to date with changes known to be in force on or before 1 November 2026.
- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80). Subsection (1) substitutes Articles 22A to 22D. Subsection (3) substitutes Data Protection Act 2018 sections 50A to 50D.
- [Criminal Procedure and Investigations Act 1996, section 3](https://www.legislation.gov.uk/ukpga/1996/25/section/3). Subsection (1) was read. The Part II code was not opened.
- [ATRS mandatory scope and exemptions policy](https://www.gov.uk/government/publications/algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy/algorithmic-transparency-recording-standard-atrs-mandatory-scope-and-exemptions-policy). Published 17 December 2024. Sections 3, 4.2, and 4.3, and the large-language-model row of Annex 1, were read.
- [Evaluation of AI trials in the asylum decision making process](https://www.gov.uk/government/publications/evaluation-of-ai-trials-in-the-asylum-decision-making-process/evaluation-of-ai-trials-in-the-asylum-decision-making-process). Published 29 April 2025.
- [AI to speed up justice under major disclosure reforms](https://www.gov.uk/government/news/ai-to-speed-up-justice-under-major-disclosure-reforms). Published 14 July 2026.
- [DBS Barring Referral AI Summary Tool](https://www.gov.uk/algorithmic-transparency-records/disclosure-and-barring-service-barring-referral-ai-summary-tool), and the [register index](https://www.gov.uk/algorithmic-transparency-records) listing dated 14 October 2026.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

Articles 22B, 22C, and 22D are in section 80(1), which was read. They were not given separate notes beyond the substitution. A Foundry product page was not opened for this experiment. Billing pages linked from the harness overview were not opened.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
